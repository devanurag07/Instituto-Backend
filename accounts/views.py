import random
import string


# Create your views here.
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated


# Custom
from accounts.models import LoginOtp, OtpTempData, User
from accounts.services import create_institute
from accounts.utils import get_model, get_role, required_data, resp_fail, resp_success, set_email, update_profile, user_created, user_exists
from .serializers import UserSerializer
from institute.models import Institute, StudentProfile, TeacherRequest
from institute.serializers import SubjectSerialzier
from batch.models import StudentRequest, Batch, Subject
from batch.serializers import BatchSerializer
from django.core import serializers


class Auth(ViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # Step - 2
    # Verify and Create
    @action(methods=['POST'], detail=False, url_path="signup_otp_verify")
    def signup_otp_verify(self, request, *args, **kwargs):

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

        if (user_exists(mobile=int(mobile))):
            return Response(resp_fail("User Already Exists...", {}, 302))

        otp_exists = OtpTempData.objects.filter(mobile=int(mobile)).exists()

        if (otp_exists):
            otp_temp = OtpTempData.objects.filter(mobile=int(mobile)).first()

            attempts_left = 5-otp_temp.attempts
            if (attempts_left == 0):
                otp_temp.delete()

                return Response(resp_fail("OTP Attempts Exhausted.Try Resend.", error_code=303))

            if (otp_temp.otp == int(otp)):

                gen_password = ''.join(random.choices(string.ascii_uppercase +
                                                      string.digits, k=8))

                user = User(first_name=otp_temp.first_name,
                            last_name=otp_temp.last_name,
                            mobile=otp_temp.mobile,
                            password=gen_password,
                            is_verified=True)

                user.default_type = get_role(role)
                user.save()

                user_data = UserSerializer(user).data

                refresh_token = RefreshToken.for_user(user)

                return Response(resp_success("OTP Verified Successfully.", {
                    "token": str(refresh_token.access_token),
                    "refresh": str(refresh_token),
                    "user": user_data
                },))

            else:

                otp_temp.attempts += 1
                otp_temp.save()

                return Response(resp_fail("Wrong OTP Input...", error_code=304))

        else:
            return Response(resp_fail("No OTP Exists.", {}, 305))

    # Step 1 -
    @action(methods=['POST'], detail=False, url_path="get_signup_otp")
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
                    return Response(resp_fail("User Already Exists ", error_code=401))

                else:

                    institute_exist = Institute.objects.filter(
                        user=request.user).exists()

                    request_exist = TeacherRequest.objects.filter(
                        teacher=request.user).exists() or StudentRequest.objects.filter(student=request.user)

                    batch_exist = Batch.objects.filter(
                        teacher__id=request.user.id).exists()

                    if (institute_exist or request_exist or batch_exist):
                        return Response(resp_fail("Can't Create Your Account.", {}, 402))
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

            }, 403))

    @action(methods=['POST'], detail=False, url_path="get_login_otp")
    def get_login_otp(self, request):

        otp = random.randint(1000, 9999)
        data = request.data
        req_data = required_data(data, ["mobile"])

        has_errors = not req_data[0]

        if (has_errors):
            errors = req_data[1]
            return Response(resp_fail("Required Params Missing (User-Login)", {"errors": errors}, 501))

        else:
            mobile, = req_data[1]

        user_list = User.objects.filter(mobile=mobile)
        if (not user_list.exists()):
            return Response(resp_fail("No User Found With This Mobile", error_code=502))

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
            return Response(resp_fail("Required Params Missing (User-Login)", {"errors": errors}, 601))

        else:
            mobile, otp = req_data[1]

        user_list = User.objects.filter(mobile=mobile)

        if (not user_list.exists()):
            return Response(resp_fail("No User Found With This Mobile", error_code=602))

        user = user_list.first()

        otp_list = LoginOtp.objects.filter(mobile=mobile)

        if (otp_list.exists()):
            login_otp = otp_list.first()

            attempts_left = 5-login_otp.attempts
            if (attempts_left == 0):
                login_otp.delete()
                return Response(resp_fail("OTP Attempts Exhausted.Try Resend.", error_code=603))

            if (login_otp.otp == int(otp)):

                LoginOtp.objects.filter(mobile=mobile).delete()

                # Generating Token
                refresh_token = RefreshToken.for_user(user)
                user_data = UserSerializer(user).data
                print(user.institute)

                return Response(resp_success("OTP Verified Successfully", {
                    "token": str(refresh_token.access_token),
                    "refresh": str(refresh_token),
                    "user": user_data

                }))

            else:
                login_otp.attempts += 1
                login_otp.save()
                attempts_left = 5-login_otp.attempts
                return Response(resp_fail(f"Wrong Otp {attempts_left} Attempts Left", error_code=605))

        else:
            return Response(resp_fail("No OTP Found", {}, 604))


# after user created -- profile creation - institute creation - request creation
class AuthPost(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request):

        user = request.user
        user_role = user.role

        # common fields

        req_fields_dict = {
            "student": ['insitute_code', 'batches', "father_name", "mother_name"],
            "teacher": ["institute_code", "about_me", "email"],
            "owner": ["institute_code", "institute_name", "institute_desc",
                      "max_students", "email", "about_me", "location"]

        }

        data = request.data
        # "user.role.lower() => student,owner,teacher"
        success, req_data = required_data(
            data, req_fields_dict[user.role.lower()])

        # Setting Gender
        gender = data.get("gender", None)
        extra_errors = {}
        if (gender == None):
            extra_errors = {
                "gender": "Gender Required"
            }
        elif (not (gender in ["male", "female", "other"])):
            extra_errors = {
                "gender": "Invalid Gender Value"
            }

        if (not success):
            errors = req_data
            errors.update(extra_errors)

            return Response(resp_fail(f"Required Parameters Missing ({user.role.upper()})", {
                "errors": errors,
            }, 309))

        elif len(extra_errors.keys()) != 0:
            return Response(resp_fail(f"Required Parameters Missing ({user.role.upper()})", {
                "errors": extra_errors,
            }, 310))

        user.gender = gender
        user.save()

        if (user_role == "Student"):

            institute_code, batches, father_name, mother_name = req_data

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

            # Updating Profile
            profile, created = StudentProfile.objects.get_or_create(
                user=request.user)
            profile.father_name = father_name
            profile.mother_name = mother_name
            profile.save()

            user_created(request.user)

            return Response(resp_success("Request Created", {}))

        elif user_role == "Teacher":

            institute_code, about_me, email = req_data

            institute_list = Institute.objects.filter(
                institute_code=institute_code)

            if (institute_list.exists()):
                # Getting Institute FROM list - list.first() -> list[0]
                institute = institute_list.first()
            else:
                return Response(resp_fail("Institute Not Found", {}, 307))

            # Updating Profile Data
            update_profile(user, data={
                "about_me": about_me
            })
            email_set, errors = set_email(user, email)
            if (not email_set):
                return Response(resp_fail("Invalid Email", {
                    "errors": errors
                }, error_code=801))

            teacher_request, created = TeacherRequest.objects.get_or_create(
                teacher=request.user, defaults={
                    "institute": institute
                })

            if (created):

                user_created(request.user)

                return Response(resp_success("Teacher Request Sent...", {}))

            else:
                # Set User Created True
                user_created(request.user)
                return Response(resp_fail("Request Already There...", {}, 308))

        elif (user_role == 'Owner'):
            institute_code, institute_name, institute_desc, max_students, email, about_me, location = req_data

            institute_exists = Institute.objects.filter(
                owner=request.user).exists()
            if (institute_exists):
                return Response(resp_fail("You can't create institute...", {}, error_code=310))

            # Updating Profile Data
            update_profile(user, data={
                "location": location,
                "about_me": about_me
            })

            email_set, errors = set_email(user, email)
            if (not email_set):
                return Response(resp_fail("Invalid Email", {
                    "errors": errors
                }, error_code=801))

            institute = create_institute({
                "institute_code": institute_code,
                "institute_name": institute_name,
                "institute_desc": institute_desc,
                "max_students": max_students
            }, owner=request.user)

            if (institute["created"]):

                user_created(request.user)

                return Response(resp_success("Institute Created"))

            else:

                errors = institute["errors"]
                return Response(resp_fail("Invalid Arguments", data={
                    "errors": errors
                }, error_code=323))


class AuthCommon(ViewSet):

    permission_classes = [IsAuthenticated]

    @action(methods=["POST"], detail=False, url_path="get_institute_subjects")
    def get_subjects(self, request):
        data = request.data
        success, req_data = required_data(data, ["institute_code"])

        if (success):
            institute_code, = req_data
        else:
            errors = req_data
            return Response(resp_fail("Missing Arguments", {
                "errors": errors
            }, 403))

        institute = get_model(
            Institute, institute_code=institute_code)

        if (not institute["exist"]):
            return Response(resp_fail("Institute Does Not Exists", {}, error_code=404))

        institute = institute["data"]
        subjects = Subject.objects.filter(institute=institute)
        serialized = SubjectSerialzier(subjects, many=True)

        return Response(resp_success("Institute Subjects Fetched", {
            "subjects": serialized.data}))

    @action(methods=["POST"], detail=False, url_path="get_institute_batches")
    def get_batches(self, request):
        data = request.data
        success, req_data = required_data(
            data, ["institute_code", "subjects", "grade"])

        if (success):
            print('somethin')
            institute_code, subjects, grade = req_data
        else:
            errors = req_data
            return Response(resp_fail("Missing Arguments", {
                "errors": errors
            }, 403))

        institute = get_model(
            Institute, institute_code=institute_code)

        if (not institute["exist"]):
            return Response(resp_fail("Institute Does Not Exists", {}, error_code=404))

        institute = institute["data"]

        batches = Batch.objects.filter(
            institute=institute, batch_subject__subject_name__in=subjects, grade=grade)
        return Response(resp_success("Batches Fetched Successfully", {
            "batches": BatchSerializer(batches, many=True).data
        }))
