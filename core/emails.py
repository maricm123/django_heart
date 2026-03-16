from dataclasses import dataclass
from typing import Literal
from django.conf import settings
from django.core.mail import EmailMessage


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
    Send detailed training session report to client via Celery task.
    """
    from core.models import EmailTrainingSessionReport
    from core.tasks import send_training_session_report_email_task

    subject = f"Your Training Session Report - {training_session.title}"

    # Ekstraktuj summary metrike
    metrics = training_session.summary_metrics or {}
    summary = metrics.get('summary', {})
    
    # Plain text fallback
    text_message = f"""
        Training Session Report: {training_session.title}

        Coach: {training_session.coach.user.name or training_session.coach.user.email}
        Date: {training_session.start.strftime('%Y-%m-%d %H:%M')}
        Duration: {format_duration(training_session.duration)}
        Calories Burned: {summary.get('calories', 0):.2f} kcal

        Session Metrics:
        - Average HR: {summary.get('avg_hr', 'N/A')} bpm
        - Max HR: {summary.get('max_hr', 'N/A')} bpm
        - Duration: {format_duration(summary.get('duration_seconds', 0))}

        Thank you for your training!
    """

    # AI Prompt (from coach if available)
    ai_prompt = ""
    if hasattr(training_session.coach, 'summary_metric_ai_prompt_for_mails'):
        ai_prompt = training_session.coach.summary_metric_ai_prompt_for_mails or ""
    
    # Create email record
    email_record = EmailTrainingSessionReport.create(
        training_session=training_session,
        coach=training_session.coach,
        recipient_email=recipient_email,
        ai_prompt=ai_prompt,
        generated_content=text_message,
        tenant_schema_name=training_session.coach.gym.schema_name
    )

    # Triggeraj Celery task za slanje
    send_training_session_report_email_task.delay(
        email_record.id,
        training_session.coach.gym.schema_name
    )


def format_duration(seconds):
    """Format seconds to HH:MM:SS"""
    if not seconds:
        return "N/A"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
