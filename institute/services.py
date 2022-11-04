from ast import Pass
from asyncore import read
from dataclasses import dataclass, fields
from pickletools import read_floatnl
from re import sub
from turtle import Turtle
from xmlrpc.client import FastParser
from accounts.models import Owner, User
from accounts.serializers import UserSerializer
from accounts.utils import get_model, resp_fail, resp_success
from .models import Institute, Subject, SubjectAccess, TeacherRequest
from .serializers import SubjectAccessSerializer, SubjectSerialzier
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


def get_insitute(owner):
    """Gives The Institute Attached to Owner"""
    institute_list = Institute.objects.filter(owner=owner)
    if (institute_list.exists()):
        return {
            "exist": True,
            "data": institute_list.first()
        }

    return {
        "exist": False,
        "data": institute_list
    }


def create_subject(subject, owner):
    """Creates Subject [English,Science,Etc] Object 
    for Institute of owner"""

    institute = get_insitute(owner=owner)
    if (institute["exist"]):
        subject, created = Subject.objects.get_or_create(
            subject_name=subject, institute=institute["data"], defaults={
                "created_by": owner
            })

        if (created):
            return resp_success("Subject Created", {
                "data": SubjectSerialzier(subject).data
            })

        else:
            return resp_fail("Subject Already Exist", {}, 503)
    else:
        return resp_fail("Insitute Does Not Exist", {}, 502)


# Teacher
def get_assigned_subjects(teacher):
    """
    Gives the 'data' = subject access objects [list] of teacher
    and All The Different Institutes A Teacher Is Working In"""

    subjects_accs = SubjectAccess.objects.filter(teacher=teacher)
    if (subjects_accs.exists()):
        institutes = set(
            [subject.created_by.institute for subject in subjects_accs])

        return {
            'success': True,
            'data': subjects_accs,
            'institutes': institutes
        }

    return {
        "success": False,
        "data": []
    }


def has_subject_perm(subject, teacher):
    """
    Returns True if teacher has perm or access to subject
    otherwise False
    """
    if(subject.institute.owner == teacher):
        return True

    subject_accs = get_assigned_subjects(teacher=teacher)
    if (subject_accs["success"]):
        subjects = [subject_acc.subject for subject_acc in subject_accs['data']]
        if (subject in subjects):
            return True
        return False

    else:
        return False


# Institute (OWNER)
def get_teacher_requests(institute):
    """Gets all the requests sent by Teachers
     to Institute 

     Return TecherRequests Seriliazed Data"""
    teacher_requests = TeacherRequest.objects.filter(
        institute=institute, approved=False)

    class TeacherRequestSerializer(ModelSerializer):
        teacher = UserSerializer(many=False, read_only=True)

        class Meta:
            model = TeacherRequest
            fields = "__all__"

    # print(teacher_requests.all().values())  bro teacher ki id return krde teacher: {id: 16} me

    data = TeacherRequestSerializer(teacher_requests, many=True).data
    return data


def assign_subjects(teacher, subjects, grades, institute):
    """
        Checks Every Subject of Grade [nested loop] 
        for errors
        When Every Subject And Grade Is Valid

        returns True,Subject Access Data

    """

    # Get Error List
    errors = {

    }

    class SubjectAccSerializer(ModelSerializer):
        class Meta:
            model = SubjectAccess
            fields = ["subject", "grade"]
    # Validating Every Subject and Grade
    for grade in grades:
        # Looping Through all subject in grade
        for subject_name in subjects:
            subject = get_model(
                Subject, subject_name=subject_name, institute=institute)

            if (subject["exist"]):
                subject = subject["data"]
                subject_acc = SubjectAccSerializer(
                    data={"subject": subject.id, "grade": grade})

                if (subject_acc.is_valid()):
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
            # It will give nicely documented errors -x - close

    if (len(errors.keys()) != 0):
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


def get_teachers_data(institute):
    class TeacherSerializer(ModelSerializer):
        class Meta:
            model = User
            fields = "__all__"

    teacher_reqs = TeacherRequest.objects.filter(
        approved=True, institute=institute)

    teachers = [request_dict["teacher"]
                for request_dict in teacher_reqs.values('teacher')]

    if (len(teachers) == 0):
        return []

    teachers_data = TeacherSerializer(teachers, many=True).data

    return teachers_data
