from fastapi import APIRouter, Depends, HTTPException, status
from psycopg import AsyncConnection
from datetime import datetime
from database import get_db
from schemas import CheckinAtividadeRequest, CheckinResponse # Crie o schema para receber qrcode e atividade_id

router = APIRouter(prefix="/api/v1/checkin-atividade", tags=["Check-in Atividades"])

@router.post("/", response_model=CheckinResponse, status_code=status.HTTP_200_OK)
async def registrar_checkin_atividade(
    dados: CheckinAtividadeRequest, 
    db: AsyncConnection = Depends(get_db)
):
    async with db.cursor() as cur:
        # 1. Tenta realizar o UPDATE atômico com todas as travas
        query_update = """
            UPDATE inscricoes_atividades ia
            SET data_checkin = CURRENT_TIMESTAMP
            FROM inscricoes i, atividades a
            WHERE ia.inscricao_id = i.id 
              AND ia.atividade_id = a.id
              AND i.codigo_qrcode = %s
              AND ia.atividade_id = %s
              AND ia.status = 'CONFIRMADA'
              AND ia.data_checkin IS NULL
            RETURNING i.nome_completo, a.nome AS nome_atividade;
        """
        
        await cur.execute(query_update, (dados.codigo_qrcode, dados.atividade_id))
        sucesso = await cur.fetchone()

        # CAMINHO FELIZ: Atualizou 1 linha, entrada no workshop liberada
        if sucesso:
            await db.commit()
            
            nome_aluno = sucesso["nome_completo"] if isinstance(sucesso, dict) else sucesso[0]
            nome_workshop = sucesso["nome_atividade"] if isinstance(sucesso, dict) else sucesso[1]

            return CheckinResponse(
                status="Sucesso",
                mensagem=f"Entrada liberada para a atividade: {nome_workshop}",
                aluno=nome_aluno,
                data_hora=datetime.now()
            )

        # DIAGNÓSTICO DE ERROS (Executado apenas se o UPDATE alterar 0 linhas)
        
        # Caso A: Checar se o QR Code do aluno existe
        await cur.execute("SELECT id FROM inscricoes WHERE codigo_qrcode = %s;", (dados.codigo_qrcode,))
        aluno_existe = await cur.fetchone()
        if not aluno_existe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="QR Code inválido ou não encontrado."
            )

        # Caso B: Checar a situação da vaga na tabela de vínculo
        await cur.execute(
            """
            SELECT ia.status, ia.data_checkin 
            FROM inscricoes_atividades ia
            JOIN inscricoes i ON i.id = ia.inscricao_id
            WHERE i.codigo_qrcode = %s AND ia.atividade_id = %s;
            """,
            (dados.codigo_qrcode, dados.atividade_id)
        )
        vinculo = await cur.fetchone()

        # B1: O aluno não se inscreveu neste workshop específico
        if not vinculo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Aluno não possui inscrição nesta atividade."
            )

        # B2: O aluno já fez o check-in no workshop
        status_vaga = vinculo["status"] if isinstance(vinculo, dict) else vinculo[0]
        checkin_realizado = vinculo["data_checkin"] if isinstance(vinculo, dict) else vinculo[1]

        if checkin_realizado:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Check-in já realizado anteriormente nesta atividade."
            )

        # B3: A inscrição existe, mas está cancelada ou em fila de espera
        if status_vaga != 'CONFIRMADA':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Inscrição na atividade com status '{status_vaga}'. Entrada não permitida."
            )