from ast import Sub
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from accounts.utils import required_data, resp_fail, resp_success
from institute.models import Institute, Subject
from institute.permissions import IsOwner
from institute.services import create_subject, get_insitute
# Create your views here.
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import SubjectSerialzier


# Owner
class SubjectApi(ModelViewSet):
    # serializer_class=
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        queryset = Subject.objects.filter(owner=self.request.user)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data

        req_data = required_data(data, ["subject"])

        has_errors = not req_data[0]

        if(has_errors):
            errors = req_data[1]

            return resp_fail("Missing Arguments", {
                "errors": errors
            }, 501)

        subject, = req_data[1]

        resp = create_subject(subject=subject, owner=request.user)

        return Response(resp)


class BatchApi(ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwner]

    def create(self, request, *args, **kwargs):
        data = request.data
        success, req_data = required_data(
            data, ["batch_name", "batch_subject", "batch_code", "grade"])

        if(success):
            batch_name, batch_subject, batch_code, grade = req_data
        else:
            errors = req_data

            return resp_fail("Missing Arguments", {
                "errors": errors
            }, 502)
