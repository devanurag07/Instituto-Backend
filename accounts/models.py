from email.policy import default
from random import choices
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from accounts.managers import CustomUserManager, StudentManager, OwnerManager, TeacherManager
from accounts.roles import Roles
from .valdiators import _validate_mobile
from simple_history.models import HistoricalRecords
from django.utils import timezone
# Create your models here.


class User(AbstractUser):
    username = None
    email = models.EmailField(blank=True)
    mobile = models.BigIntegerField(
        blank=False, unique=True)
    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    default_type = Roles.NULL
    role = models.CharField(
        _("Role"), choices=Roles.choices, default=default_type, max_length=255)

    is_verified = models.BooleanField(default=False)
    is_created = models.BooleanField(default=False)

    class GenderChoices(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"

    gender = models.CharField(
        max_length=255, choices=GenderChoices.choices, default=GenderChoices.MALE)

    history = HistoricalRecords()

    def __str__(self) -> str:
        return f"m-{self.first_name + ' '+ self.last_name} Role: {self.role}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.default_type
            self.set_password(self.password)

        return super().save(*args, **kwargs)


class Student(User):

    default_type = Roles.STUDENT
    objects = StudentManager()

    class Meta:
        proxy = True


class Owner(User):
    default_type = Roles.OWNER
    objects = OwnerManager()

    class Meta:
        proxy = True


class Teacher(User):
    default_type = Roles.TEACHER
    objects = TeacherManager()

    class Meta:
        proxy = True

# OTP Models


class OtpTempData(models.Model):
    otp = models.IntegerField()
    mobile = models.BigIntegerField()
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    attempts = models.IntegerField(default=0)

    created_at = models.DateTimeField(
        auto_now_add=True)

    history = HistoricalRecords()


class LoginOtp(models.Model):
    otp = models.IntegerField()
    mobile = models.BigIntegerField()
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(
        auto_now_add=True)

    history = HistoricalRecords()
