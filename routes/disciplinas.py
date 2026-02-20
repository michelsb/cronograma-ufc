from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select, delete

from auth_utils import get_current_user
from database import get_session
from models import Disciplina, Aula, Horario
from sqlalchemy.orm import selectinload

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/disciplinas", name="disciplinas")
def listar_disciplinas(request: Request,
                       semestre: str | None = None,
                       sucesso: str | None = None,
                       erro: str | None = None,
                       usuario = Depends(get_current_user)):
    """Lista as disciplinas, permitindo filtrar por semestre.
    Se semestre não for fornecido, tenta usar o último disponível."""
    with get_session() as session:
        semestres = session.exec(select(Disciplina.semestre).distinct()).all()
        semestres = sorted(semestres)

        if semestre not in semestres:
            semestre = semestres[-1] if semestres else None

        disciplinas = session.exec(
            select(Disciplina)
            .where(Disciplina.semestre == semestre)
            .options(selectinload(Disciplina.horarios))
        ).all()

    return templates.TemplateResponse(
        "disciplinas.html",
        {
            "request": request,
            "disciplinas": disciplinas,
            "semestres": semestres,
            "semestre_atual": semestre,
            "sucesso": sucesso,
            "erro": erro,
            "usuario": usuario
        }
    )

@router.get("/disciplinas/{disciplina_id}/editar", name="disciplinas/{disciplina_id}/editar")
def editar_disciplina_form(request: Request, 
                           disciplina_id: int,
                           usuario = Depends(get_current_user)):
    with get_session() as session:
        disciplina = session.get(Disciplina, disciplina_id)

    return templates.TemplateResponse(
        "editar_disciplina.html",
        {"request": request, "disciplina": disciplina, "usuario": usuario}
    )


@router.post("/api/disciplinas/{disciplina_id}/editar", name="api/disciplinas/{disciplina_id}/editar")
def editar_disciplina(request: Request, 
                      disciplina_id: int,
                      nome: str = Form(...),
                      professor: str = Form(...),
                      turma: str = Form(...),
                      usuario = Depends(get_current_user)):

    with get_session() as session:
        disciplina = session.get(Disciplina, disciplina_id)
        disciplina.nome = nome
        disciplina.professor = professor
        disciplina.turma = turma
        session.commit()

    return RedirectResponse(
        url=f"{request.url_for('disciplinas')}?sucesso=Disciplina+atualizada+com+sucesso",
        status_code=303
    )


@router.post("/disciplinas/{disciplina_id}/remover", name="disciplinas/{disciplina_id}/remover")
def remover_disciplina(request: Request, disciplina_id: int,
                       usuario = Depends(get_current_user)):
    with get_session() as session:
        disciplina = session.get(Disciplina, disciplina_id)

        if not disciplina:
            return RedirectResponse(
                url=request.url_for("disciplinas") + "?erro=Disciplina+não+encontrada",
                status_code=303
            )

        session.exec(delete(Aula).where(Aula.disciplina_id == disciplina_id))
        session.exec(delete(Horario).where(Horario.disciplina_id == disciplina_id))
        session.delete(disciplina)
        session.commit()

    return RedirectResponse(
        url=f"{request.url_for('disciplinas')}?sucesso=Disciplina+removida+com+sucesso",
        status_code=303
    )

@router.get("/disciplinas/{disciplina_id}/dashboard", name="disciplinas/{disciplina_id}/dashboard")
def dashboard_disciplina(request: Request, disciplina_id: int, usuario = Depends(get_current_user)):
    with get_session() as session:
        disciplina = session.get(Disciplina, disciplina_id)

        aulas = session.exec(
            select(Aula).where(Aula.disciplina_id == disciplina_id).order_by(Aula.data)
        ).all()

        # separar dias sem aula
        dias_sem_aula = [a for a in aulas if a.sem_aula]
        aulas_normais = [a for a in aulas if not a.sem_aula]

        # cálculo de créditos
        creditos = disciplina.carga_horaria_semanal  # você precisa ter esse campo
        aulas_previstas = (creditos * 16) // 2

        # aulas disponíveis no semestre
        aulas_disponiveis = len(aulas) - len(dias_sem_aula)

        # aulas dadas
        aulas_dadas = len([a for a in aulas_normais if a.atividades.strip() != ""])

        # faltas
        faltas = len([a for a in aulas_normais if a.presenca == "F"])

    return templates.TemplateResponse(
        "dashboard_disciplina.html",
        {
            "request": request,
            "disciplina": disciplina,
            "aulas": aulas,
            "aulas_normais": aulas_normais,
            "dias_sem_aula_qtd": len(dias_sem_aula),
            "aulas_previstas": aulas_previstas,
            "aulas_disponiveis": aulas_disponiveis,
            "aulas_dadas": aulas_dadas,
            "faltas": faltas,
            "usuario": usuario
        }
    )

@router.get("/disciplinas/{disciplina_id}/view", name="disciplinas/{disciplina_id}/view")
def dashboard_disciplina(request: Request, disciplina_id: int):
    with get_session() as session:
        disciplina = session.get(Disciplina, disciplina_id)

        aulas = session.exec(
            select(Aula).where(Aula.disciplina_id == disciplina_id).order_by(Aula.data)
        ).all()

        # separar dias sem aula
        dias_sem_aula = [a for a in aulas if a.sem_aula]
        aulas_normais = [a for a in aulas if not a.sem_aula]

        # cálculo de créditos
        creditos = disciplina.carga_horaria_semanal  # você precisa ter esse campo
        aulas_previstas = (creditos * 16) // 2

        # aulas disponíveis no semestre
        aulas_disponiveis = len(aulas) - len(dias_sem_aula)

        # aulas dadas
        aulas_dadas = len([a for a in aulas_normais if a.atividades.strip() != ""])

        # faltas
        faltas = len([a for a in aulas_normais if a.presenca == "F"])

    return templates.TemplateResponse(
        "dashboard_disciplina.html",
        {
            "request": request,
            "disciplina": disciplina,
            "aulas": aulas,
            "aulas_normais": aulas_normais,
            "dias_sem_aula_qtd": len(dias_sem_aula),
            "aulas_previstas": aulas_previstas,
            "aulas_disponiveis": aulas_disponiveis,
            "aulas_dadas": aulas_dadas,
            "faltas": faltas,
        }
    )