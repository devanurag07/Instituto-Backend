from accounts.models import Owner, User
from ..accounts.utils import resp_fail, resp_success
from .models import Institute, Subject
from .serializers import SubjectSerialzier
resp_success
resp_fail


def get_insitute(owner):
    institute_list = Institute.objects.filter(owner=owner)
    if(institute_list.exists()):
        return True, institute_list.first()

    return False, None


def create_subject(subject, owner):

    institute_exist, institute = get_insitute(owner=owner)

    if(institute_exist):
        subject, created = Subject.objects.get_or_create(
            subject_name=subject, institute=institute)

        if(created):
            return resp_success("Subject Created", {
                "data": SubjectSerialzier(subject).data
            })

        else:
            return resp_fail("Subject Already Exist", {}, 503)
    else:
        return resp_fail("Insitute Does Not Exist", {}, 502)
