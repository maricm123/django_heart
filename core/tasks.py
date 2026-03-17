from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
import logging

logger = logging.getLogger(__name__)


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
            msg = EmailMessage(
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
