from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from shared.config import settings


def send_verification_email(to_email: str, token: str) -> bool:
    """
    Envía un correo de verificación al usuario usando SendGrid.
    Retorna True si el envío fue exitoso, False si hubo un error.
    """

    # DEBUG: ver que settings está leyendo bien
    print("[EMAIL] Using email_from:", settings.email_from)
    print("[EMAIL] Using frontend_url:", settings.frontend_url)
    print("[EMAIL] SendGrid key is None?", settings.sendgrid_api_key is None)

    if not settings.sendgrid_api_key:
        print("[SendGrid] Falta SENDGRID_API_KEY en el entorno")
        return False
    
    backend_url = "http://localhost:8000"
    verification_link = f"{settings.frontend_url}/verify?token={token}"

    subject = "Verifica tu cuenta"

    html_content = f"""
        <div style="font-family: Arial, sans-serif; color: #333;">
            <h2>Verifica tu cuenta</h2>
            <p>Gracias por registrarte. Haz clic en el siguiente enlace para verificar tu cuenta:</p>
            <a href="{verification_link}"
               style="display:inline-block; background-color:#2563eb; color:white;
                      padding:10px 20px; text-decoration:none; border-radius:5px;
                      font-weight:bold;">
                Verificar cuenta
            </a>
            <p>Si no solicitaste esta verificación, puedes ignorar este mensaje.</p>
        </div>
    """

    message = Mail(
        from_email=settings.email_from,
        to_emails=to_email,
        subject=subject,
        html_content=html_content,
    )

    try:
        sg = SendGridAPIClient(settings.sendgrid_api_key)
        response = sg.send(message)

        # LOG IMPORTANTE: aquí veremos qué responde SendGrid
        print(
            f"[SendGrid] status={response.status_code} "
            f"body={response.body} "
            f"headers={response.headers}"
        )

        if 200 <= response.status_code < 300:
            print(f"[SendGrid] Correo de verificación enviado a {to_email}")
            return True
        else:
            print(f"[SendGrid] Error inesperado, status={response.status_code}")
            return False

    except Exception as e:
        print(f"[SendGrid] Excepción enviando correo a {to_email}: {e}")
        return False
