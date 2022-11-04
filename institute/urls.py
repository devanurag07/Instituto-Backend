from django.urls import path
from rest_framework.routers import DefaultRouter
from institute.views import InstituteApi, SubjectApi

router = DefaultRouter(trailing_slash=True)

# Owner Specific
router.register("subject", SubjectApi, basename="subject_api")
router.register("institute", InstituteApi, basename="institute_api")

urlpatterns = router.urls
