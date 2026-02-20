from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select

from auth_utils import get_current_user
from database import get_session
from services import parse_texto_grade, salvar_disciplinas_e_horarios, gerar_aulas_para_disciplina
from models import Disciplina

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/importar-texto")
def importar_texto(request: Request, usuario = Depends(get_current_user)):
    return templates.TemplateResponse("importar_texto.html", {"request": request, "usuario": usuario})


@router.post("/api/importar-texto-preview")
def api_importar_texto_preview(request: Request, texto: str = Form(...), usuario = Depends(get_current_user)):
    disciplinas = parse_texto_grade(texto)

    return templates.TemplateResponse(
        "preview_importacao.html",
        {"request": request, "disciplinas": disciplinas, "texto": texto, "usuario": usuario}
    )


@router.post("/api/importar-texto-confirmar")
def api_importar_texto_confirmar(texto: str = Form(...), usuario = Depends(get_current_user)):
    disciplinas = parse_texto_grade(texto)

    with get_session() as session:
        salvar_disciplinas_e_horarios(disciplinas, session)

        for d in session.exec(select(Disciplina)).all():
            gerar_aulas_para_disciplina(session, d)

    return RedirectResponse("/disciplinas?sucesso=Disciplinas+importadas+com+sucesso", status_code=303)