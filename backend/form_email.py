import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

load_dotenv()  # carga variables .env automáticamente

send_email_endpoint = APIRouter()

class ContactForm(BaseModel):
    name: str
    email: EmailStr
    message: str

@send_email_endpoint.post("/contact")
async def send_email(form: ContactForm):
    try:
        sender_email = os.getenv("EMAIL")  # tu email emisor real (por ejemplo Gmail)
        receiver_email = os.getenv("EMAIL") # donde quieres recibir los mensajes
        password = os.getenv("PASSWORD_APPLICATION")  # contraseña de aplicación desde .env

        if not password:
            raise HTTPException(status_code=500, detail="No se encontró la contraseña en variables de entorno")

        message = MIMEMultipart("alternative")
        message["Subject"] = f"Nuevo mensaje de {form.name} CV Web"
        message["From"] = sender_email
        message["To"] = receiver_email

        # Texto plano (fallback)
        text = f"Nombre: {form.name}\nEmail: {form.email}\nMensaje:\n{form.message}"

        # HTML con estilo avanzado
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>Nuevo mensaje de contacto</title>
        </head>
        <body style="margin:0; padding:0; background-color:#f4f6f8; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        <table align="center" width="600" cellpadding="0" cellspacing="0" style="background:#fff; margin: 40px auto; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <tr>
            <td style="background: #0052cc; padding: 20px 30px; border-radius: 10px 10px 0 0; color: #ffffff; text-align: center;">
                <h1 style="margin: 0; font-weight: 700;">Nuevo mensaje desde CV Web</h1>
            </td>
            </tr>
            <tr>
            <td style="padding: 30px;">
                <p style="font-size: 16px; color: #333;">Has recibido un nuevo mensaje con los siguientes detalles:</p>

                <table width="100%" cellpadding="5" cellspacing="0" style="border-collapse: collapse; margin-top: 20px;">
                <tr>
                    <td style="background: #e7f0fd; font-weight: 600; width: 130px; border-radius: 5px 0 0 5px;">Nombre:</td>
                    <td style="background: #f9fbfd; border-radius: 0 5px 5px 0;">{form.name}</td>
                </tr>
                <tr>
                    <td style="background: #e7f0fd; font-weight: 600; border-radius: 5px 0 0 5px;">Email:</td>
                    <td style="background: #f9fbfd; border-radius: 0 5px 5px 0;">{form.email}</td>
                </tr>
                <tr>
                    <td style="background: #e7f0fd; font-weight: 600; vertical-align: top; border-radius: 5px 0 0 5px;">Mensaje:</td>
                    <td style="background: #f9fbfd; border-radius: 0 5px 5px 0; white-space: pre-line;">{form.message}</td>
                </tr>
                </table>

                <p style="font-size: 14px; color: #777; margin-top: 30px;">Este mensaje fue enviado desde tu formulario web.</p>
            </td>
            </tr>
            <tr>
            <td style="background: #f1f3f5; padding: 15px 30px; text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; color: #999;">
                &copy; 2025 Tu Empresa - Todos los derechos reservados
            </td>
            </tr>
        </table>
        </body>
        </html>
        """

        # Adjuntar ambas versiones
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        message.attach(part1)
        message.attach(part2)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        return {"status": "Mensaje enviado correctamente"}


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enviando email: {str(e)}")
