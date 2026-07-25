from fastapi import APIRouter, Depends, HTTPException, status
from psycopg import AsyncConnection
from datetime import datetime
from database import get_db
from schemas import CheckinRequest, CheckinResponse

router = APIRouter(prefix="/api/v1/checkin", tags=["Check-in"])

@router.post("/", response_model=CheckinResponse, status_code=status.HTTP_200_OK)
async def registrar_checkin(dados: CheckinRequest, db: AsyncConnection = Depends(get_db)):
    async with db.cursor() as cur:
        # 1. Tenta atualizar a linha ONDE o qrcode é igual E o checkin ainda é NULL.
        # Retornamos o nome_completo para usar na resposta se der certo.
        query_update = """
            UPDATE inscricoes 
            SET data_checkin = CURRENT_TIMESTAMP
            WHERE codigo_qrcode = %s AND data_checkin IS NULL
            RETURNING nome_completo;
        """
        
        await cur.execute(query_update, (dados.codigo_qrcode,))
        inscricao = await cur.fetchone()

        # 2. Se 'inscricao' veio preenchida, o update funcionou (1 linha alterada)
        if inscricao:
            await db.commit()
            
            # Pega o nome retornado pela query (psycopg pode retornar dict ou tuple dependendo do row_factory)
            nome_aluno = inscricao["nome_completo"] if isinstance(inscricao, dict) else inscricao[0]

            return CheckinResponse(
                status="Sucesso",
                mensagem="Entrada liberada com sucesso!",
                aluno=nome_aluno,
                data_hora=datetime.now()
            )

        # 3. Se 'inscricao' veio vazia, a query alterou 0 linhas.
        # Isso significa uma de duas coisas: O QR Code não existe OU já fez check-in.
        await cur.execute(
            "SELECT id, data_checkin FROM inscricoes WHERE codigo_qrcode = %s;",
            (dados.codigo_qrcode,)
        )
        registro_existente = await cur.fetchone()

        # Caso A: QR Code nem existe no banco
        if not registro_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="QR Code inválido ou não encontrado no sistema."
            )

        # Caso B: O QR Code existe, logo o UPDATE falhou porque data_checkin NÃO era NULL
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="QR Code já utilizado! Check-in recusado para evitar duplicidade."
        )