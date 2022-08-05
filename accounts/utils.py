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
