from argparse import Action
from venv import create
from wsgiref.simple_server import demo_app
from rest_framework.viewsets import ModelViewSet
from accounts.utils import get_model, required_data, resp_fail, resp_success
from batch.serializers import BatchSerializer
from batch.services import create_batch_msg, create_msg
from institute.models import Institute, Subject, TeacherRequest
# Create your views here.
from rest_framework.permissions import IsAuthenticated

from institute.services import has_subject_perm
from .permissions import BatchCreatePermission, IsUserAuthenticated
from batch.models import Batch, Message
from rest_framework.response import Response
from rest_framework.decorators import action
# Create your views here.


class BatchApi(ModelViewSet):
    permission_classes = [IsUserAuthenticated, BatchCreatePermission]

    def create(self, request, *args, **kwargs):
        # Handling Request Data
        data = request.data
        success, req_data = required_data(
            data, ["batch_name", "batch_subject", "batch_code", "institute", "grade"])

        if (success):
            batch_name, batch_subject, batch_code, institute, grade = req_data
        else:
            errors = req_data

            return resp_fail("Missing Arguments", {
                "errors": errors
            }, 502)

        # Checking Conditions and Errors
        institute = get_model(Institute, pk=int(institute))
        if (not institute["exist"]):
            return Response(resp_fail("Institute Does Not Exist", {}))

        institute = institute["data"]

        teacher_request = get_model(
            TeacherRequest, institute=institute, teacher=request.user)
        if (not teacher_request["exist"]):
            return Response(resp_fail("You Do Not Belong To Institute", error_code=504))

        teacher_request = teacher_request['data']

        if (not teacher_request.approved):
            return Response(resp_fail("You are not allowed to create batch", data={}, error_code=505))

        subject = get_model(Subject, institute=institute,
                            subject=batch_subject)
        if (not subject['exist']):
            return Response(resp_fail("Subject Does Not Exist", error_code=506))

        subject = subject['data']
        has_create_perm = has_subject_perm(subject=subject)

        if (has_create_perm):
            batch_exists = Batch.objects.filter(batch_code).exists()

            if (batch_exists):
                return Response(resp_fail("Batch With This Batch Code Already Exists", {}, error_code=504))

            batch_form = BatchSerializer(
                data={
                    "batch_name": batch_name,
                    "batch_code": batch_code,
                    "grade": grade,
                    "batch_subject": subject.id,
                    "institute": institute.id,
                    "teacher": request.user
                }
            )

            if (batch_form.is_valid()):

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


class MessageAPI(ModelViewSet):
    permission_classes = [IsUserAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(sender=user)

    def create(self, request, *args, **kwargs):
        data = request.data
        success, req_data = required_data(data, ["message", "reciever"])

        if (not success):
            errors = req_data

            return resp_fail("Missing Arguments", {
                "errors": errors
            }, 801)

        message, reciever = req_data
        resp = create_msg(request, message, reciever)

        if (not resp["success"]):
            error = resp["error"]
            return Response(resp_fail(error, resp, 802))

        return Response(resp_success(
            "Message Sent Successfully", resp
        ))

    @action(methods=['POST'], detail=False, url_path="send_msg_batch")
    def send_msg_batch(self, request, *args, **kwargs):
        data = request.data

        success, req_data = required_data(data, ["message", "batch"])

        if (not success):
            errors = req_data

            return resp_fail("Missing Arguments", {
                "errors": errors
            }, 811)

        message, batch_id = req_data
        resp = create_batch_msg(request, message, batch_id)
