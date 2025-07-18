from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db import models, transaction
from django.utils import timezone
from datetime import date


class CustomUserManager(UserManager):
    def _create_user(self, first_name, last_name, email, password=None, **extra_fields):
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

    gender = models.CharField(
        max_length=10,
        choices=[("male", "Male"), ("female", "Female")],
        null=True,
        blank=True
    )
    weight = models.FloatField(null=True, blank=True)   # KG
    height = models.FloatField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    CLIENT = 'client'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (CLIENT, 'Client'),
        (ADMIN, 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=CLIENT)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    def is_admin(self):
        return self.role == self.ADMIN

    def is_client(self):
        return self.role == self.CLIENT

    def __str__(self):
        return f"{self.email} -- {self.first_name} -- {self.last_name}"

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
