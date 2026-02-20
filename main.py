from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from database import init_db, get_session
from startup_user import criar_usuario_inicial
from routes import auth, home, disciplinas, aulas, dias_sem_aula, importacao, dashboard

app = FastAPI()

# Templates e estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def startup():
    init_db()  # Cria as tabelas
    criar_usuario_inicial()  # Cria o usuário admin se não existir

@app.get("/health") 
def health(): 
    return {"status": "ok"}

# ROTAS PÚBLICAS
app.include_router(auth.router)  # login/logout
app.include_router(disciplinas.router)  # dashboard público está dentro deste router


# ROTAS PRIVADAS
app.include_router(home.router)
app.include_router(aulas.router)
app.include_router(dias_sem_aula.router)
app.include_router(importacao.router)
app.include_router(dashboard.router)