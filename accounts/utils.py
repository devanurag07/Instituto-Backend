from multiprocessing import reduction
import phonenumbers
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from accounts.roles import Roles


def _validate_mobile(value):
    try:
        value = int(value)
        length = len(str(value))
        if(length != 10):
            return False

    except Exception as e:
        return False

    return True


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


def get_model(model, **args):
    obj_list = model.objects.filter(**args)

    if(obj_list.exists()):
        return True, obj_list.first()

    return False, []
