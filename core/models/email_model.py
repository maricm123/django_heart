from core.models.behaviours import TimeStampable
from django.db import models
from django.utils import timezone


class EmailTrainingSessionReport(TimeStampable):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    training_session = models.ForeignKey('training_session.TrainingSession', on_delete=models.CASCADE, related_name='email_training_session_reports')
    coach = models.ForeignKey('user.Coach', on_delete=models.CASCADE, related_name='email_training_session_reports')
    recipient_email = models.EmailField()

    ai_prompt = models.TextField(help_text="AI prompt used to generate content")
    generated_content = models.TextField(help_text="Generated email content")
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    
    attempt_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)

    class Meta:
        verbose_name = "Email Training Session Report"
        verbose_name_plural = "Email Training Session Reports"

    def __str__(self):
        return f"Email Report for Session {self.training_session.id} to {self.recipient_email}"

    def mark_as_sent(self):
        """Mark email as sent."""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at'])

    def mark_as_failed(self, error_message):
        """Mark email as failed with error message."""
        self.status = 'failed'
        self.error_message = error_message
        self.attempt_count += 1
        self.save(update_fields=['status', 'error_message', 'attempt_count'])

    @classmethod
    def create(
        cls,
        **kwargs
    ):
        email = cls.objects.create(**kwargs)
        return email
