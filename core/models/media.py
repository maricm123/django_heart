from django.db import models
from core.models.behaviours import TimeStampable


class BaseMedia(
    TimeStampable,
    # CreatedBy
):
    title = models.CharField(max_length=255)
    file_path = models.URLField(null=False, blank=False)  # Store video URL (S3)

    class Meta:
        abstract = True


class ProfileImage(
    BaseMedia
):

    def __str__(self):
        return f"{self.title} {self.id}"

    @classmethod
    def create(cls):
        pass
