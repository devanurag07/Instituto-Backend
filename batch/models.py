from distutils.command.upload import upload
from email.policy import default
from pyexpat import model
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
    blacklist_students = models.ManyToManyField(User)

    history = HistoricalRecords()


# Approve Requests
class StudentRequest(models.Model):
    batch = models.ForeignKey(
        Batch, related_name="requests", on_delete=models.CASCADE)

    approved = models.BooleanField(default=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    history = HistoricalRecords()


# Personal Conversation
class Message(models.Model):
    message = models.TextField()
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages")
    reciever = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="recieved_messages", blank=True)

    is_reply = models.BooleanField(default=False)
    parent_msg = models.ForeignKey(
        "Message", on_delete=models.CASCADE, related_name="messages", null=True, blank=True)

    is_batch_msg = models.BooleanField(default=False)
    batch = models.ForeignKey(
        Batch, on_delete=models.CASCADE, related_name="messages", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


# Managing The Media
class Image(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="media/images")
    created_at = models.DateTimeField(auto_now_add=True)


class Media(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    file = models.FileField(upload_to="media/images")
    created_at = models.DateTimeField(auto_now_add=True)


class Blocked(models.Model):
    blocked_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blocklist")

    victim = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
