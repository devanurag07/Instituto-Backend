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
    institute_form = InstituteSerializer(data=data)
    if(institute_form.is_valid()):
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


def assign_subjects(teacher, subjects, grades, institute):
    # Get Error List
    errors = {

    }

    class SubjectAccSerializer(ModelSerializer):
        class Meta:
            model = SubjectAccess
            fields = ["subject", "grade"]

    for grade in grades:
        for subject_name in subjects:
            subject_name = get_model(
                Subject, subject_name=subject_name, institute=institute)

            if(subject_name["exist"]):
                subject_name = subject_name["data"]
                subject_acc = SubjectAccSerializer(
                    data={"subject": subject_name.id, "grade": grade})
                if(subject_acc.is_valid()):
                    pass
                else:
                    form_errors = subject_acc.errors
                    grade_error = form_errors.get("grade", None)
                    sub_error = form_errors.get("subject", None)

                    errors.setdefault(grade, {})
                    errors[grade]["error"] = grade_error
                    errors[grade][subject_name] = sub_error

            else:
                errors.setdefault(grade, {})
                errors[grade][subject_name] = "Subject Does Not Exist..."

    if(len(errors.keys()) != 0):
        print(errors)
        return False, {
            "errors": errors
        }

    # Create New Access List
    prev_accs = SubjectAccess.objects.filter(
        teacher=teacher, subject__institute=institute)
    prev_accs.delete()

    subject_acc_data = []
    for grade in grades:
        for subject_name in subjects:
            subject = get_model(
                Subject, subject_name=subject_name, institute=institute)

            subject = subject["data"]

            subject_acc, created = SubjectAccess.objects.get_or_create(
                subject=subject, grade=grade, defaults={
                    "teacher": teacher,
                    "created_by": institute.owner
                })

            subject_data = SubjectAccessSerializer(
                subject_acc, many=False).data

            subject_acc_data.append(subject_data)

    return True, subject_acc_data
