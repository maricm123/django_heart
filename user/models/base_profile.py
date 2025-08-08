from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.functional import cached_property
from core.models.behaviours import TimeStampable
from gym.models import GymTenant

User = get_user_model()


class BaseProfile(TimeStampable):
    """
    Used to extend all profiles (Convive / TeamMember) given them tools
    NOTE: only to be used with profiles model, or will create an error.
    """

    class Meta:
        abstract = True

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    gym = models.ForeignKey(
        GymTenant,
        on_delete=models.CASCADE,
        related_name="%(class)ss"
    )

    def __str__(self):
        return f"{self.name} ({self.email})"

    @cached_property
    def as_app_log(self):  # override as_app_log() from AppLogFormatable
        return f"{self.name} ({self.pk})"

    @cached_property
    def name(self):
        return self.user.name
