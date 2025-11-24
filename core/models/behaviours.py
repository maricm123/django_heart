from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from datetime import date, datetime
from django.utils.timezone import localtime


class HasOneProfileImage(models.Model):
    class Meta:
        abstract = True

    profile_image = models.OneToOneField(
        "core.ProfileImage",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )


class TimeStampable(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_("creations"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("last modification"))


class CreatedBy(models.Model):
    class Meta:
        abstract = True

    created_by = models.ForeignKey("user.User", on_delete=models.CASCADE)


class FramableQueryset(models.query.QuerySet):
    class Meta:
        abstract = True

    def in_interval(self, user, i_start, i_end):
        """
        Returns all objects whose interval has an intersection with the provided interval.
        Returns interval based on client.
        NOTE 31.10.2024
        I added check for user, but when we creating new class it cant create two classes in one time.
        That means here it will not return QuerySet, it can return just one object.
        Based on this maybe we need to change and update function in serializer where we going with for loop.
        """
        qs = self.filter(
            (
                    Q(start__lte=i_start, end__gte=i_start)
                    | Q(start__lte=i_end, end__gte=i_end)
                    | Q(start__gte=i_start, start__lte=i_end)
                    | Q(end__gte=i_start, end__lte=i_end)
            ),
            ~Q(end=i_start) & ~Q(start=i_end),
        )

        # Ovde proveravamo iz kog modela se poziva
        if self.model.__name__ == 'ClassSession':
            return qs.filter(class_header__client=user.client)
        elif self.model.__name__ == 'CourseSession':
            return qs.filter(course_day__course__created_by=user)
        else:
            raise NotImplementedError(f"in_interval not implemented for model {self.model.__name__}")


class Framable(models.Model):
    class Meta:
        abstract = True

    def _check_start_end(self):
        """Raises a ValidationError if end is not after start"""
        if self.end:
            if self.start >= self.end:
                raise ValidationError(MSG_END_DATE_BEFORE_START)

    def clean(self):
        self._check_start_end()

    @staticmethod
    def has_intersection(p1, p2):
        """Return True if 2 framed elements have an intersection"""

        # condition1: any overlap between frames
        condition_1 = (
            p2.start <= p1.start <= p2.end
            or p2.start <= p1.end <= p2.end
            or p1.start <= p2.start <= p1.end
            or p1.start <= p2.end <= p1.end
        )

        # condition2: no same borders
        condition_2 = p1.start != p2.end and p1.end != p2.start

        return condition_1 and condition_2


class DateTimeFramableQuerySet(FramableQueryset, models.query.QuerySet):
    class Meta:
        abstract = True

    def in_frame(self):
        """Returns all objects that have an intersection with now"""
        now = timezone.now()
        return self.filter(start__lte=now, end__gte=now)

    def before_frame(self, before: datetime = None):
        """Returns all objects that are before now or given datetime"""
        now = before or timezone.now()
        return self.filter(end__lte=now)

    def after_frame(self, after: datetime = None):
        """Returns all objects that are after now or given datetime"""
        now = after or timezone.now()
        return self.filter(start__gte=now)

    def day(self, day: date = None):
        """
        Return all objects that starts the provided day.
        Today is the default if day is not provided.
        """
        if day is None:
            day = localtime(timezone.now()).date()
        return self.filter(start__date=day)


class DateTimeFramable(Framable, models.Model):
    class Meta:
        abstract = True

    start = models.DateTimeField(verbose_name=_("start"))
    end = models.DateTimeField(verbose_name=_("end"), null=True, blank=True)

    @property
    def is_current(self):
        return self.start < timezone.now() < self.end

    @property
    def is_before(self):
        return timezone.now() < self.start

    @property
    def is_after(self):
        return timezone.now() > self.end


class IsActiveQuerySet(models.query.QuerySet):
    class Meta:
        abstract = True

    def active(self):
        return self.filter(is_active=True)


class IsActive(models.Model):
    class Meta:
        abstract = True

    is_active = models.BooleanField(default=True)


class HasProfileImage(models.Model):
    class Meta:
        abstract = True

    profile_image = models.ForeignKey("core.ProfileImage", null=True, blank=True, on_delete=models.SET_NULL)
