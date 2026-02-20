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

@app.get("/health", tags=["health"])
def health():
    """
    Endpoint de healthcheck que verifica a conexão com o banco de dados.
    
    Usado pelo Docker para determinar se o container está saudável.
    """
    try:
        # Tenta acessar o banco de dados
        with get_session() as session:
            session.exec("SELECT 1")
        return JSONResponse(
            status_code=200,
            content={"status": "healthy", "message": "Application and database are OK"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "message": f"Database error: {str(e)}"}
        )

# ROTAS PÚBLICAS
app.include_router(auth.router)  # login/logout
app.include_router(disciplinas.router)  # dashboard público está dentro deste router


# ROTAS PRIVADAS
app.include_router(home.router)
app.include_router(aulas.router)
app.include_router(dias_sem_aula.router)
app.include_router(importacao.router)
app.include_router(dashboard.router)