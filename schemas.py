from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import UUID4

#model do chekin das atividades
class CheckinAtividadeRequest(BaseModel):
    codigo_qrcode: str
    atividade_id: UUID4

# 1. O que o Front-end tem permissão para nos enviar
class InscricaoCreate(BaseModel):
    nome_completo: str = Field(..., min_length=3, max_length=150, description="Nome completo do aluno")
    email: EmailStr = Field(..., description="E-mail válido para contato e envio do QR Code")
    cpf: str = Field(..., min_length=11, max_length=14, description="CPF (aceitamos com ou sem pontuação)")
    telefone: Optional[str] = Field(None, description="Telefone opcional")
    serie_categoria: str = Field(default="GERAL", description="Ex: 1_ANO, 2_ANO, 3_ANO ou GERAL")

# 2. O que nós devolvemos para o Front-end após salvar no banco
class InscricaoResponse(BaseModel):
    id: UUID
    nome_completo: str
    email: EmailStr
    cpf: str
    serie_categoria: str
    codigo_qrcode: str
    status: str
    criado_em: datetime

    # Essa configuração permite que o Pydantic leia os dados que virão lá do PostgreSQL
    model_config = ConfigDict(from_attributes=True)
    
    # 3. O que nós recebemos no momento em que alguém tenta entrar no evento
class CheckinRequest(BaseModel):
    codigo_qrcode: str = Field(..., description="Hash de 64 caracteres lido pelo scanner do evento")

# 4. A resposta visual que devolveremos para a tela do segurança/organizador
class CheckinResponse(BaseModel):
    status: str
    mensagem: str
    aluno: Optional[str] = None
    data_hora: Optional[datetime] = None