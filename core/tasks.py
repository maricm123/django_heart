from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_training_session_report_email_task(self, email_report_id, tenant_schema_name):
    """
    Asinkroni task za slanje email reporta treninga.
    """
    from core.models import EmailTrainingSessionReport
    from django_tenants.utils import schema_context
    
    try:
        # Prvo pronađi email report iz public schema
        with schema_context(tenant_schema_name):  # ← Koristi sačuvan schema
            email_report = EmailTrainingSessionReport.objects.get(id=email_report_id)
        
            # Postavi tenant context
            logger.info(f"Email schema: {email_report.tenant_schema_name}")
            print(email_report.tenant_schema_name, "ASDASDASDAS")  # Debug: provjeri koji tenant schema se koristi
            # Sada su sve baza operacije u tenant schema-i
            email_report = EmailTrainingSessionReport.objects.get(id=email_report_id)
            print(email_report)
            logger.info(f"Email schema: {email_report}")
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


@shared_task
def test_database_connection():
    """Test da li Celery može pristupiti bazi sa schema_context"""
    from django_tenants.utils import schema_context
    from gym.models import GymTenant
    
    try:
        # Prvo pronađi sve tenante
        tenants = GymTenant.objects.all()
        logger.info(f"Found {tenants.count()} tenants")
        
        for tenant in tenants:
            logger.info(f"Testing schema: {tenant.schema_name}")
            
            with schema_context(tenant.schema_name):
                try:
                    from core.models import EmailTrainingSessionReport
                    email_count = EmailTrainingSessionReport.objects.count()
                    logger.info(f"✅ {tenant.schema_name}: Email reports = {email_count}")
                except Exception as e:
                    logger.error(f"❌ {tenant.schema_name}: {str(e)}")
        
        return {"status": "success", "message": "All schemas tested"}
        
    except Exception as e:
        logger.error(f"❌ General error: {str(e)}")
        return {"status": "failed", "error": str(e)}
