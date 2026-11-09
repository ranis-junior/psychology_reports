import logging

from taskiq import TaskiqDepends

from app.service.email import send_email
from app.settings import get_settings, Settings
from app.worker import broker

logger = logging.getLogger(__name__)


@broker.task
async def send_verification_email(
        email: str,
        token: str,
        expires_in_minutes: int = 1440,
        settings: Settings = TaskiqDepends(get_settings),
) -> None:
    verification_url = f'{settings.FRONTEND_URL}/verify-email?token={token}'
    hours = max(1, expires_in_minutes // 60)
    html = (
        '<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">'
        '<h2>Confirm your account</h2>'
        '<p>Click the link below to validate your email and activate your account:</p>'
        f'<p><a href="{verification_url}">Validate my account</a></p>'
        f'<p>If the button does not work, copy and paste this link into your browser:</p>'
        f'<p>{verification_url}</p>'
        f'<p>This link expires in {hours} hours.</p>'
        '</div>'
    )
    try:
        await send_email(email, 'Validate your account', html)
    except Exception:
        logger.exception('Failed to send verification email to %s', email)
