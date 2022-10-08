from dataclasses import fields
from ftplib import error_reply
from pyexpat import ErrorString
from accounts.utils import get_model
from institute.models import Subject, SubjectAccess
from institute.serializers import SubjectAccessSerializer
from .serializers import InstituteSerializer
from rest_framework.serializers import ModelSerializer
# Owner


def create_institute(data, owner):
    # Validation Of Data
    institute_form = InstituteSerializer(data=data)
    if(institute_form.is_valid()):
        # Saving Data
        institute = institute_form.save(owner=owner)
        institute_data = InstituteSerializer(institute, many=False).data

        return {
            "created": True,
            "data": institute_data
        }

    else:
        return {
            "created": False,
            "errors": institute_form.errors,
            "data": {

            }
        }
