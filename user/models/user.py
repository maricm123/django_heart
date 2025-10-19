from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from datetime import date
from django.utils.functional import cached_property
from django.db.models import OneToOneRel
from phonenumber_field.modelfields import PhoneNumberField


class CustomUserManager(UserManager):
    def _create_user(
        self,
        first_name,
        last_name,
        email,
        password=None,
        **extra_fields
    ):
        if not email:
            raise ValueError("You have not provided a valid e-mail address")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(
            self,
            first_name=None,
            last_name=None,
            email=None,
            password=None,
            **extra_fields
    ):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(first_name, last_name, email, password, **extra_fields)

    def create_client_user(
            self,
            first_name=None,
            last_name=None,
            email=None,
            **extra_fields
    ):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        if not email:
            raise ValueError("You have not provided a valid e-mail address")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            **extra_fields
        )
        user.save(using=self._db)

        return user

    def create_superuser(
            self,
            first_name="Superuser",
            last_name="User",
            email=None,
            password=None,
            **extra_fields
    ):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(first_name, last_name, email, password, **extra_fields)


class User(
    AbstractBaseUser,
    PermissionsMixin,
):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=False)

    profile_image_url = models.URLField(max_length=500, null=True, blank=True)

    birth_date = models.DateField(null=True, blank=True)

    phone_number = PhoneNumberField(
        blank=True,
        null=True,
        unique=True,  # optional, if you want unique numbers
        # region="US"  # optional, default region for parsing local numbers
    )

    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email} -- {self.first_name} -- {self.last_name}"

    @cached_property
    def name(self):
        return f"{self.first_name.strip()} {self.last_name.strip()}"

    def set_user_active(self):
        self.is_active = True
        self.save()
        return self

    def get_age_from_birth_date(self):
        today = date.today()
        print(today)
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    @property
    def age(self):
        return self.get_age_from_birth_date()

    @cached_property
    def profile(self):
        """Get the profile object from the user (we allow only one for now)."""
        from .base_profile import BaseProfile

        profiles = list()
        for f in User._meta.get_fields():
            if isinstance(f, OneToOneRel) and issubclass(f.related_model, BaseProfile):
                try:
                    profiles.append(getattr(self, f.name))
                except ObjectDoesNotExist:
                    pass
        if len(profiles) == 0:
            return None  # no profile found
        elif len(profiles) == 1:
            return profiles[0]
        else:  # multiple profiles (forbidden in our logic)
            raise Exception("Multiple profiles detected!")

    @property
    def is_coach(self):
        return hasattr(self, "coach")
