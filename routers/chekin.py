from fastapi import APIRouter, Depends, HTTPException, status
from psycopg import AsyncConnection
from datetime import datetime
from database import get_db
from schemas import CheckinRequest, CheckinResponse

# Criamos o agrupador de rotas de Check-in
router = APIRouter(prefix="/api/v1/checkin", tags=["Check-in"])

@router.post("/", response_model=CheckinResponse, status_code=status.HTTP_200_OK)
async def registrar_checkin(dados: CheckinRequest, db: AsyncConnection = Depends(get_db)):
    async with db.cursor() as cur:
        # 1. Busca quem é o dono deste QR Code
        await cur.execute(
            "SELECT id, nome_completo, status FROM inscricoes WHERE codigo_qrcode = %s;",
            (dados.codigo_qrcode,)
        )
        inscricao = await cur.fetchone()

        # 2. QR Code não existe no banco (pode ser falso/antigo)
        if not inscricao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="QR Code inválido ou não encontrado no sistema."
            )

        # 3. Regra de Fraude: Aluno já entrou no evento
        if inscricao["status"] == 'CHECKIN_REALIZADO':
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Check-in bloqueado. {inscricao['nome_completo']} já registrou entrada anteriormente."
            )

        # 4. Caminho Feliz: Libera a entrada e atualiza o banco
        # 4. Caminho Feliz: Libera a entrada e atualiza o banco com a hora exata
        query_update = """
            UPDATE inscricoes 
            SET status = 'CHECKIN_REALIZADO', data_checkin = CURRENT_TIMESTAMP
            WHERE id = %s 
            RETURNING nome_completo;
        """
        
        await cur.execute(query_update, (inscricao["id"],))
        
        # Confirma a alteração no banco
        await db.commit()

        # Retorna o painel verde para a equipe de recepção
        return CheckinResponse(
            status="Sucesso",
            mensagem="Entrada liberada com sucesso!",
            aluno=inscricao["nome_completo"],
            data_hora=datetime.now()
        )