from django.urls import path
from rest_framework.routers import DefaultRouter

from institute.views import InstituteApi, SubjectApi
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import *

router = DefaultRouter(trailing_slash=True)
router.register("auth", Auth)
router.register("initial", AuthPost)
router.register("common", AuthCommon, basename="auth_common")


# Owner Specific

router.register("subject", SubjectApi, basename="subject_api")
router.register("institute", InstituteApi, basename="institute_api")

urlpatterns = router.urls

urlpatterns += [
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]
