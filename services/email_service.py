import smtplib
import os
import io
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formatdate, make_msgid
from dotenv import load_dotenv
import qrcode

load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
EMAIL_SENHA_APP = os.getenv("EMAIL_SENHA_APP")

def enviar_email_confirmacao_sync(email_destino: str, nome_aluno: str, qrcode_uuid: str):
    if not EMAIL_REMETENTE or not EMAIL_SENHA_APP:
        raise ValueError("EMAIL_REMETENTE ou EMAIL_SENHA_APP não configurados no .env!")

    # 1. Gera o QR Code em memória
    qr_img = qrcode.make(qrcode_uuid)
    img_buffer = io.BytesIO()
    qr_img.save(img_buffer, format="PNG")
    img_data = img_buffer.getvalue()

    # 2. Container Raiz do e-mail (related)
    msg_root = MIMEMultipart("related")
    msg_root["Subject"] = "Inforday - Confirmação de Inscrição e Credencial"
    msg_root["From"] = f"Equipe Inforday <{EMAIL_REMETENTE}>"
    msg_root["To"] = email_destino
    msg_root["Date"] = formatdate(localtime=True)
    msg_root["Message-ID"] = make_msgid()

    # 3. Container para o texto (alternative)
    msg_alternative = MIMEMultipart("alternative")
    msg_root.attach(msg_alternative)

    # 4. Gera ID do anexo
    # Exemplo de resultado do make_msgid: <12345.abc@dominio.com>
    raw_cid = make_msgid(domain="inforday.local") 
    cid_clean = raw_cid.strip("<>")

    # 5. Versão em Texto Puro (Essencial para não ser tratado como spam)
    corpo_texto = f"""Olá, {nome_aluno}!

Sua inscrição para o evento Inforday foi confirmada com sucesso.
Seu Código de Inscrição é: {qrcode_uuid}

Apresente este código ou o QR Code enviado no e-mail na entrada do evento.
"""
    msg_alternative.attach(MIMEText(corpo_texto, "plain", "utf-8"))

    # 6. Corpo HTML apontando para cid:
    corpo_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <h2>Olá, {nome_aluno}!</h2>
        <p>Sua inscrição para o evento <strong>Inforday</strong> foi confirmada com sucesso.</p>
        <p>Abaixo está o seu QR Code oficial de acesso. Apresente esta credencial na portaria do evento e nas salas de workshops:</p>
        
        <div style="text-align: center; margin: 25px 0;">
            <img src="cid:{cid_clean}" alt="QR Code de Acesso" width="220" height="220" style="width: 220px; height: 220px; border: 1px solid #ddd; padding: 10px; border-radius: 8px; display: block; margin: 0 auto;" />
        </div>
        
        <p style="text-align: center; font-size: 14px; color: #666;">
            Código de Inscrição: <code>{qrcode_uuid}</code>
        </p>
        
        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;" />
        <p style="font-size: 12px; color: #888;">Esta é uma mensagem automática gerada pela organização do Inforday. Por favor, não responda a este e-mail.</p>
      </body>
    </html>
    """
    msg_alternative.attach(MIMEText(corpo_html, "html", "utf-8"))

    # 7. Configuração da Imagem embutida (Anexa direto na RAIZ 'related')
    msg_image = MIMEImage(img_data, _subtype="png")
    
    # IMPORTANTE: O Content-ID precisa estar entre < >
    msg_image.add_header("Content-ID", f"<{cid_clean}>")
    msg_image.add_header("Content-Disposition", "inline", filename="qrcode.png")
    
    msg_root.attach(msg_image)

    # 8. Disparo
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_REMETENTE, EMAIL_SENHA_APP)
        server.sendmail(EMAIL_REMETENTE, email_destino, msg_root.as_string())