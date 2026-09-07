import logging

import resend

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class EmailSendError(RuntimeError):
    """The email provider rejected or failed a send.

    Raised by ``_send`` so callers can decide what the user is told. Most routers
    turn it into a 5xx — telling someone "invitation sent" when it wasn't is worse
    than an honest error. The one exception is the password-reset flow, which
    swallows it to keep its response identical whether or not the address exists.
    """


def _send(to: str, subject: str, html: str) -> None:
    settings = get_settings()
    if not settings.resend_api_key:
        logger.info("EMAIL (console mode — no RESEND_API_KEY set)")
        logger.info("  To: %s", to)
        logger.info("  Subject: %s", subject)
        logger.info("  Body:\n%s", html)
        return

    resend.api_key = settings.resend_api_key
    try:
        resend.Emails.send(
            {
                "from": settings.email_from,
                "to": [to],
                "subject": subject,
                "html": html,
            }
        )
    except Exception as exc:
        # A provider error (unverified domain, bad key, rejected recipient) is logged
        # for ops (the link is recoverable from the line below) and re-raised so the
        # caller can surface it instead of reporting a false "sent".
        logger.exception("Failed to send email to %s (subject=%r)", to, subject)
        logger.info("EMAIL fell back to log (send failed). Body:\n%s", html)
        raise EmailSendError(f"Failed to send email to {to}") from exc


def send_invitation(to: str, invitation_token: str) -> None:
    settings = get_settings()
    accept_url = f"{settings.frontend_url}/accept-invitation?token={invitation_token}"
    html = f"""\
<h2>You've been invited to VetBreath</h2>
<p>Your veterinarian has invited you to monitor your dog's respiratory rate.</p>
<p><a href="{accept_url}" style="display:inline-block;padding:12px 24px;background:#2563eb;color:#fff;border-radius:6px;text-decoration:none;">Accept invitation</a></p>
<p>Or copy this link: {accept_url}</p>
<p>This link expires in {settings.invitation_token_expire_days} days.</p>
"""
    _send(to, "You're invited to VetBreath", html)


def send_password_reset(to: str, reset_token: str) -> None:
    settings = get_settings()
    reset_url = f"{settings.frontend_url}/password-reset?token={reset_token}"
    html = f"""\
<h2>Reset your VetBreath password</h2>
<p>Click the button below to choose a new password.</p>
<p><a href="{reset_url}" style="display:inline-block;padding:12px 24px;background:#2563eb;color:#fff;border-radius:6px;text-decoration:none;">Reset password</a></p>
<p>Or copy this link: {reset_url}</p>
<p>If you didn't request this, ignore this email.</p>
"""
    _send(to, "Reset your VetBreath password", html)
