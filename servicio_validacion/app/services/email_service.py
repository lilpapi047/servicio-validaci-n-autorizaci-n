import os
import resend
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()

# Configurar la API key de Resend
resend.api_key = os.getenv("RESEND_API_KEY")

# URL del frontend para generar enlaces de verificación
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


def send_verification_email(to_email: str, token: str) -> bool:
    """
    Envía un correo de verificación al usuario con un enlace único.
    Retorna True si el envío fue exitoso, False si hubo un error.
    """

    if not resend.api_key:
        raise ValueError("Falta la variable RESEND_API_KEY en el entorno")

    verification_link = f"{FRONTEND_URL}/verify?token={token}"

    html_content = f"""
        <div style="font-family: Arial, sans-serif; color: #333;">
            <h2>Verifica tu cuenta</h2>
            <p>Gracias por registrarte. Haz clic en el siguiente enlace para verificar tu cuenta:</p>
            <a href="{verification_link}"
               style="display:inline-block; background-color:#2563eb; color:white; padding:10px 20px;
                      text-decoration:none; border-radius:5px; font-weight:bold;">
                Verificar cuenta
            </a>
            <p>Si no solicitaste esta verificación, puedes ignorar este mensaje.</p>
        </div>
    """

    try:
        resend.Emails.send({
            "from": "no-reply@tu-dominio.com",
            "to": [to_email],  # 👈 importante, debe ser una lista
            "subject": "Verifica tu cuenta",
            "html": html_content,
        })
        print(f"Correo de verificación enviado a {to_email}")
        return True  # 👈 esto permite que tu test unitario pase correctamente
    except Exception as e:
        print(f"Error enviando correo a {to_email}: {e}")
        return False
