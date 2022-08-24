from argparse import Action
from ast import Delete
from curses import initscr
from distutils.file_util import move_file
from distutils.log import error
from email.policy import default
from operator import eq
from webbrowser import get
from wsgiref import validate
from django.shortcuts import render
import random
import string


# Create your views here.
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated


# Custom
from accounts.models import Batch, Institute, LoginOtp, OtpTempData, Student, StudentRequest, Teacher, TeacherRequest, User
from accounts.utils import get_role, required_data, resp_fail, resp_success, user_created
from .serializers import UserSerializer


class Auth(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # Step - 2
    # Verify and Create
    def create(self, request, *args, **kwargs):

        # Verify Otp
        data = request.data
        mobile = data.get("mobile", None)
        otp = data.get("otp", None)
        role = data.get("role", None)

        req_data = required_data(data, ["mobile", "otp", "role"])
        has_errors = not req_data[0]

        if (has_errors):
            errors = req_data[1]

            return Response(resp_fail("Required Parameters Missing (User) ", {
                "errors": errors,
            }, error_code=301))

        otp_exists = OtpTempData.objects.filter(mobile=int(mobile)).exists()

        if (otp_exists):
            otp_temp = OtpTempData.objects.filter(mobile=int(mobile)).first()

            attempts_left = 5-otp_temp.attempts
            if (attempts_left == 0):
                otp_temp.delete()

                return Response(resp_fail("OTP Attempts Exhausted.Try Resend.", error_code=311))

            if (otp_temp.otp == otp):

                gen_password = ''.join(random.choices(string.ascii_uppercase +
                                                      string.digits, k=8))

                user = User(first_name=otp_temp.first_name,
                            last_name=otp_temp.last_name,
                            mobile=otp_temp.mobile,
                            password=gen_password,
                            is_verified=True)

                user.default_type = get_role(role)
                user.save()

                refresh_token = RefreshToken.for_user(user)

                return Response(resp_success("OTP Verified Successfully.", {
                    "token": str(refresh_token.access_token),
                    "refresh": str(refresh_token)
                },))

            else:

                otp_temp.attempts += 1
                otp_temp.save()

                return Response(resp_fail("Wrong OTP Input...", error_code=302))

        else:
            return resp_fail("No OTP Exists.", {}, 304)

    # Step 1 -
    @action(methods=['POST'], detail=False, url_path="send_otp")
    def send_otp(self, request):

        otp = random.randint(1000, 9999)
        user_data = self.serializer_class(data=request.data)

        # Handle Data Validation
        is_valid = user_data.is_valid()

        if (is_valid):
            validated_data = user_data.validated_data

            mobile = validated_data.get("mobile", None)
            already_exist = User.objects.filter(mobile=mobile).exists()

            if (already_exist):
                user = User.objects.filter(mobile=mobile).first()

                if (user.is_verified and user.is_created):
                    return Response({
                        "success": False,
                        "data": {

                        },
                        "message": "Account Already Exist...",
                        "error_code": "301"
                    })

                else:
                    institute_exist = Institute.objects.filter(
                        user=request.user).exists()

                    request_exist = TeacherRequest.objects.filter(
                        teacher=request.user).exists() or StudentRequest.objects.filter(student=request.user)

                    batch_exist = Batch.objects.filter(
                        teacher__id=request.user.id).exists()

                    if (institute_exist or request_exist or batch_exist):
                        return Response(resp_fail("Can't Create Your Account.", {}, 305))
                    else:
                        user.delete()

            OtpTempData.objects.filter(mobile=mobile).delete()
            otp_temp = OtpTempData(
                otp=otp,
                **validated_data,
                attempts=0
            )

            otp_temp.save()

            return Response(
                {
                    "success": True,
                    "data": {
                        "otp": otp_temp.otp
                    },
                    "message": "OTP Sent Successfully..."
                }
            )

        else:
            # handle Error
            errors = user_data.errors
            return Response(resp_fail("Invalid or Missing User Data", {
                "errors": errors,

            }, 303))

    @action(methods=['POST'], detail=False, url_path="get_login_otp")
    def get_login_otp(self, request):

        otp = random.randint(1000, 9999)
        data = request.data
        req_data = required_data(data, ["mobile"])

        has_errors = not req_data[0]

        if (has_errors):
            errors = req_data[1]
            return Response(resp_fail("Required Params Missing (User-Login)", {"errors": errors}, 401))

        else:
            mobile, = req_data[1]

        LoginOtp.objects.filter(mobile=mobile).delete()
        login_otp = LoginOtp(
            otp=otp,
            mobile=mobile,
            attempts=0
        )

        login_otp.save()

        return Response(resp_success('OTP Sent Successfully', {
            "otp": otp
        }))

    @action(methods=['POST'], detail=False, url_path="login_otp_verify")
    def login_verify(self, request):
        data = request.data
        req_data = required_data(data, ["mobile", "otp"])

        has_errors = not req_data[0]
        if (has_errors):
            errors = req_data[1]
            return Response(resp_fail("Required Params Missing (User-Login)", {"errors": errors}, 401))

        else:
            mobile, otp = req_data[1]

        user_list = User.objects.filter(mobile=mobile)

        if (not user_list.exists()):
            return Response(resp_fail("No User Found With This Mobile"))

        user = user_list.first()

        otp_list = LoginOtp.objects.filter(mobile=mobile)

        if (otp_list.exists()):
            login_otp = otp_list.first()

            attempts_left = 5-login_otp.attempts
            if (attempts_left == 0):
                login_otp.delete()
                return Response(resp_fail("OTP Attempts Exhausted.Try Resend.", error_code=403))

            if (login_otp.otp == int(otp)):

                LoginOtp.objects.filter(mobile=mobile).delete()

                # Generating Token
                refresh_token = RefreshToken.for_user(user)

                return Response(resp_success("OTP Verified Successfully", {
                    "token": str(refresh_token.access_token),
                    "refresh": str(refresh_token)
                }))

            else:
                login_otp.attempts += 1
                login_otp.save()
                attempts_left = 5-login_otp.attempts
                return Response(resp_fail(f"Wrong Otp {attempts_left} Attempts Left", error_code=404))

        else:
            return Response(resp_fail("No OTP Found", {}, 402))


# after user created -- profile creation - institute creation - request creation
class AuthPost(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request):
        print('\n', 'request data', request.data, '\n')
        user = request.user
        user_role = user.role

        if (user_role == "Student"):
            data = request.data

            req_data = required_data(data, ['insitute_code', 'batches'])
            errors = not req_data[0]

            if (errors):
                error_msgs = req_data[1]

                return Response(resp_fail("Required Parameters Missing .. (Student)", {
                    "errors": error_msgs
                }))

            else:
                institute_code, batches = req_data[1]

            institute_list = Institute.objects.filter(
                institute_code=institute_code)

            if (institute_list.exists()):
                institute = institute_list.first()

            # student_request = StudentRequest(student=request.user)

            for batch_name in batches:
                batch_list = institute.batches.objects.filter(
                    batch_name=batch_name)

                if (batch_list.exists()):
                    batch = batch_list.first()
                    StudentRequest.objects.get_or_create(
                        student=request.user, batch=batch)

            user_created(request.user)
            return Response(resp_success("Request Created", {}))

        elif user_role == "Teacher":
            data = request.data

            req_data = required_data(request.data, ["institute_code"])

            if (req_data[0]):
                #  ->  req_data=[..args]
                institute_code = req_data[1][0]
            else:
                # ->  req_data={field:error}

                errors = req_data[1]

                resp = resp_fail("Institute Code Not Provided (Teacher)", {
                    "errors": errors
                }, 306)

                return Response(resp)

            institute_list = Institute.objects.filter(
                institute_code=institute_code)

            if (institute_list.exists()):
                # Getting Institute FROM list - list.first() -> list[0]
                institute = institute_list.first()
            else:
                return Response(resp_fail("Institute Not Found", {}, 307))

            teacher_request, created = TeacherRequest.objects.get_or_create(
                teacher=request.user)

            if (created):

                user_created(request.user)
                return Response(resp_success("Teacher Request Sent...", {}))
            else:
                user_created(request.user)
                return Response(resp_fail("Request Already There...", {}, 308))

        elif (user_role == 'Owner'):

            data = request.data

            req_data = required_data(
                data, ["institute_code", "institute_name", "institute_desc", "max_students"])

            errors = not req_data[0]

            if (errors):
                errors = req_data[1]

                return Response(resp_fail("Required Parameters Missing (Owner)", {
                    "errors": errors,
                }, 309))

            else:
                institute_code, institute_name, institute_desc, max_students = req_data[1]

                institute_exists = Institute.objects.filter(owner=request.user)

                if (institute_exists):
                    return Response(resp_fail("You can't create institute...", {}, error_code=310))

                institute = Institute(institute_code=institute_code, institute_name=institute_name,
                                      institute_desc=institute_desc, max_students=max_students)

                institute.save()

                user_created(request.user)
                return Response(resp_success("Institute Created", {}))
