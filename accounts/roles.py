from django.db import models


class Roles(models.TextChoices):
    STUDENT = "Student", "STUDENT"
    TEACHER = "Teacher", "TEACHER"
    OWNER = "Owner", "OWNER"
    NULL = "Null", "NULL"
