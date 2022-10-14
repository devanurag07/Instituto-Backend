from dataclasses import field
from batch.models import Batch, Message
from rest_framework.serializers import ModelSerializer


class BatchSerializer(ModelSerializer):
    class Meta:
        model = Batch
        fields = "__all__"


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"
