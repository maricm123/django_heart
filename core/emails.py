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
    from django.template.loader import render_to_string
    import logging

    logger = logging.getLogger(__name__)
    subject = f"Your Training Session Report - {training_session.title}"

    # Ekstraktuj summary metrike
    metrics = training_session.summary_metrics or {}
    summary = metrics.get('summary', {})
    hr_zones = summary.get('hr_zones_seconds', {})
    
    # Kontekst za template
    context = {
        'session': training_session,
        'coach_name': training_session.coach.user.name or training_session.coach.user.email,
        'duration': format_duration(training_session.duration),
        'calories': summary.get('calories', 0),
        'avg_hr': summary.get('avg_hr', 'N/A'),
        'max_hr': summary.get('max_hr', 'N/A'),
        'hr_zones': hr_zones,
    }
    
    logger.info(f"[EMAIL] Starting to render template for session {training_session.id}")
    logger.info(f"[EMAIL] Context keys: {list(context.keys())}")
    
    # Generiši HTML email iz template-a
    try:
        html_message = render_to_string('emails/session_report.html', context)
        logger.info(f"[EMAIL] HTML template rendered successfully, length: {len(html_message)}")
        
        # Provjeri da li HTML počinje sa <
        if html_message and html_message.strip().startswith('<'):
            logger.info("[EMAIL] HTML looks valid (starts with <)")
        else:
            logger.warning(f"[EMAIL] HTML looks suspicious! First 100 chars: {html_message[:100]}")
            
    except Exception as e:
        logger.error(f"[EMAIL] Error rendering template: {str(e)}", exc_info=True)
        # Fallback na jednostavniji HTML ako rendering pada
        html_message = f"""
        <html>
        <body>
            <h2>{training_session.title}</h2>
            <p>Coach: {context['coach_name']}</p>
            <p>Duration: {context['duration']}</p>
            <p>Calories: {context['calories']:.2f} kcal</p>
            <p>Avg HR: {context['avg_hr']} bpm</p>
            <p>Max HR: {context['max_hr']} bpm</p>
        </body>
        </html>
        """
        logger.info("[EMAIL] Using fallback HTML template")
    
    # Plain text fallback
    text_message = f"""
        Training Session Report: {training_session.title}

        Coach: {context['coach_name']}
        Date: {training_session.start.strftime('%Y-%m-%d %H:%M')}
        Duration: {context['duration']}
        Calories Burned: {context['calories']:.2f} kcal

        Session Metrics:
        - Average HR: {context['avg_hr']} bpm
        - Max HR: {context['max_hr']} bpm
        - Duration: {format_duration(summary.get('duration_seconds', 0))}

        Thank you for your training!
    """

    # AI Prompt (from coach if available)
    ai_prompt = ""
    if hasattr(training_session.coach, 'summary_metric_ai_prompt_for_mails'):
        ai_prompt = training_session.coach.summary_metric_ai_prompt_for_mails or ""
    
    # Create email record
    logger.info(f"[EMAIL] Creating EmailTrainingSessionReport record")
    email_record = EmailTrainingSessionReport.create(
        training_session=training_session,
        coach=training_session.coach,
        recipient_email=recipient_email,
        ai_prompt=ai_prompt,
        generated_content=html_message,
        tenant_schema_name=training_session.coach.gym.schema_name
    )
    
    logger.info(f"[EMAIL] Email record created with ID: {email_record.id}")

    # Triggeraj Celery task za slanje
    logger.info(f"[EMAIL] Triggering Celery task for email {email_record.id}")
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
