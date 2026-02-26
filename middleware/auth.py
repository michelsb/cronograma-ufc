from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from auth_utils import get_current_user


class AuthRedirectMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, root_path: str):
        super().__init__(app)
        self.root_path = root_path.rstrip("/")

        # Rotas públicas EXATAS
        self.public_exact = {
            f"{self.root_path}/login",
            f"{self.root_path}/logout",
            f"{self.root_path}/api/login",
        }

        # Rotas públicas por PADRÃO (prefixo)
        self.public_prefix = [
            f"{self.root_path}/static",
        ]

        # Rotas públicas com PADRÃO DINÂMICO
        # /disciplinas/{id}/view
        self.public_dynamic = [
            f"{self.root_path}/disciplinas/",
        ]

    def is_public(self, path: str) -> bool:
        # 1. Match exato
        if path in self.public_exact:
            return True

        # 2. Prefixos públicos
        if any(path.startswith(prefix) for prefix in self.public_prefix):
            return True

        # 3. Rota dinâmica: /disciplinas/{id}/view
        for base in self.public_dynamic:
            if path.startswith(base) and path.endswith("/view"):
                return True

        return False

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if self.is_public(path):
            return await call_next(request)

        # Protegido → precisa de usuário
        try:
            request.state.usuario = get_current_user(request)
        except:
            return RedirectResponse(f"{self.root_path}/login")

        return await call_next(request)