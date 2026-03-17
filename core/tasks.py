from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
import logging
from core.emails import format_duration
import openai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_ai_summary_task(self, email_report_id, tenant_schema_name):
    """
    Generiši AI summary, renderuj template, i pokreni email slanje (asinkrono).
    """
    from core.models import EmailTrainingSessionReport
    from core.ai_service import generate_session_summary
    from django_tenants.utils import schema_context
    from django.template.loader import render_to_string
    
    try:
        with schema_context(tenant_schema_name):
            logger.info(f"[AI TASK] Fetching email record {email_report_id}")
            email_report = EmailTrainingSessionReport.objects.get(id=email_report_id)
            
            # 1. Generiši AI summary
            logger.info(f"[AI TASK] Generating AI summary for session {email_report.training_session.id}")
            ai_summary = generate_session_summary(
                email_report.training_session, 
                email_report.coach
            )
            email_report.ai_prompt = ai_summary
            logger.info(f"[AI TASK] AI Summary: {ai_summary}")
            
            # 2. Pripremi context sa AI summary-jem
            training_session = email_report.training_session
            metrics = training_session.summary_metrics or {}
            summary = metrics.get('summary', {})
            hr_zones = summary.get('hr_zones_seconds', {})
            
            from core.emails import format_duration
            context = {
                'session': training_session,
                'coach_name': email_report.coach.user.name or email_report.coach.user.email,
                'duration': format_duration(training_session.duration),
                'calories': summary.get('calories', 0),
                'avg_hr': summary.get('avg_hr', 'N/A'),
                'max_hr': summary.get('max_hr', 'N/A'),
                'hr_zones': hr_zones,
                'ai_summary': ai_summary,
            }

            # 3. Renderuj template sa AI summary-jem
            logger.info(f"[AI TASK] Rendering template")
            html_message = render_to_string('emails/session_report.html', context)
            email_report.generated_content = html_message
            email_report.save()
            
            logger.info(f"[AI TASK] Template rendered, length: {len(html_message)}")
            
            # 4. Pokreni email slanje task
            logger.info(f"[AI TASK] Triggering email send task")
            send_training_session_report_email_task.delay(
                email_report_id,
                tenant_schema_name
            )
            
            return {"status": "success", "email_id": email_report_id}
            
    except Exception as exc:
        logger.error(f"[AI TASK] Error: {str(exc)}", exc_info=True)
        try:
            with schema_context(tenant_schema_name):
                email_report = EmailTrainingSessionReport.objects.get(id=email_report_id)
                email_report.mark_as_failed(f"AI error: {str(exc)}")
        except:
            pass
        
        try:
            raise self.retry(exc=exc, countdown=60)
        except self.MaxRetriesExceededError:
            return {"status": "failed"}


@shared_task(bind=True, max_retries=3)
def send_training_session_report_email_task(self, email_report_id, tenant_schema_name):
    """
    Asinkroni task za slanje email reporta treninga sa HTML template-om.
    """
    from core.models import EmailTrainingSessionReport
    from django_tenants.utils import schema_context
    
    try:
        # Pronađi email report iz tenant schema-te
        with schema_context(tenant_schema_name):
            logger.info(f"[TASK] Fetching email record {email_report_id} from schema {tenant_schema_name}")
            email_report = EmailTrainingSessionReport.objects.get(id=email_report_id)

            subject = f"Your Training Session Report - {email_report.training_session.title}"

            # Plain text verzija kao fallback
            text_body = f"""
                Training Session Report: {email_report.training_session.title}

                Duration: {email_report.training_session.duration}

                Check your detailed report and metrics online.
            """
            
            # HTML verzija iz template-a
            html_body = email_report.generated_content
            
            logger.info(f"[TASK] HTML content length: {len(html_body) if html_body else 0}")
            if html_body:
                logger.info(f"[TASK] HTML first 150 chars: {html_body[:150]}")
            
            # Kreiraj EmailMessage sa plain text body
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email_report.recipient_email],
            )
            
            # Priloži HTML verziju kao alternativu
            if html_body:
                logger.info(f"[TASK] Attaching HTML alternative")
                msg.attach_alternative(html_body, "text/html")
            else:
                logger.warning(f"[TASK] No HTML content to attach!")
            
            logger.info(f"[TASK] Sending email to {email_report.recipient_email}")
            msg.send(fail_silently=False)
            email_report.mark_as_sent()
            
            logger.info(f"[TASK] Email sent successfully: {email_report.id}")
            return {"status": "success", "email_id": email_report.id}
        
    except Exception as exc:
        logger.error(f"[TASK] Error sending email: {str(exc)}", exc_info=True)
        try:
            with schema_context(tenant_schema_name):
                email_report = EmailTrainingSessionReport.objects.get(id=email_report_id)
                email_report.mark_as_failed(str(exc))
        except Exception as inner_exc:
            logger.error(f"[TASK] Failed to mark email as failed: {str(inner_exc)}")
        
        try:
            raise self.retry(exc=exc, countdown=60)
        except self.MaxRetriesExceededError:
            logger.error(f"[TASK] Max retries exceeded for email {email_report_id}")
            return {"status": "failed", "error": "Max retries exceeded"}
