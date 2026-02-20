from fastapi import APIRouter, Request
from fastapi.params import Depends
from fastapi.templating import Jinja2Templates
from sqlmodel import select

from auth_utils import get_current_user
from database import get_session
from models import Aula, Disciplina

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/dashboard", name="dashboard")
def pagina_dashboard(request: Request, semestre: str = "2026.1", usuario = Depends(get_current_user)):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "semestre": semestre, "usuario": usuario}
    )


@router.get("/api/dashboard-resumo", name="api/dashboard-resumo")
def api_dashboard_resumo(semestre: str = "2026.1", usuario = Depends(get_current_user)):
    with get_session() as session:
        aulas = session.exec(
            select(Aula).join(Disciplina).where(Disciplina.semestre == semestre)
        ).all()

    total_previstas = len(aulas)
    canceladas = sum(1 for a in aulas if a.sem_aula)
    reposicoes = sum(1 for a in aulas if a.reposicao)
    efetivas = total_previstas - canceladas + reposicoes

    return {
        "total_previstas": total_previstas,
        "canceladas": canceladas,
        "reposicoes": reposicoes,
        "efetivas": efetivas
    }