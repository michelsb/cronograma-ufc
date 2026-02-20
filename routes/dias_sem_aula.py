from datetime import date

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select

from auth_utils import get_current_user
from database import get_session
from models import DiaSemAula
from services import recalcular_aulas_por_data

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/dias-sem-aula", name="dias-sem-aula")
def listar_dias_sem_aula(request: Request,
                         sucesso: str | None = None,
                         erro: str | None = None,
                         usuario = Depends(get_current_user)):

    with get_session() as session:
        dias = session.exec(select(DiaSemAula).order_by(DiaSemAula.data)).all()

    return templates.TemplateResponse(
        "dias_sem_aula.html",
        {"request": request, "dias": dias, "sucesso": sucesso, "erro": erro, "usuario": usuario}
    )


@router.get("/dias-sem-aula/{dia_id}/editar", name="dias-sem-aula/{dia_id}/editar")
def editar_dia_sem_aula_form(request: Request, dia_id: int, usuario = Depends(get_current_user)):
    with get_session() as session:
        dia = session.get(DiaSemAula, dia_id)

    return templates.TemplateResponse(
        "editar_dia_sem_aula.html",
        {"request": request, "dia": dia, "usuario": usuario}
    )


@router.post("/api/dias-sem-aula", name="api/dias-sem-aula")
def cadastrar_dia_sem_aula(data: str = Form(...), motivo: str = Form(...), usuario = Depends(get_current_user)):
    with get_session() as session:
        data_convertida = date.fromisoformat(data)

        dia = DiaSemAula(data=data_convertida, motivo=motivo)
        session.add(dia)
        session.commit()

        recalcular_aulas_por_data(session, data_convertida)

    return RedirectResponse(
        url="/dias-sem-aula?sucesso=Dia+sem+aula+adicionado",
        status_code=303
    )


@router.post("/api/dias-sem-aula/{dia_id}/editar", name="api/dias-sem-aula/{dia_id}/editar")
def editar_dia_sem_aula(dia_id: int,
                        data: str = Form(...),
                        motivo: str = Form(...), usuario = Depends(get_current_user)):

    with get_session() as session:
        dia = session.get(DiaSemAula, dia_id)

        data_antiga = dia.data
        data_nova = date.fromisoformat(data)

        dia.data = data_nova
        dia.motivo = motivo
        session.commit()

        recalcular_aulas_por_data(session, data_antiga)
        recalcular_aulas_por_data(session, data_nova)

    return RedirectResponse(
        url="/dias-sem-aula?sucesso=Dia+sem+aula+atualizado",
        status_code=303
    )

@router.post("/dias-sem-aula/{dia_id}/remover", name="dias-sem-aula/{dia_id}/remover")
def remover_dia_sem_aula(dia_id: int, usuario = Depends(get_current_user)):
    with get_session() as session:
        dia = session.get(DiaSemAula, dia_id)
        if not dia:
            return RedirectResponse(
                url="/dias-sem-aula?erro=Dia+não+encontrado",
                status_code=303
            )
        data_afetada = dia.data

        session.delete(dia)
        session.commit()

        # Recalcular aulas
        recalcular_aulas_por_data(session, data_afetada)

    return RedirectResponse(
        url="/dias-sem-aula?sucesso=Dia+sem+aula+removido",
        status_code=303
    )