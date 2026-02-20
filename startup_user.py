import os
from database import get_session
from models import Usuario
from auth_utils import gerar_hash_senha
from sqlmodel import select

def criar_usuario_inicial():
    nome = os.getenv("ADMIN_NOME")
    email = os.getenv("ADMIN_EMAIL")
    senha = os.getenv("ADMIN_SENHA")
    papel = os.getenv("ADMIN_PAPEL", "admin")

    if not (nome and email and senha):
        print("Variáveis de ambiente de usuário inicial não configuradas. Ignorando criação.")
        return

    with get_session() as session:
        existente = session.exec(select(Usuario).where(Usuario.email == email)).first()

        if existente:
            print(f"Usuário inicial '{email}' já existe. Ignorando criação.")
            return

        novo = Usuario(
            nome=nome,
            email=email,
            senha_hash=gerar_hash_senha(senha),
            papel=papel
        )
        session.add(novo)
        session.commit()

        print(f"Usuário inicial '{email}' criado com sucesso!")

if __name__ == "__main__":
    criar_usuario_inicial()