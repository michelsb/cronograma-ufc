from datetime import date
from fastapi import APIRouter, Request, Depends, Form
from sqlmodel import select
from models import Disciplina, AulaReposicao
from auth_utils import get_current_user
from database import get_session
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

dias_pt = {
    "monday": "segunda",
    "tuesday": "terça",
    "wednesday": "quarta",
    "thursday": "quinta",
    "friday": "sexta",
    "saturday": "sábado",
    "sunday": "domingo"
}

# LISTAR
@router.get("/disciplinas/{disciplina_id}/reposicoes", name="reposicoes_list")
def listar_reposicoes(request: Request, disciplina_id: int, usuario=Depends(get_current_user)):
    with get_session() as session:
        disciplina = session.get(Disciplina, disciplina_id)
        reposicoes = session.exec(
            select(AulaReposicao)
            .where(AulaReposicao.disciplina_id == disciplina_id)
            .order_by(AulaReposicao.data)
        ).all()

    return templates.TemplateResponse(
        "reposicoes.html",
        {
            "request": request,
            "disciplina": disciplina,
            "reposicoes": reposicoes,
            "usuario": usuario,
        },
    )


# CRIAR
@router.post("/disciplinas/{disciplina_id}/reposicoes", name="reposicoes_create")
def criar_reposicao(
    request: Request,
    disciplina_id: int,
    data: str = Form(...),
    inicio: str = Form(...),
    fim: str = Form(...),
    conteudo: str = Form(""),
    atividades: str = Form(""),
    observacoes: str = Form(""),
    substitui_aula: str = Form(None),
    usuario=Depends(get_current_user),
):
    with get_session() as session:
        
        data_obj = date.fromisoformat(data)
        dia_semana = dias_pt[data_obj.strftime("%A").lower()]
        nova = AulaReposicao(
            disciplina_id=disciplina_id,
            data=date.fromisoformat(data),
            dia_semana=dia_semana,
            inicio=inicio,
            fim=fim,
            conteudo=conteudo,
            atividades=atividades,
            observacoes=observacoes,
            substitui_aula=bool(substitui_aula),
        )
        session.add(nova)
        session.commit()

    return RedirectResponse(
        request.url_for("reposicoes_list", disciplina_id=disciplina_id),
        status_code=303,
    )


# EDITAR (FORMULÁRIO)
@router.get("/reposicoes/{reposicao_id}/editar", name="reposicoes_edit_form")
def editar_reposicao_form(request: Request, reposicao_id: int, usuario=Depends(get_current_user)):
    with get_session() as session:
        reposicao = session.get(AulaReposicao, reposicao_id)
        disciplina = reposicao.disciplina

    return templates.TemplateResponse(
        "editar_reposicao.html",
        {
            "request": request,
            "reposicao": reposicao,
            "disciplina": disciplina,
            "usuario": usuario,
        },
    )


# EDITAR (POST)
@router.post("/reposicoes/{reposicao_id}/editar", name="reposicoes_edit")
def editar_reposicao(
    request: Request,
    reposicao_id: int,
    data: str = Form(...),
    inicio: str = Form(...),
    fim: str = Form(...),
    conteudo: str = Form(""),
    atividades: str = Form(""),
    observacoes: str = Form(""),
    substitui_aula: str = Form(None),
    usuario=Depends(get_current_user),
):
    with get_session() as session:

        data_obj = date.fromisoformat(data)
        dia_semana = dias_pt[data_obj.strftime("%A").lower()]

        reposicao = session.get(AulaReposicao, reposicao_id)

        reposicao.data = date.fromisoformat(data)
        reposicao.dia_semana = dia_semana
        reposicao.inicio = inicio
        reposicao.fim = fim
        reposicao.conteudo = conteudo
        reposicao.atividades = atividades
        reposicao.observacoes = observacoes
        reposicao.substitui_aula = bool(substitui_aula)

        session.add(reposicao)
        session.commit()

    return RedirectResponse(
        request.url_for("reposicoes_list", disciplina_id=reposicao.disciplina_id),
        status_code=303,
    )


# REMOVER
@router.post("/reposicoes/{reposicao_id}/remover", name="reposicoes_delete")
def remover_reposicao(request: Request, reposicao_id: int, usuario=Depends(get_current_user)):
    with get_session() as session:
        reposicao = session.get(AulaReposicao, reposicao_id)
        disciplina_id = reposicao.disciplina_id
        session.delete(reposicao)
        session.commit()

    return RedirectResponse(
        request.url_for("reposicoes_list", disciplina_id=disciplina_id),
        status_code=303,
    )