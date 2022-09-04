from asyncore import read
from dataclasses import dataclass, fields
from pickletools import read_floatnl
from re import sub
from turtle import Turtle
from xmlrpc.client import FastParser
from accounts.models import Owner, User
from accounts.serializers import UserSerializer
from accounts.utils import resp_fail, resp_success
from .models import Institute, Subject, SubjectAccess, TeacherRequest
from .serializers import SubjectSerialzier
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


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


# Institute
def get_teacher_requests(institute):
    teacher_requests = TeacherRequest.objects.filter(
        institute=institute, approved=False)

    class TeacherRequestSerializer(ModelSerializer):
        teacher = UserSerializer(many=False, read_only=True)

        class Meta:
            model = TeacherRequest
            fields = "__all__"

    data = TeacherRequestSerializer(teacher_requests, many=True).data
    return data
