from fastapi import APIRouter, Request, Form
from fastapi.params import Depends
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select
from sqlalchemy.orm import selectinload

from auth_utils import get_current_user
from database import get_session
from models import Aula, Disciplina

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/disciplinas/{disciplina_id}/aulas", name="disciplinas/{disciplina_id}/aulas")
def pagina_aulas(
    disciplina_id: int,
    request: Request,
    sucesso: str | None = None,
    erro: str | None = None,
    usuario = Depends(get_current_user)
):
    with get_session() as session:
        disciplina = session.exec(
            select(Disciplina)
            .where(Disciplina.id == disciplina_id)
            .options(
                selectinload(Disciplina.horarios),
                selectinload(Disciplina.aulas)
            )
        ).one()

        # As aulas já vêm carregadas e anexadas à disciplina
        aulas = sorted(disciplina.aulas, key=lambda a: a.data)

        # IMPORTANTE: NÃO acessar nada lazy depois daqui
        # porque o template vai usar apenas objetos já carregados

        return templates.TemplateResponse(
            "aulas.html",
            {
                "request": request,
                "disciplina": disciplina,
                "aulas": aulas,
                "sucesso": sucesso,
                "erro": erro,
                "usuario": usuario
            }
        )


@router.post("/api/aulas/{aula_id}", name="api/aulas/{aula_id}")
def api_atualizar_aula(
    request: Request,
    aula_id: int,
    conteudo: str = Form(""),
    atividades: str = Form(""),
    presenca: str = Form(""),
    observacoes: str = Form(""),
    sem_aula: bool = Form(False),
    reposicao: bool = Form(False),
    usuario = Depends(get_current_user)
):
    with get_session() as session:
        aula = session.get(Aula, aula_id)
        disciplina_id = aula.disciplina_id

        aula.conteudo = conteudo
        aula.atividades = atividades
        aula.presenca = presenca
        aula.observacoes = observacoes
        aula.sem_aula = sem_aula
        aula.reposicao = reposicao

        session.commit()

    return RedirectResponse(
        url=f"{request.url_for('disciplinas/{disciplina_id}/aulas', disciplina_id=disciplina_id)}?sucesso=Aula+atualizada",
        status_code=303
    )


@router.get("/api/disciplinas/{disciplina_id}/cronograma-json", name="api/disciplinas/{disciplina_id}/cronograma-json")
def api_cronograma_json(disciplina_id: int,
                        usuario = Depends(get_current_user)):
    with get_session() as session:
        aulas = session.exec(
            select(Aula).where(Aula.disciplina_id == disciplina_id)
        ).all()

    return JSONResponse(aulas)