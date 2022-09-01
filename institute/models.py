from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from accounts.models import User
# Create your models here.


# Institute
class Institute(models.Model):
    institute_name = models.CharField(max_length=255)
    institute_code = models.CharField(max_length=255, unique=True)
    institute_desc = models.TextField()
    max_students = models.IntegerField()
    owner = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="institute")

    # [One teacher can have one institute ]
    history = HistoricalRecords()


# Class and Subject
CLASS_CHOICES = [
    (str(i), str(i)) for i in range(1, 13)
]


class Subject(models.Model):
    subject_name = models.CharField(max_length=255)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    history = HistoricalRecords()


class SubjectAccess(models.Model):
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="access_objects")
    grade = models.CharField(
        default="1", choices=CLASS_CHOICES, max_length=20)
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subject_accesses")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="given_accesses")

    history = HistoricalRecords()


class TeacherRequest(models.Model):
    institute = models.ForeignKey(
        Institute, on_delete=models.CASCADE, related_name="requests")

    approved = models.BooleanField(default=False)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)

    history = HistoricalRecords()


# Profiles
class OwnerProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="owner_profile")
    history = HistoricalRecords()


class TeacherProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="teacher_profile")

    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)

    history = HistoricalRecords()


class StudentProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="student_profile")

    father_name = models.CharField(max_length=255, null=True)
    mother_name = models.CharField(max_length=255, null=True)

    history = HistoricalRecords()
