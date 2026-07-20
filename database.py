import os
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from dotenv import load_dotenv

# Carrega as variáveis de segurança (senhas e portas) do nosso arquivo .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "inforday_db")

# Monta a URL de conexão com o PostgreSQL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Cria o Pool Assíncrono (o nosso "clube" de conexões)
pool = AsyncConnectionPool(
    conninfo=DATABASE_URL,
    open=False,  # O pool começará fechado e será aberto quando ligarmos o servidor FastAPI
    kwargs={"row_factory": dict_row}  # Transforma os resultados do banco em dicionários Python (perfeito para JSON)
)

async def get_db():
    """
    Função 'geradora' que injeta uma conexão do pool nas rotas da API 
    e devolve a conexão com segurança logo após o uso.
    """
    async with pool.connection() as conn:
        yield conn