"""
database.py
-----------
Responsável pela configuração do banco SQLite e criação das tabelas.

Usa SQLModel (em cima de SQLAlchemy) para mapear os modelos.
"""

import os

from sqlmodel import SQLModel, create_engine, Session

# URL do banco de dados
# PostgreSQL: postgresql://usuario:senha@localhost:5432/cronograma
# SQLite: sqlite:///./database/cronograma.db
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://michel:senha123@localhost:5432/cronograma_dev")

# Engine de conexão
engine = create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    """
    Cria as tabelas no banco, caso ainda não existam.

    É chamada na inicialização da aplicação (startup do FastAPI).
    """
    from models import Disciplina, Horario, Aula, DiaSemAula, Usuario# noqa: F401
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """
    Retorna uma sessão de banco de dados.

    Use com 'with get_session() as session:' para garantir fechamento.
    """
    return Session(engine)