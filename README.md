# Cronograma App 📅

Sistema de gerenciamento de cronograma acadêmico desenvolvido com **FastAPI** e **PostgreSQL**.

## 📋 Descrição

Aplicação web para gerenciar e organizar horários de aulas, disciplinas, dias sem acula e importação de dados acadêmicos. Oferece autenticação de usuários, dashboard com visualizações e relatórios acadêmicos.

## 🛠️ Tecnologias

| Tecnologia | Versão | Propósito |
|-----------|--------|----------|
| **Python** | 3.12 | Linguagem principal |
| **FastAPI** | 0.104+ | Framework web |
| **SQLModel** | 0.0.14 | ORM e validação |
| **PostgreSQL** | 17.5 | Banco de dados |
| **Jinja2** | Templates | Renderização HTML |
| **Docker** | Latest | Containerização |

## 📁 Estrutura do Projeto

```
cronograma_app/
├── main.py                 # Aplicação principal FastAPI
├── database.py             # Configuração banco de dados
├── models.py               # Modelos SQLModel
├── auth_utils.py           # Utilitários autenticação
├── services.py             # Lógica de negócio
├── startup_user.py         # Setup usuário inicial
│
├── routes/                 # Rotas da aplicação
│   ├── auth.py            # Login/logout
│   ├── home.py            # Página inicial
│   ├── dashboard.py       # Dashboard acadêmico
│   ├── disciplinas.py     # Gerenciar disciplinas
│   ├── aulas.py           # Gerenciar aulas
│   ├── dias_sem_aula.py   # Gerenciar dias sem aula
│   └── importacao.py      # Importar dados
│
├── templates/             # HTML Jinja2
│   ├── base.html          # Layout base
│   ├── login.html         # Página login
│   ├── home.html          # Home autenticada
│   └── ...
│
├── static/                # CSS, JS
│   └── style.css
│
├── requirements.txt       # Dependências Python
├── Dockerfile             # Containerização
├── docker-compose.yml     # Orquestração containers
├── .env.example          # Template de variáveis
├── .gitignore            # Git ignore
└── README.md             # Este arquivo
```

## 🚀 Início Rápido

### Opção 1: Desenvolvimento Local

#### Pré-requisitos
- Python 3.12+
- PostgreSQL 17+
- pip / venv

#### Instalação

1. **Clonar repositório:**
```bash
git clone seu-repo
cd cronograma_app
```

2. **Criar ambiente virtual:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

4. **Configurar variáveis:**
```bash
cp .env.example .env
# Editar .env com seus valores:
# - POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
# - DATABASE_URL apontando para localhost
# - ADMIN_NOME, ADMIN_EMAIL, ADMIN_SENHA
# - SECRET_KEY
```

5. **Criar banco (PostgreSQL deve estar rodando):**
```bash
# Tabelas são criadas automaticamente ao iniciar
# Usuário admin é criado automaticamente também
```

6. **Rodar aplicação:**
```bash
uvicorn main:app --reload
```

Acesse: http://localhost:8000

### Opção 2: Docker (Recomendado)

#### Pré-requisitos
- Docker
- Docker Compose

#### Instalação

1. **Clonar repositório:**
```bash
git clone seu-repo
cd cronograma_app
```

2. **Configurar variáveis:**
```bash
cp .env.example .env
# Editar .env com valores para Docker:
# DATABASE_URL=postgresql://usuario:senha@postgres:5432/cronograma_dev
```

3. **iniciar containers:**
```bash
docker-compose up
```

Acesse: http://localhost:8000

**Parar containers:**
```bash
docker-compose down
```

**Remover volume de banco (limpar dados):**
```bash
docker-compose down -v
```

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` baseado em `.env.example`:

```env
# PostgreSQL
POSTGRES_DB=cronograma_dev
POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha
POSTGRES_PORT=5432

# Admin inicial
ADMIN_NOME=Seu Nome
ADMIN_EMAIL=seu@email.com
ADMIN_SENHA=senha_segura
ADMIN_PAPEL=admin

# Segurança
SECRET_KEY=chave-secreta-muito-grande-aqui

# Database URL
# Local: postgresql://usuario:senha@localhost:5432/cronograma_dev
# Docker: postgresql://usuario:senha@postgres:5432/cronograma_dev
DATABASE_URL=postgresql://usuario:senha@localhost:5432/cronograma_dev
```

### Criação do Usuário Admin

O usuário admin é criado **automaticamente** ao iniciar a aplicação se:
- As variáveis `ADMIN_NOME`, `ADMIN_EMAIL`, `ADMIN_SENHA` estão definidas
- O usuário ainda não existe no banco

## 📡 API & Endpoints

### **Autenticação**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Redireciona para login |
| GET | `/login` | Página de login |
| POST | `/login` | Fazer login |
| GET | `/logout` | Fazer logout |

### **Health Check**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Verifica saúde da app e DB |

### **Dashboard**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/home` | Home (autenticado) |
| GET | `/dashboard` | Dashboard acadêmico |

### **Disciplinas**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/disciplinas` | Listar disciplinas |
| POST | `/disciplinas` | Criar disciplina |
| GET | `/disciplinas/{id}/edit` | Editar disciplina |
| DELETE | `/disciplinas/{id}` | Deletar disciplina |

### **Aulas**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/aulas` | Listar aulas |
| POST | `/aulas` | Criar aula |

### **Dias sem Aula**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/dias-sem-aula` | Listar dias |
| POST | `/dias-sem-aula` | Criar dia |
| GET | `/dias-sem-aula/{id}/edit` | Editar dia |
| DELETE | `/dias-sem-aula/{id}` | Deletar dia |

### **Importação**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/importacao` | Página upload |
| POST | `/importacao` | Upload arquivo |

## 🔐 Autenticação

A aplicação usa:
- **Hash de senha:** algoritmo seguro (implementado em `auth_utils.py`)
- **Sessões:** baseadas em cookies
- **Proteção CSRF:** integrada no FastAPI

**Login padrão** (criado automaticamente):
```
Email:    admin@ufc.br (ou do .env)
Senha:    senha123 (ou do .env)
```

## 📊 Modelos de Dados

### Usuario
```python
- id: int (PK)
- nome: str
- email: str (UNIQUE)
- senha_hash: str
- papel: str (admin, professor, etc)
- created_at: datetime
```

### Disciplina
```python
- id: int (PK)
- nome: str
- codigo: str
- descricao: str
- usuario_id: int (FK)
```

### Aula
```python
- id: int (PK)
- disciplina_id: int (FK)
- data: date
- horario_inicio: time
- horario_fim: time
- sala: str
```

### DiaSemAula
```python
- id: int (PK)
- data: date
- motivo: str
- usuario_id: int (FK)
```

## 🏥 Health Check

Endpoint para monitoramento:

```bash
curl http://localhost:8000/health
```

**Resposta (200 OK):**
```json
{
  "status": "healthy",
  "message": "Application and database are OK"
}
```

**Resposta (503 Erro):**
```json
{
  "status": "unhealthy",
  "message": "Database error: ..."
}
```

## 🧪 Testes

```bash
# Verificar sintaxe Python
python -m py_compile *.py routes/*.py

# Lint (se flake8 instalado)
flake8 . --exclude=venv

# Type checking (se mypy instalado)
mypy main.py models.py
```

## 📦 Dependências Principais

```
fastapi==0.104.1         # Framework web
uvicorn==0.24.0          # ASGI server
sqlmodel==0.0.14         # ORM + validação
psycopg2-binary==2.9.9   # Driver PostgreSQL
python-multipart==0.0.6  # Parsing form data
```

Ver `requirements.txt` para lista completa.

## 🐳 Docker

### Build

```bash
# Build imagem
docker-compose build

# Build sem cache
docker-compose build --no-cache
```

### Run

```bash
# Modo daemon
docker-compose up -d

# Modo foreground (logs visíveis)
docker-compose up

# Logs
docker-compose logs -f app

# Logs do banco
docker-compose logs -f postgres
```

### Cleanup

```bash
# Parar containers
docker-compose down

# Remover tudo (including volumes)
docker-compose down -v

# Remover imagens
docker-compose down --rmi all
```

## 🛡️ Segurança

- ✅ Python 3.12 (latest)
- ✅ Alpine Linux (imagem menor)
- ✅ Multi-stage build (sem dev dependencies)
- ✅ Usuário não-root executa app
- ✅ Health checks ativados
- ✅ Environment variables para secrets
- ✅ `.gitignore` protege `.env`

### Checklist de Produção

- [ ] Alterar `SECRET_KEY` para valor aleatório longo
- [ ] Alterar senhas padrão admin
- [ ] Configurar HTTPS/SSL
- [ ] Configurar CORS se necessário
- [ ] Adicionar rate limiting
- [ ] Configurar logs centralizados
- [ ] Adicionar backup automático DB
- [ ] Testar disaster recovery

## 🐛 Troubleshooting

### Container não inicia
```bash
# Verificar logs
docker-compose logs postgres
docker-compose logs app

# Verificar se porta 5432 está em uso
netstat -ano | findstr :5432  # Windows
lsof -i :5432  # Linux/macOS
```

### Erro de conexão DB
```bash
# Verificar se PostgreSQL está rodando
docker-compose ps

# Reiniciar
docker-compose restart postgres
```

### Usuário admin não criado
```bash
# Envs não lidas, criar manualmente:
# 1. Conectar ao DB
docker exec -it cronograma_postgres psql -U seu_usuario cronograma_dev

# 2. Inserir usuário manualmente (usar hash de senha)
```

### Limpar tudo e recomeçar
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

## 📝 Logs

### Local
```bash
# Terminal mostrará logs
# Press Ctrl+C para parar
```

### Docker
```bash
# Ver logs em tempo real
docker-compose logs -f

# Ver últimas N linhas
docker-compose logs --tail=50

# Ver logs de um serviço específico
docker-compose logs app
docker-compose logs postgres
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/novo-feature`)
3. Commit mudanças (`git commit -m 'Add novo-feature'`)
4. Push para branch (`git push origin feature/novo-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é licenciado sob a **Apache License 2.0** - veja o arquivo [LICENSE](LICENSE) para detalhes.

```
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## 📞 Suporte

Para dúvidas ou issues:
- 📧 Email: michelsb@gmail.com
- 🐛 Abrir issue no GitHub
- 💬 Discussões na comunidade

---

**Desenvolvido com ❤️ para UFC**

Copyright © 2026 Michel S.B. | Licenciado sob Apache License 2.0

Última atualização: Fevereiro 2026
