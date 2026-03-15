from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_training_session_report_email_task(self, email_report_id):
    """
    Asinkroni task za slanje email reporta treninga.
    """
    from core.models import EmailTrainingSessionReport
    
    try:
        email_report = EmailTrainingSessionReport.objects.get(id=email_report_id)
        
        subject = f"Your Training Session Report - {email_report.training_session.title}"
        body = email_report.generated_content
        
        msg = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_report.recipient_email],
        )
        
        msg.send(fail_silently=False)
        email_report.mark_as_sent()
        
        logger.info(f"Email sent successfully: {email_report.id}")
        return {"status": "success", "email_id": email_report.id}
        
    except EmailTrainingSessionReport.DoesNotExist:
        logger.error(f"EmailTrainingSessionReport {email_report_id} not found")
        return {"status": "failed", "error": "Email record not found"}
        
    except Exception as exc:
        logger.error(f"Error sending email: {str(exc)}")
        try:
            email_report = EmailTrainingSessionReport.objects.get(id=email_report_id)
            email_report.mark_as_failed(str(exc))
        except:
            pass
        
        try:
            raise self.retry(exc=exc, countdown=60)
        except self.MaxRetriesExceededError:
            return {"status": "failed", "error": "Max retries exceeded"}
