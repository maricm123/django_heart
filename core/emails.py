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
    Send detailed training session report to client.
    """
    from django.template.loader import render_to_string
    from core.models import EmailTrainingSessionReport

    subject = f"Your Training Session Report - {training_session.title}"

    context = {
        'session': training_session,
        'client_name': training_session.client.user.name or training_session.client.user.email,
        'coach_name': training_session.coach.user.name or training_session.coach.user.email,
        'duration': format_duration(training_session.duration),
        'calories': training_session.calories_burned or 0,
        'metrics': training_session.summary_metrics or {}
    }
    
    # HTML template
    # html_message = render_to_string('emails/session_report.html', context)
    
    # Plain text fallback
    text_message = f"""
        Training Session Report: {training_session.title}

        Coach: {context['coach_name']}
        Date: {training_session.start.strftime('%Y-%m-%d %H:%M')}
        Duration: {context['duration']}
        Calories Burned: {context['calories']} kcal

        Session Metrics:
        - Average HR: {context['metrics'].get('avg_hr', 'N/A')} bpm
        - Max HR: {context['metrics'].get('max_hr', 'N/A')} bpm

        Thank you for your training!
    """

    # AI Prompt (from coach if available)
    ai_prompt = ""
    if hasattr(training_session.coach, 'summary_metric_ai_prompt_for_mails'):
        ai_prompt = training_session.coach.summary_metric_ai_prompt_for_mails or ""
    
    # Create email record BEFORE sending
    email_record = EmailTrainingSessionReport.objects.create_from_session(
        training_session=training_session,
        coach=training_session.coach,
        recipient_email=recipient_email,
        ai_prompt=ai_prompt,
        generated_content=text_message
    )
    
    try:
        msg = EmailMessage(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        # msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)
        
        # Mark as sent
        email_record.mark_as_sent()
        
    except Exception as e:
        # Mark as failed with error
        email_record.mark_as_failed(str(e))
        raise


def format_duration(seconds):
    """Format seconds to HH:MM:SS"""
    if not seconds:
        return "N/A"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
