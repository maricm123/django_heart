from core.models import EmailTrainingSessionReport
from django_tenants.utils import schema_context


def get_dashboard_info(request):
    return {
        "gym_name": request.tenant.name,
        "coach_name": request.user.coach.name,
    }


def get_coach_email_reports(coach):
    if not coach:
        return None
    
    with schema_context(coach.gym.schema_name):
        return EmailTrainingSessionReport.objects.filter(
            coach=coach
        ).select_related(
            'training_session',
            'training_session__client',
            'training_session__client__user',
            'coach',
            'coach__user'
        ).order_by('-created_at')


def get_coach_email_reports_filtered(coach, status=None, limit=20):
    if not coach:
        return None
    
    with schema_context(coach.gym.schema_name):
        queryset = EmailTrainingSessionReport.objects.filter(
            coach=coach
        ).select_related(
            'training_session',
            'training_session__client',
            'training_session__client__user',
            'coach',
            'coach__user'
        )
        
        if status and status in ['pending', 'sent', 'failed']:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')[:limit]


def get_coach_email_reports_stats(coach):
    if not coach:
        return {}
    
    with schema_context(coach.gym.schema_name):
        reports = EmailTrainingSessionReport.objects.filter(coach=coach)
        
        total_sent = reports.filter(status='sent').count()
        total_pending = reports.filter(status='pending').count()
        total_failed = reports.filter(status='failed').count()
        total = reports.count()
        
        success_rate = (total_sent / total * 100) if total > 0 else 0
        average_attempts = (sum(r.attempt_count for r in reports) / total) if total > 0 else 0
        
        return {
            'total_emails': total,
            'sent': total_sent,
            'pending': total_pending,
            'failed': total_failed,
            'success_rate': f"{success_rate:.2f}%",
            'average_attempts': round(average_attempts, 2)
        }