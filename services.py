"""
services.py
-----------
Serviços de domínio da aplicação:

- parse_texto_grade:
    Lê o texto extraído do PDF do SIGAA e extrai disciplinas + horários.

- salvar_disciplinas_e_horarios:
    Persiste disciplinas e horários no banco (não gera aulas aqui).

- gerar_aulas_para_disciplina:
    Gera (ou atualiza) as aulas (datas) a partir do período e horários,
    respeitando dias sem aula e preservando aulas com conteúdo manual.

- recalcular_aulas_por_data:
    Recalcula aulas das disciplinas afetadas por um dia sem aula,
    sem apagar aulas manualmente preenchidas.
"""

from typing import List, Dict
from sqlmodel import Session, select

from models import Disciplina, Horario, Aula, DiaSemAula

import re
from datetime import date, datetime, timedelta


# ---------------------------------------------------------
# Utilidades
# ---------------------------------------------------------

def parse_date(value: str) -> date:
    return date.fromisoformat(value)

def extrair_carga_horaria(linha: str) -> int:
    """
    Extrai a carga horária semanal de uma linha do tipo:
        "4 / 64"
    Retorna apenas o primeiro número (ex.: 4).
    """
    m = re.match(r"(\d+)\s*/\s*\d+", linha)
    return int(m.group(1)) if m else 0


# ---------------------------------------------------------
# PARSE DO TEXTO DO PDF
# ---------------------------------------------------------

def parse_texto_grade(texto: str) -> List[Dict]:
    """
    Recebe o texto extraído do PDF e retorna uma lista de dicionários
    representando disciplinas e seus horários.

    Estrutura de retorno:
    [
        {
            "codigo": "QXD0267",
            "nome": "SEGURANÇA DA INFORMAÇÃO",
            "professor": "MICHEL SALES BONFIM",
            "turma": "T01A",
            "semestre": "2026.1",
            "periodo_inicio": "2026-03-02",
            "periodo_fim": "2026-07-07",
            "carga_horaria_semanal": 4,
            "horarios": [
                {"dia": "segunda", "inicio": "10:00", "fim": "12:00"},
                {"dia": "quarta", "inicio": "10:00", "fim": "12:00"},
            ]
        },
        ...
    ]
    """

    # Remove linhas vazias e espaços extras
    linhas = [l.strip() for l in texto.splitlines() if l.strip()]
    disciplinas = []
    i = 0

    while i < len(linhas):
        linha = linhas[i]

        # Detecta início de disciplina:
        # Ex.: "QXD0267 - SEGURANÇA DA INFORMAÇÃO - T01A"
        m_inicio = re.match(r"(QXD\d{4}) - (.+?) - T\d+", linha)
        if m_inicio:
            codigo = m_inicio.group(1)
            nome = m_inicio.group(2).strip()

            # Linha 2: semestre + turma
            # Ex.: "2026.1 T01A"
            linha2 = linhas[i + 1]
            m_sem = re.match(r"(\d{4}\.\d)\s+(T\d+A)", linha2)
            semestre = m_sem.group(1)
            turma = m_sem.group(2)

            # Linha 3: carga horária semanal
            # Ex.: "4 / 64"
            linha_ch = linhas[i + 2]
            carga_horaria_semanal = extrair_carga_horaria(linha_ch)

            # A partir da linha 4, vêm os horários semanais,
            # até encontrar uma linha que começa com "(" (período).
            horarios = []
            j = i + 3

            while j < len(linhas) and not linhas[j].startswith("("):
                # Ex.: "SEG 10:00-12:00"
                m_h = re.match(r"(SEG|TER|QUA|QUI|SEX|SAB)\s+(\d{2}:\d{2})-(\d{2}:\d{2})", linhas[j])
                if m_h:
                    dia_sigla = m_h.group(1)
                    inicio_h = m_h.group(2)
                    fim_h = m_h.group(3)

                    dia_mapa = {
                        "SEG": "segunda",
                        "TER": "terca",
                        "QUA": "quarta",
                        "QUI": "quinta",
                        "SEX": "sexta",
                        "SAB": "sabado"
                    }

                    horarios.append({
                        "dia": dia_mapa[dia_sigla],
                        "inicio": inicio_h,
                        "fim": fim_h
                    })
                j += 1

            # Linha do período:
            # Ex.: "(02/03/2026 - 07/07/2026)"
            linha_periodo = linhas[j]
            m_p = re.match(r"\((\d{2}/\d{2}/\d{4}) - (\d{2}/\d{2}/\d{4})\)", linha_periodo)

            #inicio = datetime.strptime(m_p.group(1), "%d/%m/%Y").strftime("%Y-%m-%d")
            #fim = datetime.strptime(m_p.group(2), "%d/%m/%Y").strftime("%Y-%m-%d")

            inicio = datetime.strptime(m_p.group(1), "%d/%m/%Y").date()
            fim = datetime.strptime(m_p.group(2), "%d/%m/%Y").date()

            disciplinas.append({
                "codigo": codigo,
                "nome": nome,
                "professor": "MICHEL SALES BONFIM",
                "turma": turma,
                "semestre": semestre,
                "periodo_inicio": inicio,
                "periodo_fim": fim,
                "carga_horaria_semanal": carga_horaria_semanal,
                "horarios": horarios
            })

            # Avança o índice para depois do bloco da disciplina atual
            i = j + 2
        else:
            i += 1

    return disciplinas


# ---------------------------------------------------------
# Persistência das disciplinas e horários
# ---------------------------------------------------------

def salvar_disciplinas_e_horarios(disciplinas_extraidas: List[Dict], session: Session) -> None:
    """
    Recebe a lista de disciplinas extraídas do texto do PDF e salva:

    - Disciplina
    - Horario (para cada dia/intervalo)

    Não gera as aulas aqui; isso é feito em outra função.
    """
    for d in disciplinas_extraidas:
        disc = Disciplina(
            codigo=d["codigo"],
            nome=d["nome"],
            professor=d["professor"],
            turma=d["turma"],
            carga_horaria_semanal=d["carga_horaria_semanal"],
            semestre=d["semestre"],
            periodo_inicio=d["periodo_inicio"],
            periodo_fim=d["periodo_fim"],
        )
        session.add(disc)
        session.flush()  # garante disc.id para usar como FK nos horários

        for h in d["horarios"]:
            hor = Horario(
                dia=h["dia"],
                inicio=h["inicio"],
                fim=h["fim"],
                disciplina_id=disc.id
            )
            session.add(hor)

    session.commit()


# ---------------------------------------------------------
# Geração de aulas (cronograma)
# ---------------------------------------------------------

def gerar_aulas_para_disciplina(session: Session, disciplina: Disciplina) -> None:
    """
    Gera (ou atualiza) as aulas de uma disciplina com base:

    - no período (periodo_inicio, periodo_fim)
    - nos horários semanais cadastrados
    - nos dias sem aula (feriados/recessos)

    Regras importantes:
    - NÃO apaga aulas com conteúdo manual (conteúdo, atividades, presenças, observações relevantes).
    - Atualiza aulas automáticas (datas, flags de sem_aula).
    - Cria novas aulas quando necessário.
    - Remove apenas aulas vazias que não deveriam mais existir.
    """

    print(f"\n>>> Regerando aulas para {disciplina.codigo} - {disciplina.nome}")

    # 1. Buscar horários da disciplina
    horarios = session.exec(
        select(Horario).where(Horario.disciplina_id == disciplina.id)
    ).all()

    if not horarios:
        print("Nenhum horário encontrado, pulando disciplina.")
        return

    # 2. Buscar dias sem aula (feriados/recessos)
    #    Mapeia data -> motivo
    dias_sem_aula = {
        d.data: d.motivo
        for d in session.exec(select(DiaSemAula)).all()
    }

    # 3. Buscar aulas existentes da disciplina
    aulas_existentes = session.exec(
        select(Aula).where(Aula.disciplina_id == disciplina.id)
    ).all()

    # Função auxiliar:
    # Aula é considerada "preenchida" se tiver QUALQUER dado manual.
    def aula_preenchida(a: Aula) -> bool:
        if a.conteudo.strip():
            return True
        if a.atividades.strip():
            return True
        if a.presenca.strip():
            return True
        if a.observacoes.strip() and not a.observacoes.startswith("SEM AULA"):
            return True
        return False

    # Mapeia aulas existentes por (data, dia_semana)
    # Isso permite localizar rapidamente se já existe uma aula para aquele dia.
    aulas_map = {
        (a.data, a.dia_semana): a
        for a in aulas_existentes
    }

    # 4. Converter período da disciplina (strings) para date
    inicio = disciplina.periodo_inicio
    fim = disciplina.periodo_fim

    # Mapa de nome do dia -> weekday() do Python
    dia_map = {
        "segunda": 0,
        "terca": 1,
        "quarta": 2,
        "quinta": 3,
        "sexta": 4,
        "sabado": 5
    }

    # 5. Gerar todas as aulas previstas (datas) com base nos horários
    #    Cada horário gera uma sequência de datas semanais dentro do período.
    aulas_previstas = []

    for h in horarios:
        dia_semana = dia_map[h.dia]  # ex.: "segunda" -> 0

        # Encontrar a primeira data dentro do período que cai nesse dia da semana
        data_atual = inicio
        while data_atual.weekday() != dia_semana:
            data_atual += timedelta(days=1)

        # A partir daí, avançar de 7 em 7 dias até o fim do período
        while data_atual <= fim:
            aulas_previstas.append((data_atual, h.inicio, h.fim, h.dia))
            data_atual += timedelta(days=7)

    # 6. Criar ou atualizar aulas com base nas aulas previstas
    usadas = set()  # guarda chaves (data, dia_semana) que foram usadas

    for data_aula, inicio_h, fim_h, dia_semana in aulas_previstas:

        motivo = dias_sem_aula.get(data_aula)
        sem_aula = motivo is not None
        observacoes = f"SEM AULA – {motivo}" if motivo else ""

        chave = (str(data_aula), dia_semana)

        if chave in aulas_map:
            # Aula já existe: atualizar apenas o que é automático
            aula = aulas_map[chave]
            usadas.add(chave)

            # Atualiza a data (caso o período tenha mudado)
            #aula.data = str(data_aula)
            aula.data = str(data_aula)

            # Atualiza flags de sem aula
            if sem_aula:
                aula.sem_aula = True
                aula.observacoes = observacoes
            else:
                # Se antes era "SEM AULA" automático, limpar
                if aula.observacoes.startswith("SEM AULA"):
                    aula.sem_aula = False
                    aula.observacoes = ""

            continue

        # Se não existe aula para essa data/horário, criar uma nova
        nova = Aula(
            disciplina_id=disciplina.id,
            data=data_aula,
            dia_semana=dia_semana,
            conteudo="",
            atividades="",
            presenca="",
            observacoes=observacoes,
            sem_aula=sem_aula,
            reposicao=False
        )
        session.add(nova)

    # 7. Remover aulas que não deveriam existir mais
    #    Somente se estiverem vazias (sem conteúdo manual).
    for chave, aula in aulas_map.items():
        if chave not in usadas:
            if not aula_preenchida(aula):
                session.delete(aula)

    session.commit()
    print(f"✔ Aulas geradas para {disciplina.codigo}")


# ---------------------------------------------------------
# Recalcular aulas quando um feriado muda
# ---------------------------------------------------------

def recalcular_aulas_por_data(session: Session, data_afetada: date) -> None:
    """
    Recalcula as aulas de todas as disciplinas cujo período inclui o dia afetado.

    IMPORTANTE:
    - NÃO apaga todas as aulas da disciplina.
    - Apenas chama gerar_aulas_para_disciplina(), que já é incremental
      e preserva aulas com conteúdo manual.
    """

    # 1. Encontrar disciplinas cujo período inclui a data afetada
    disciplinas = session.exec(
        select(Disciplina).where(
            Disciplina.periodo_inicio <= data_afetada,
            Disciplina.periodo_fim >= data_afetada
        )
    ).all()

    # 2. Para cada disciplina afetada, regerar aulas de forma incremental
    for d in disciplinas:
        gerar_aulas_para_disciplina(session, d)

    session.commit()