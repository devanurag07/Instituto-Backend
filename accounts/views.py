from argparse import Action
from ast import Delete
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
from accounts.models import Institute, OtpTempData, Student, StudentRequest, User
from accounts.utils import get_role
from .serializers import UserSerializer


class Auth(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # Step - 2
    #Verify and Create
    def create(self, request, *args, **kwargs):

        # Verify Otp
        data = request.data
        mobile = data.get("mobile", None)
        otp = data.get("otp", None)
        role = data.get("role", None)

        if((not role) or (not otp) or (not mobile)):
            return Response({
                "success": False,
                "data": {

                },
                "message": "Something Wrong...",
                "error_code": "304"
            })

        otp_exists = OtpTempData.objects.filter(mobile=int(mobile)).exists()

        if(otp_exists):
            otp_temp = OtpTempData.objects.filter(mobile=int(mobile)).first()

            if(otp_temp.otp == otp):

                gen_password = ''.join(random.choices(string.ascii_uppercase +
                                                      string.digits, k=8))

                user = User(first_name=otp_temp.first_name,
                            last_name=otp_temp.last_name,
                            mobile=otp_temp.mobile,
                            password=gen_password,
                            default_type=get_role(role),
                            is_verified=True)

                user.save()

                refresh_token = RefreshToken.for_user(user)
                return Response({
                    "success": True,
                    "data": {
                        "token": str(refresh_token.access_token),
                        "refresh": str(refresh_token)
                    },
                    "message": "OTP Verified Successfully.",
                })

            else:

                otp_temp.attempts += 1
                otp_temp.save()
                attempts_left = 5-otp_temp.attempts

                if(attempts_left == 0):
                    otp_temp.delete()

                    return Response({
                        "success": False,
                        "data": {

                        },
                        "message": "OTP Attempts Exhausted.Try Resend.",
                        "error_code": "303"
                    })

                else:

                    return Response({
                        "success": False,
                        "data": {

                        },
                        "message": "Wrong OTP Input...",
                        "error_code": "302"
                    })

        else:
            pass

    # Step 1 -
    @action(methods=['post'], detail="false", url_path="send_otp")
    def send_otp(self, request):
        otp = random.randint(10000, 99999)
        user_data = self.serializer_class(request.data)

        # Handle Data Validation
        if(user_data.is_valid()):
            validated_data = user_data.validated_data

            mobile = validated_data.get("mobile", None)

            already_exist = User.objects.filter(mobile=mobile).exists()

            if(already_exist):
                user = User.objects.filter(mobile=mobile).first()

                if(user.is_verified and user.is_created):
                    return Response({
                        "success": False,
                        "data": {

                        },
                        "message": "Account Already Exist...",
                        "error_code": "301"
                    })

                else:
                    user.delete()

            otp_temp = OtpTempData.objects.update_or_create(
                otp=otp,
                **validated_data,
                attempts=0
            )

            otp_temp.save()

            return Response(
                {
                    "success": True,
                    "data": {
                        "otp": otp
                    },
                    "message": "OTP Sent Successfully..."
                }
            )

        else:
            # handle Error
            pass


# after user created -- profile creation - institute creation - request creation
class AuthPost(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        user = request.user
        user_role = user.role

        if(user_role == "Student"):
            data = request.data

            institute_code = data.get("insitute_code", None)
            batches = data.get("batches", None)

            if(not (institute_code and batches)):

                pass

            institute_list = Institute.objects.filter(
                institute_code=institute_code)

            if(institute_list.exists()):
                institute = institute_list.first()

            student_request = StudentRequest(student=request.user)

            for batch_name in batches:
                batch_list = institute.batches.objects.filter(
                    batch_name=batch_name)

                if(batch_list.exists()):
                    batch = batch_list.first()
                    student_request.batches.add(batch)

            student_request.save()

        elif user_role == "Teacher":
            pass

        elif(user_role == 'Owner'):
            pass
