from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UserConfirmation(models.Model):
    class Meta:
        abstract = True

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)

    def __str__(self):
        return self.user.email


class UserActivationRegisterConfirmation(UserConfirmation):
    expires_at = models.DateTimeField()


class PasswordResetConfirmation(UserConfirmation):
    expires_at = models.DateTimeField()


class DeleteUserProfileConfirmation(UserConfirmation):
    expires_at = models.DateTimeField()
