"""
models.py
---------
Define os modelos de dados persistidos no SQLite.

- Disciplina: dados básicos da disciplina
- Horario: dia/horário semanal da disciplina
- Aula: cada encontro (data) gerado a partir do período + horários
- Feriado: datas sem aula no semestre
"""

from datetime import date

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List


class Disciplina(SQLModel, table=True):
    """
    Representa uma disciplina ofertada no semestre.

    Exemplo:
        codigo: QXD0267
        nome: SEGURANÇA DA INFORMAÇÃO
        professor: MICHEL SALES BONFIM
        turma: 01A
        semestre: 2026.1
        periodo_inicio: 2026-03-02
        periodo_fim: 2026-07-07
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str
    nome: str
    professor: str
    turma: str
    semestre: str
    periodo_inicio: str
    periodo_fim: str
    carga_horaria_semanal: int = Field(default=0)
    
    horarios: List["Horario"] = Relationship(back_populates="disciplina")
    aulas: List["Aula"] = Relationship(back_populates="disciplina")


class Horario(SQLModel, table=True):
    """
    Representa um horário semanal da disciplina.

    Exemplo:
        dia: "segunda"
        inicio: "10:00"
        fim: "12:00"
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    dia: str
    inicio: str
    fim: str
    disciplina_id: int = Field(foreign_key="disciplina.id")

    disciplina: Disciplina = Relationship(back_populates="horarios")


class Aula(SQLModel, table=True):
    """
    Representa uma aula específica (data) da disciplina.

    É gerada automaticamente a partir do período e dos horários semanais.
    Pode ser editada pelo professor via frontend.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    data: str
    dia_semana: str
    conteudo: str = ""
    atividades: str = ""
    presenca: str = ""
    observacoes: str = ""
    sem_aula: bool = False
    reposicao: bool = False

    disciplina_id: int = Field(foreign_key="disciplina.id")
    disciplina: Disciplina = Relationship(back_populates="aulas")


class DiaSemAula(SQLModel, table=True):
    """
    Representa um dia específico sem aula (feriado, recesso, etc).
    
    Exemplo:
        data: 2026-04-21
        motivo: "Tiradentes"
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    data: date
    motivo: str = ""

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    email: str = Field(unique=True, index=True)
    senha_hash: str
    papel: str = "admin"
