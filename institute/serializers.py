from dataclasses import field, fields
from .models import Batch, Subject
from rest_framework.serializers import ModelSerializer


class SubjectSerialzier(ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class BatchSerializer(ModelSerializer):
    class Meta:
        moedel = Batch
        fields = "__all__"
