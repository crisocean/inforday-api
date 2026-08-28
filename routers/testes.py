from fastapi import APIRouter, status
from pydantic import BaseModel, EmailStr
from services.email_service import enviar_email_confirmacao_sync
import uuid

router = APIRouter(prefix="/api/v1/testes", tags=["Testes & Homologação"])

class TesteEmailRequest(BaseModel):
    email: EmailStr
    nome: str

@router.post("/disparar-email", status_code=status.HTTP_200_OK)
async def testar_servico_email(dados: TesteEmailRequest):
    qrcode_falso = str(uuid.uuid4())
    
    # Execução direta para forçar o erro a aparecer no Swagger/Terminal
    enviar_email_confirmacao_sync(
        email_destino=dados.email, 
        nome_aluno=dados.nome, 
        qrcode_uuid=qrcode_falso
    )

    return {"status": "Sucesso", "mensagem": f"E-mail enviado para {dados.email}!"}