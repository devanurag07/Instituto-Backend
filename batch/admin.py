from django.contrib import admin

# Register your models here.
from batch.models import Message, Batch, StudentRequest, Blocked

admin.site.register([Message, Batch, StudentRequest, Blocked])
