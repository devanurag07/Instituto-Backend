from django.db import models
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from accounts.models import User
from institute.models import Institute, Subject
# Create your models here.
# Create your models here.


# Class and Subject
CLASS_CHOICES = [
    (str(i), str(i)) for i in range(1, 13)
]


class Batch(models.Model):
    batch_name = models.CharField(max_length=255)
    batch_code = models.CharField(max_length=255, unique=True)

    grade = models.CharField(
        default="1", choices=CLASS_CHOICES, max_length=20)

    batch_subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    institute = models.ForeignKey(
        Institute, on_delete=models.CASCADE)

    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="teacher_batches")

    students = models.ManyToManyField(User, related_name="batches")
    blocklist = models.ManyToManyField(User)

    history = HistoricalRecords()


# Approve Requests
class StudentRequest(models.Model):
    batch = models.ForeignKey(
        Batch, related_name="requests", on_delete=models.CASCADE)

    approved = models.BooleanField(default=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    history = HistoricalRecords()
