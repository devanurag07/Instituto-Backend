from rest_framework.viewsets import ModelViewSet, ViewSet
from accounts.utils import get_model, required_data, resp_fail, resp_success
from institute.models import Institute, Subject, TeacherRequest
from institute.permissions import IsOwner
from institute.services import create_subject, get_insitute, get_teacher_requests, assign_subjects, get_teachers_data
# Create your views here.
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from accounts.models import User
from accounts.utils import get_model


# Owner
class SubjectApi(ModelViewSet):

    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        queryset = Subject.objects.filter(owner=self.request.user)
        return queryset

    # Create Subject

    def create(self, request, *args, **kwargs):
        data = request.data
        success, req_data = required_data(data, ["subject"])

        if (not success):
            errors = req_data
            return Response(resp_fail("Missing Arguments", {
                "errors": errors
            }, 501))

        subject, = req_data  # (subject,)
        resp = create_subject(subject=subject, owner=request.user)

        return Response(resp)

    # Assign Subjects or Approving Teacher Request
    @action(methods=["POST"], detail=False, url_path="assign_subjects")
    def assign_subjects(self, request, *args, **kwargs):
        data = request.data
        success, req_data = required_data(
            data, ["teacher_id", "subjects", "grades"])

        if (not success):
            return Response(resp_fail("Missing Required Data", {
                "errors": req_data
            }, error_code=601))

        # Getting Data From req
        teacher_id, subjects, grades = req_data

        # Check Teacher Existence
        teacher = get_model(User, pk=int(teacher_id),
                            role="teacher".capitalize())
        if (not teacher["exist"]):
            return Response(resp_fail("Teacher Does Not exist", {}, error_code=602))
        teacher = teacher["data"]
        #*#

        # Check Institute Existence
        institute = get_insitute(request.user)
        if (not institute["exist"]):
            return Response(resp_fail("Institute Does Not exist", {}, error_code=603))
        institute = institute["data"]

        # Check Teacher Request Existence
        teacher_request = get_model(
            TeacherRequest, institute=institute, teacher=teacher)
        if (not teacher_request["exist"]):
            # return no perm to assign subjects
            return Response(resp_fail("Teacher Request Does Not exist", {}, error_code=604))

        # SUCCESS=bool,DATA
        assigned, data = assign_subjects(teacher=teacher,
                                         subjects=subjects, grades=grades, institute=institute)

        if (not assigned):
            return Response(resp_fail("Invalid Data", {"errors": data["errors"]}))

        teacher_request = teacher_request["data"]
        teacher_request.approved = True
        teacher_request.save()

        return Response(resp_success(
            "Subject Access Provided Successfully", {
                "subject_accs": data
            }), 201)


class InstituteApi(ViewSet):
    permission_classes = [IsAuthenticated, IsOwner]

    @action(methods=["GET"], detail=False, url_path="teacher_requests")
    def get_teacher_requests(self, request, *args, **kwargs):
        user = request.user
        institute = get_model(Institute, owner=user)

        if (not institute["exist"]):
            return Response(resp_fail("Your Account isn't created properly", error_code=4001))

        institute = institute["data"]

        teacher_reqs_data = get_teacher_requests(institute)

        return Response(resp_success("Teacher Request Fetched", {
            "data": teacher_reqs_data
        }))

    # GET Teachers
    @action(methods=["GET"], detail=False, url_path="teacher")
    def get_teachers(self, request, *args, **kwargs):
        user = request.user
        institute = get_model(Institute, owner=user)
        if (not institute["exist"]):
            return Response(resp_fail("Your Account isn't created properly", error_code=4001))

        institute = institute["data"]

        teachers_data = get_teachers_data(institute=institute)
        return teachers_data
