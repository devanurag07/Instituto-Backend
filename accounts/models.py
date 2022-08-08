from email.policy import default
from random import choices
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from accounts.managers import CustomUserManager, StudentManager, OwnerManager, TeacherManager
from accounts.roles import Roles
from accounts.utils import _validate_mobile
from simple_history.models import HistoricalRecords
from django.utils import timezone
# Create your models here.


class User(AbstractUser):
    username = None
    email = models.EmailField(blank=True)
    mobile = models.BigIntegerField(
        blank=False, unique=True)
    USERNAME_FIELD = 'mobile'

    objects = CustomUserManager()

    default_type = Roles.NULL
    role = models.CharField(
        _("Role"), choices=Roles.choices, default=default_type, max_length=255)

    is_verified = models.BooleanField(default=False)
    is_created = models.BooleanField(default=False)

    history = HistoricalRecords()

    def __str__(self) -> str:
        return f"m-{self.mobile}"

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


# Profiles
class OwnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    history = HistoricalRecords()


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    history = HistoricalRecords()


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    history = HistoricalRecords()


# Institute

class Institute(models.Model):
    institute_name = models.CharField(max_length=255)
    institute_code = models.CharField(max_length=255, unique=True)
    institute_desc = models.TextField()
    max_students = models.IntegerField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    teachers = models.ManyToManyField(User, related_name="institutes")

    history = HistoricalRecords()


class Batch(models.Model):
    batch_name = models.CharField(max_length=255)
    batch_code = models.CharField(max_length=255, unique=True)
    students = models.ManyToManyField(User, related_name="std_batches")

    batch_class = models.IntegerField()
    batch_subject = models.CharField(max_length=255)

    institute = models.ForeignKey(
        Institute, on_delete=models.CASCADE)

    teacher = models.ManyToManyField(User, related_name="teacher_batches")

    history = HistoricalRecords()


# Approve Requests
class StudentRequest(models.Model):
    batch = models.ForeignKey(
        Batch, related_name="requests", on_delete=models.CASCADE)

    approved = models.BooleanField(default=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    history = HistoricalRecords()


class TeacherRequest(models.Model):
    institute = models.ForeignKey(
        Institute, on_delete=models.CASCADE, related_name="requests")

    approved = models.BooleanField(default=False)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)

    history = HistoricalRecords()


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
