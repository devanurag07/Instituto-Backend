from dataclasses import dataclass
from re import sub
from xmlrpc.client import FastParser
from accounts.models import Owner, User
from accounts.utils import resp_fail, resp_success
from .models import Institute, Subject, SubjectAccess
from .serializers import SubjectSerialzier
resp_success
resp_fail


def get_insitute(owner):
    institute_list = Institute.objects.filter(owner=owner)
    if(institute_list.exists()):
        return {
            "exist": True,
            "data": institute_list.first()
        }

    return {
        "exist": False,
        "data": institute_list
    }


def create_subject(subject, owner):

    institute = get_insitute(owner=owner)

    if(institute["exist"]):
        subject, created = Subject.objects.get_or_create(
            subject_name=subject, institute=institute["data"], defaults={
                "created_by": owner
            })

        if(created):
            return resp_success("Subject Created", {
                "data": SubjectSerialzier(subject).data
            })

        else:
            return resp_fail("Subject Already Exist", {}, 503)
    else:
        return resp_fail("Insitute Does Not Exist", {}, 502)


# Teacher
def get_assigned_subjects(teacher):
    subjects = SubjectAccess.objects.filter(teacher=teacher)
    if(subjects.exists()):
        institutes = set(
            [subject.created_by.institute for subject in subjects])

        return {
            'success': True,
            'data': subjects,
            'institutes': institutes
        }

    return {
        "success": False,
        "data": []
    }


def has_subject_perm(subject, teacher):
    subject_accs = get_assigned_subjects(teacher=teacher)
    if(subject_accs["success"]):

        subjects = [subject_acc.subject for subject_acc in subject_accs['data']]
        if(subject in subjects):
            return True
        return False

    else:
        return False
