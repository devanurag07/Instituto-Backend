from dataclasses import fields
from wsgiref import validate
from rest_framework.serializers import ModelSerializer, ValidationError
from accounts.models import User
from accounts.valdiators import _validate_mobile
from rest_framework import serializers

from institute.models import Institute
from rest_framework.validators import UniqueValidator


class UserSerializer(ModelSerializer):

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "mobile", "id"]

    def validate_mobile(self, mobile):
        if(_validate_mobile(mobile)):
            return mobile

        raise ValidationError("Invalid Mobile Number")


class InstituteSerializer(ModelSerializer):

    class Meta:
        model = Institute
        fields = ["institute_name", "institute_name",
                  "institute_desc", "max_students", "institute_code"]


class EmailSerializer(serializers.Serializer):
    # ...
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())])
