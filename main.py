from fastapi import FastAPI, Depends, HTTPException, status
from contextlib import asynccontextmanager
from psycopg import AsyncConnection
from database import pool, get_db

# 1. Importando o roteador que você acabou de criar
from routers import incricoes

@asynccontextmanager
async def lifespan(app: FastAPI):
    await pool.open()
    print("🟢 Pool de conexões com o PostgreSQL aberto com sucesso!")
    yield
    await pool.close()
    print("🔴 Pool de conexões encerrado.")

app = FastAPI(
    title="API Inforday",
    version="1.0.0",
    description="API para gestão de inscrições e check-in do evento Inforday",
    lifespan=lifespan
)

# 2. Conectando a rota de inscrições no servidor principal
app.include_router(incricoes.router)

@app.get("/", tags=["Health Check"])
async def health_check(db: AsyncConnection = Depends(get_db)):
    try:
        async with db.cursor() as cur:
            await cur.execute("SELECT 1 AS status;")
            resultado = await cur.fetchone()
            
            if resultado and resultado["status"] == 1:
                return {
                    "status": "online",
                    "mensagem": "API Inforday operacional e conectada ao PostgreSQL!",
                    "database": "conectado"
                }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha na comunicação com o banco de dados: {str(e)}"
        )