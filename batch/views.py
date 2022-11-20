from argparse import Action
import re
from venv import create
from wsgiref.simple_server import demo_app
from rest_framework.viewsets import ModelViewSet
from accounts.models import Student, User
from accounts.utils import get_model, required_data, resp_fail, resp_success
from batch.serializers import BatchSerializer, StudentRequestSerializer
from batch.services import create_msg
from institute.models import Institute, Subject, TeacherRequest
# Create your views here.
from rest_framework.permissions import IsAuthenticated

from institute.services import has_subject_perm
from .permissions import BatchReadWritePermission, IsUserAuthenticated
from batch.models import Batch, Document, Message, StudentRequest
from rest_framework.response import Response
from rest_framework.decorators import action
from .services import get_batch_details

# Create your views here.


class BatchApi(ModelViewSet):
    permission_classes = [IsUserAuthenticated, BatchReadWritePermission]

    def get_queryset(self):
        user = self.request.user
        user_role = user.role.lower()

        if(user_role == "owner"):
            return Batch.objects.filter(institute__owner=user)
        elif (user_role == "teacher"):
            return Batch.objects.filter(teacher=user)
        elif user_role == "student":
            return user.batches.all()

    def create(self, request, *args, **kwargs):
        # Handling Request Data
        data = request.data
        success, req_data = required_data(
            data, ["batch_name", "batch_subject", "batch_code", "institute", "grade"])

        if(success):
            batch_name, batch_subject, batch_code, institute, grade = req_data
        else:
            errors = req_data

            return Response(resp_fail("Missing Arguments", {
                "errors": errors
            }, 502))

        # Checking Conditions and Errors
        institute = get_model(Institute, pk=int(institute))
        if(not institute["exist"]):
            return Response(resp_fail("Institute Does Not Exist", {}))

        institute = institute["data"]
        user = request.user

        if(user in institute.teachers.all() or user == institute.owner):
            pass
        else:
            return Response(resp_fail("You Do Not Belong To Institute", error_code=504))

        subject = get_model(Subject, institute=institute,
                            subject_name=batch_subject)

        if(not subject['exist']):
            return Response(resp_fail("Subject Does Not Exist", error_code=506))

        subject = subject['data']
        has_create_perm = has_subject_perm(
            subject=subject, teacher=request.user)

        if(has_create_perm):
            batch_exists = Batch.objects.filter(batch_code=batch_code).exists()

            if(batch_exists):
                return Response(resp_fail("Batch With This Batch Code Already Exists", {}, error_code=504))

            batch_form = BatchSerializer(
                data={
                    "batch_name": batch_name,
                    "batch_code": batch_code,
                    "grade": grade,
                    "batch_subject": subject.id,
                    "institute": institute.id,
                    "teacher": request.user.id
                }
            )

            if(batch_form.is_valid()):

                batch_form.save()
                return Response(resp_success("Batch Created Successfully",
                                             {
                                                 "batch": batch_form.data
                                             }))
            else:
                errors = batch_form.errors
                return Response(resp_fail("Invalid Batch Data", {
                    "errors": errors
                }))

        else:
            return Response(resp_fail("You Do Not Have Permission For This..", {
                'error_code': 506
            }))

    def retrieve(self, request, pk=None, *args, **kwargs):
        if(pk == None):
            return Response(resp_fail("No Batch Id provided"))

        queryset = self.get_queryset()
        if(queryset):
            batch_list = queryset.filter(pk=int(pk))
            if(batch_list.exists()):
                batch = batch_list.first()
            else:
                return Response(resp_fail("Batch Does Not Exist"))
        else:
            return Response(resp_fail("Do not have the permission"))

        data = get_batch_details(batch)

        return Response(resp_success("Batch Details Retrieved", data))

    @ action(methods=["GET", "POST"], detail=True, url_path="list_student_reqs")
    def list_student_reqs(self, request, pk=None, *args, **kwargs):
        batch_id = pk
        user = request.user
        if(batch_id == None):
            return Response(resp_fail("Batch ID Can't Be None"))

        batch = get_model(Batch, id=int(batch_id))
        if(not batch["exist"]):
            return Response(resp_fail("Batch Does Not Exist With This ID"))

        batch = batch["data"]

        if(batch.teacher == user or batch.institute.owner == user):
            student_requests = StudentRequest.objects.filter(batch=batch)
            data = StudentRequestSerializer(student_requests, many=True).data

            return Response(resp_success("Fetched All Requestss", data))
        else:
            return Response(resp_fail("You Are Not Authorized"))

    @ action(methods=["POST"], detail=False, url_path="accept_student")
    def accept_student_request(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        success, req_data = required_data(data, ["student_request_id"])
        if(not success):
            errors = req_data
            return Response(resp_fail("Missing Arguments", errors))

        request_id, = req_data
        std_request = get_model(StudentRequest, id=int(request_id))
        if(not std_request["exist"]):
            return Response(resp_fail("There Is No Student Request With This ID"))

        std_request = std_request["data"]
        batch_teacher = std_request.batch.teacher

        if(batch_teacher == user):
            batch = std_request.batch
            student = std_request.student

            std_request.approved = True
            std_request.save()

            if(student in batch.students.all()):
                return Response(resp_success("Already Added To Batch"))
            else:
                batch.students.add(student)
                batch.save()

                return Response(resp_success("Added To Batch"))

        else:
            return Response(resp_fail("You are not authorized to approve request"))

    @ action(methods=["POST"], detail=True, url_path="remove_student")
    def remove_student(self, request, pk=None, *args, **kwargs):
        batch_id = pk
        user = request.user
        if(batch_id == None):
            return Response(resp_fail("Batch ID Can't Be None"))

        batch = get_model(Batch, id=int(batch_id))
        if(not batch["exist"]):
            return Response(resp_fail("Batch Does Not Exist With This ID"))
        batch = batch['data']

        data = request.data
        success, req_data = required_data(data, ["student_id"])
        if(not success):
            errors = req_data
            return Response(resp_fail("Missing Arguments", errors))

        student_id, = req_data
        student = get_model(User, id=int(student_id))
        if(not student["exist"]):
            return Response(resp_fail("There Is No Student With This ID"))
        student = student["data"]

        if(batch.teacher == user or batch.institute.owner == user):
            if (student in batch.students.all()):
                # Delete All Student Requests
                StudentRequest.objects.filter(
                    student=student, batch=batch).delete()
                batch.students.remove(student)
            else:
                return Response(resp_fail("Student Does Not Belong To This Batch"))
        else:
            return Response(resp_fail("You Are Not Authorized To Remove The Student"))

    @ action(methods=["GET"], detail=False, url_path="list_batches")
    def list_batches(self, request, pk=None, *args, **kwargs):
        role = self.request.user.role
        user = request.user

        batches = None
        if(role.lower() == "student"):
            batches = Batch.objects.filter(students__in=[user])
        elif(role.lower() == "teacher"):
            batches = Batch.objects.filter(teacher=user)
        elif(role.lower() == "owner"):
            batches = Batch.objects.filter(institute__owner=user)
        else:
            return Response(resp_fail('You do not have valid role.'))

        data = BatchSerializer(batches, many=True).data
        response = resp_success("Batches Retrieved", data)
        return Response(response)


class MessageAPI(ModelViewSet):
    permission_classes = [IsUserAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(sender=user)

    def create(self, request, *args, **kwargs):
        data = request.data
        success, req_data = required_data(data, ["message", "reciever"])

        if(not success):
            errors = req_data

            return resp_fail("Missing Arguments", {
                "errors": errors
            }, 801)

        message, reciever = req_data
        resp = create_msg(request, message, reciever)

        if(not resp["success"]):
            error = resp["error"]
            return Response(resp_fail(error, resp, 802))

        return Response(resp_success(
            "Message Sent Successfully", resp
        ))

    @ action(methods=['POST'], detail=False, url_path="send_msg_batch")
    def send_msg_batch(self, request, *args, **kwargs):
        data = request.data

        success, req_data = required_data(data, ["message", "batch"])

        if(not success):
            errors = req_data

            return resp_fail("Missing Arguments", {
                "errors": errors
            }, 811)

        message, batch_id = req_data
        resp = create_batch_msg(request, message, batch_id)


class DocumentAPI(ModelViewSet):
    permission_classes = [IsUserAuthenticated]

    def get_queryset(self):
        user = self.request.user
        user_role = user.role.lower()
        teacher = user_role == "teacher"
        owner = user_role == "owner"
        student = user_role == "student"

        if(owner):
            return Document.objects.filter(batch__institute__owner=user)
        elif (teacher):
            return Document.objects.filter(batch__teacher=user)
        elif(student):
            return Document.objects.filter(batch__students__in=[user])

    def list(self, request, *args, **kwargs):
        params = request.query_params
        limit = params.get("limit", 10)

        queryset = self.get_queryset()
