from dataclasses import field, fields
from .models import Subject, SubjectAccess
from rest_framework.serializers import ModelSerializer


class SubjectSerialzier(ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class SubjectAccessSerializer(ModelSerializer):
    class Meta:
        model = SubjectAccess
        fields = "__all__"
