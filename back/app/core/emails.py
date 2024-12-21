from typing import Any

import emails  # type: ignore
from jinja2 import Template
from loguru import logger

from app.core.config import get_settings

settings = get_settings()

##########################################################################################
# Base functions to render and send emails
##########################################################################################


def _render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_path = settings.EMAIL_TEMPLATES_BUILD_PATH / template_name
    template_str = template_path.read_text()
    html_content = Template(template_str).render(context)
    return html_content


def _send_email(
    email_to: str, subject: str, template_name: str, context: dict[str, Any]
) -> None:
    """Base function for sending an email"""

    # Add context to be used in every email.
    # Unfortunately, it can't he hardcoded in HTML due to <mj-include> that does not
    # support dynamic data. This is why we need to include it from the back-end.
    context |= {
        "visit_our_website_url": settings.FRONT_URL,
        "privacy_url": settings.FRONT_URL,  # no privacy page for now
        "support_email": settings.EMAIL_FROM_EMAIL,
        "main_logo_url": settings.MAIN_LOGO_URL,
    }

    html_content = _render_email_template(template_name=template_name, context=context)
    if settings.EMAIL_BACKEND == "dummy":
        pass  # does nothing, on purpose

    elif settings.EMAIL_BACKEND == "console":
        logger.success(
            f"An email has been sent (not for real) to: {email_to} with subject: {subject}"
        )

    elif settings.EMAIL_BACKEND == "smtp":
        message = emails.Message(
            subject=subject,
            html=html_content,
            mail_from=(settings.EMAIL_FROM_NAME, settings.EMAIL_FROM_EMAIL),
        )
        smtp_options: dict[str, Any] = {
            "host": settings.SMTP_HOST,
            "port": settings.SMTP_PORT,
            "user": settings.SMTP_USER,
            "password": settings.SMTP_PASSWORD,
        }
        if settings.SMTP_USE_TLS:
            smtp_options["tls"] = True

        response = message.send(to=email_to, smtp=smtp_options)  # type: ignore
        logger.info(f"send email result: {response}")


##########################################################################################
# Concrete functions
##########################################################################################


def send_reset_password_email(email_to: str, front_reset_password_url: str):
    _send_email(
        email_to=email_to,
        subject="Reset your password",
        template_name="reset_password.html",
        context={
            "header_title": "Password Reset Request",
            "button_primary_text": "Reset your password",
            "button_primary_url": front_reset_password_url,  # dynamically provided
        },
    )
