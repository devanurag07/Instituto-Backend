from batch.models import Batch
from rest_framework.serializers import ModelSerializer


class BatchSerializer(ModelSerializer):
    class Meta:
        moedel = Batch
        fields = "__all__"
