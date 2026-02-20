from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import timedelta

from auth_utils import (
    verificar_senha,
    criar_access_token,
    obter_usuario_por_email,
)
from database import get_session

templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...),
):
    usuario = obter_usuario_por_email(email)
    if not usuario or not verificar_senha(senha, usuario.senha_hash):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "erro": "E-mail ou senha inválidos",
                "email": email,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    access_token = criar_access_token(
        {"sub": usuario.email},
        expires_delta=timedelta(minutes=60),
    )

    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # coloque True em produção com HTTPS
        samesite="lax",
    )
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response