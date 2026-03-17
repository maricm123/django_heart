from dataclasses import dataclass
from multiprocessing import context
from typing import Literal
from django.conf import settings
from django.core.mail import EmailMessage
from core.ai_service import generate_session_summary


ContactKind = Literal["contact", "demo"]


@dataclass(frozen=True)
class ContactEmailPayload:
    name: str
    email: str
    message: str
    kind: ContactKind = "contact"
    company: str = ""
    phone: str = ""


def send_contact_email(payload: ContactEmailPayload) -> None:
    to_email = getattr(settings, "CONTACT_FORM_TO_EMAIL", None) or getattr(
        settings, "DEFAULT_FROM_EMAIL", None
    )
    if not to_email:
        raise RuntimeError("CONTACT_FORM_TO_EMAIL or DEFAULT_FROM_EMAIL must be set.")

    subject = "HeartApp - Contact form"
    if payload.kind == "demo":
        subject = "HeartApp - Book a Demo"

    body = (
        f"Kind: {payload.kind}\n"
        f"Name: {payload.name}\n"
        f"Email: {payload.email}\n"
        f"Company: {payload.company}\n"
        f"Phone: {payload.phone}\n\n"
        f"Message:\n{payload.message}\n"
    )

    msg = EmailMessage(
        subject=subject,
        body=body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=[to_email],
        reply_to=[payload.email],
    )
    msg.send(fail_silently=False)


def send_training_session_report_email(training_session, recipient_email: str) -> None:
    """
    Kreiraj email record i pokreni AI summary generation (asinhrono).
    """
    from core.models import EmailTrainingSessionReport
    from core.tasks import generate_ai_summary_task
    import logging

    logger = logging.getLogger(__name__)

    # AI Prompt (from coach if available)
    ai_prompt = ""
    if hasattr(training_session.coach, 'summary_metric_ai_prompt_for_mails'):
        ai_prompt = training_session.coach.summary_metric_ai_prompt_for_mails or ""
    
    # 1. Kreiraj email record
    logger.info(f"[EMAIL] Creating EmailTrainingSessionReport for session {training_session.id}")
    email_record = EmailTrainingSessionReport.create(
        training_session=training_session,
        coach=training_session.coach,
        recipient_email=recipient_email,
        ai_prompt=ai_prompt,
        generated_content="",  # Prazno za sada, biće generirano u task-u
        tenant_schema_name=training_session.coach.gym.schema_name
    )
    
    logger.info(f"[EMAIL] Email record created with ID: {email_record.id}")

    # 2. Pokreni Celery task za AI summary + email
    logger.info(f"[EMAIL] Triggering AI summary task for email {email_record.id}")
    generate_ai_summary_task.delay(
        email_record.id,
        training_session.coach.gym.schema_name
    )
    
    logger.info(f"[EMAIL] Email generation started (async)")
    return {"status": "processing", "email_id": email_record.id}


def format_duration(seconds):
    """Format seconds to HH:MM:SS"""
    if not seconds:
        return "N/A"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
