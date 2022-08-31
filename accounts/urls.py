from email.mime import base
from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter

from institute.views import SubjectApi
from .views import *

router = DefaultRouter(trailing_slash=True)
router.register("auth", Auth)
router.register("initial", AuthPost)
router.register("common", AuthCommon, basename="auth_common")

# Owner Specific
router.register("subject", SubjectApi, basename="subject_api")

urlpatterns = router.urls
