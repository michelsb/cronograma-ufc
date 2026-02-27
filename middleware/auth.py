from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from auth_utils import get_current_user


class AuthRedirectMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, root_path: str):
        super().__init__(app)
        self.root_path = root_path.rstrip("/")

        # Rotas públicas SEM prefixo (pois o NGINX remove)
        self.public_exact = {
            "/login",
            "/logout",
            "/api/login",
            "/health",  
        }

        self.public_prefix = [
            "/static",
        ]

        # /disciplinas/{id}/view
        self.public_dynamic = [
            "/disciplinas/",
        ]

    def is_public(self, path: str) -> bool:
        if path in self.public_exact:
            return True

        if any(path.startswith(prefix) for prefix in self.public_prefix):
            return True

        for base in self.public_dynamic:
            if path.startswith(base) and path.endswith("/view"):
                return True

        return False

    async def dispatch(self, request: Request, call_next):
        # path SEM prefixo (pois o NGINX remove)
        path = request.url.path

        if self.is_public(path):
            return await call_next(request)

        try:
            request.state.usuario = get_current_user(request)
        except:
            # Redirect COM prefixo (pois o navegador precisa dele)
            return RedirectResponse(f"{self.root_path}/login")

        return await call_next(request)