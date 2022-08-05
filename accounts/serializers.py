from wsgiref import validate
from rest_framework.serializers import ModelSerializer, ValidationError
from accounts.models import User
from accounts.utils import _validate_mobile


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "mobile"]

    def validate_mobile(self, mobile):
        if(_validate_mobile(mobile)):
            return mobile

        raise ValidationError("Invalid Mobile Number")
