from rest_framework.viewsets import ModelViewSet
from accounts.utils import get_model, required_data, resp_fail
from institute.models import Institute, Subject, TeacherRequest
# Create your views here.
from rest_framework.permissions import IsAuthenticated

from institute.services import has_subject_perm
from .permissions import BatchCreatePermission
from batch.models import Batch

# Create your views here.


class BatchApi(ModelViewSet):
    permission_classes = [IsAuthenticated, BatchCreatePermission]

    def create(self, request, *args, **kwargs):
        data = request.data
        success, req_data = required_data(
            data, ["batch_name", "batch_subject", "batch_code", "institute", "grade"])

        if(success):
            batch_name, batch_subject, batch_code, institute, grade = req_data
        else:
            errors = req_data

            return resp_fail("Missing Arguments", {
                "errors": errors
            }, 502)

        institute = get_model(Institute, pk=int(institute))

        if(not institute["exist"]):
            pass
        institute = institute["data"]

        teacher_request = get_model(
            TeacherRequest, institute=institute, teacher=request.user)

        if(not teacher_request["exist"]):
            pass

        teacher_request = teacher_request['data']
        if(not teacher_request.approved):
            pass

        subject = Subject.objects.filter(
            institute=institute, subject=batch_subject)

        has_create_perm = has_subject_perm(subject=subject)

        if(has_create_perm):
            Batch.objects.create()
        else:
            pass
