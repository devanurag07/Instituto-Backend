from django.db import models
from accounts.models import User
# Create your models here.


class ActiveUser(models.Model):
    channel_name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
