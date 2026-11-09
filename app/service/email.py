import logging
from email.message import EmailMessage

import aiosmtplib

from app.settings import settings

logger = logging.getLogger(__name__)


async def send_email(to: str, subject: str, html: str) -> None:
    if not settings.SMTP_HOST or not settings.SMTP_FROM:
        logger.warning(
            'SMTP not configured. Skipping email to %s. subject=%s',
            to, subject,
        )
        return

    message = EmailMessage()
    message['From'] = f'{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM}>'
    message['To'] = to
    message['Subject'] = subject
    message.set_content(
        f'Please enable HTML rendering to view this message.\n\n{html}'
    )
    message.add_alternative(html, subtype='html')

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME or None,
            password=settings.SMTP_PASSWORD or None,
            start_tls=settings.SMTP_PORT == 587,
        )
        logger.info('Email sent to %s. subject=%s', to, subject)
    except Exception:
        logger.exception('Failed to send email to %s. subject=%s', to, subject)
        raise
