from fastapi import APIRouter, Request
from fastapi.params import Depends
from fastapi.templating import Jinja2Templates
from sqlmodel import select

from auth_utils import get_current_user
from database import get_session
from models import Disciplina, Aula, DiaSemAula

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", include_in_schema=False)
def home(request: Request,
         usuario = Depends(get_current_user)):
    with get_session() as session:

        ultimo_semestre = session.exec(
            select(Disciplina.semestre).order_by(Disciplina.semestre.desc())
        ).first()

        if not ultimo_semestre:
            return templates.TemplateResponse("home.html", {
                "request": request,
                "total_disciplinas": 0,
                "total_aulas": 0,
                "total_dias_sem_aula": 0,
                "aulas_dadas_geral": 0,
                "aulas_restantes_geral": 0,
                "semestre": "Nenhum semestre cadastrado"
            })

        disciplinas = session.exec(
            select(Disciplina).where(Disciplina.semestre == ultimo_semestre)
        ).all()

        ids = [d.id for d in disciplinas]

        total_disciplinas = len(disciplinas)

        total_aulas = len(
            session.exec(
                select(Aula).where(Aula.disciplina_id.in_(ids))
            ).all()
        )

        total_dias_sem_aula = len(session.exec(select(DiaSemAula)).all())

        aulas_dadas_geral = len(
            session.exec(
                select(Aula).where(
                    Aula.disciplina_id.in_(ids),
                    Aula.atividades != ""
                )
            ).all()
        )

        aulas_restantes_geral = total_aulas - aulas_dadas_geral - total_dias_sem_aula

    return templates.TemplateResponse("home.html", {
        "request": request,
        "total_disciplinas": total_disciplinas,
        "total_aulas": total_aulas,
        "total_dias_sem_aula": total_dias_sem_aula,
        "aulas_dadas_geral": aulas_dadas_geral,
        "aulas_restantes_geral": aulas_restantes_geral,
        "semestre": ultimo_semestre,
        "usuario": usuario
    })