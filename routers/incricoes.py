import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from psycopg import AsyncConnection
from database import get_db
from schemas import InscricaoCreate, InscricaoResponse

# Criamos o agrupador de rotas de Inscrições
router = APIRouter(prefix="/api/v1/inscricoes", tags=["Inscrições"])

def limpar_digitos(valor: str) -> str:
    """Remove caracteres especiais (pontos, traços, espaços) deixando apenas números."""
    return "".join(filter(str.isdigit, valor))

@router.post("/", response_model=InscricaoResponse, status_code=status.HTTP_201_CREATED)
async def criar_inscricao(dados: InscricaoCreate, db: AsyncConnection = Depends(get_db)):
    # 1. Tratamento de entrada: Limpa o CPF para salvar apenas números
    cpf_limpo = limpar_digitos(dados.cpf)
    
    if len(cpf_limpo) != 11:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="CPF inválido. Deve conter exatamente 11 dígitos numéricos."
        )

    async with db.cursor() as cur:
        # 2. Regra de Negócio: Verifica se E-mail ou CPF já existem no banco
        await cur.execute(
            "SELECT email, cpf FROM inscricoes WHERE email = %s OR cpf = %s;",
            (dados.email, cpf_limpo)
        )
        existe = await cur.fetchone()
        
        if existe:
            if existe["email"] == dados.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Este e-mail já está cadastrado no evento."
                )
            if existe["cpf"] == cpf_limpo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Este CPF já está cadastrado no evento."
                )

        # 3. Gera um Token criptográfico único de 64 caracteres hex para o QR Code do aluno
        codigo_qrcode = secrets.token_hex(32)

        # 4. Inserção Segura via SQL Parametrizado
        query_insert = """
            INSERT INTO inscricoes (nome_completo, email, cpf, telefone, serie_categoria, codigo_qrcode)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, nome_completo, email, cpf, serie_categoria, codigo_qrcode, status, criado_em;
        """
        
        await cur.execute(
            query_insert,
            (dados.nome_completo, dados.email, cpf_limpo, dados.telefone, dados.serie_categoria, codigo_qrcode)
        )
        nova_inscricao = await cur.fetchone()
        
        # Confirma a transação no PostgreSQL
        await db.commit()

        return nova_inscricao