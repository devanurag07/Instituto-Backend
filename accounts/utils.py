from multiprocessing import reduction
import phonenumbers
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from accounts.roles import Roles
from rest_framework.serializers import ModelSerializer
from accounts.serializers import EmailSerializer

from institute.models import OwnerProfile, StudentProfile, TeacherProfile


def get_role(role_name):
    if role_name.lower() == "student":
        return Roles.STUDENT
    elif role_name.lower() == "owner":
        return Roles.OWNER
    elif role_name.lower() == "teacher":
        return Roles.TEACHER
    else:
        return Roles.NULL


def required_data(data_dict, data_list):
    errors = {

    }

    data = []

    for d in data_list:
        value = data_dict.get(d, None)
        if(not value):
            errors[d] = "This Field Is Required"

        data.append(value)

    if(len(list(errors.values())) == 0):
        return True, data

    return False, errors


def resp_success(message, data={}, status_code=200):

    return {
        'success': True,
        "message": message,
        "data": data,
        "status_code": status_code
    }


def resp_fail(error_msg, data={}, error_code=401):

    return {
        'success': False,
        "message": error_msg,
        "data": data,
        "status_code": error_code
    }


def user_created(user):
    user.is_created = True
    user.save()


def get_profile_model(user):
    user_role = user.role

    if(user_role.lower() == "teacher"):
        model = TeacherProfile
    elif (user_role.lower() == "owner"):
        model = OwnerProfile
    elif(user_role.lower() == "student"):
        model = StudentProfile

    return model


def update_profile(user, data):
    """Return True,profile_data or False,errors
    It updates the profile dynamically ...
    provides you the validation"""
    model = get_profile_model(user)

    class ProfileSerializer(ModelSerializer):
        class Meta:
            model = get_profile_model(user)
            # Getting all field names of data provided
            # {"location":'',"about_me"} => ['location','about_me']

            fields = [*list(data.keys())]

    profile, created = model.objects.get_or_create(user=user)
    profile_form = ProfileSerializer(instance=profile, data=data)
    if(profile_form.is_valid()):
        profile = profile_form.save()
        profile_data = ProfileSerializer(profile, many=False).data

        return True, profile_data

    else:
        errors = profile_form._errors
        return False, errors


def set_email(user, email):
    # Updating Email
    email_srl = EmailSerializer(data={"email": email})
    if(not email_srl.is_valid()):
        return False, email_srl.errors

    # Assigning Email
    user.email = email
    user.save()

    return True, {}


def get_model(model, **args):
    obj_list = model.objects.filter(**args)

    if(obj_list.exists()):
        return {
            "exist": True,
            "data": obj_list.first()
        }

    return {
        "exist": False,
        "data": []
    }


def user_exists(mobile):
    return User.objects.filter(mobile=mobile).exists()
