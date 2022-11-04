from django.urls import path
from rest_framework.routers import DefaultRouter
from batch.views import BatchApi, MessageAPI, DocumentAPI

router = DefaultRouter(trailing_slash=True)

# Owner Specific
router.register("batch", BatchApi, basename="batch_api")
router.register("document", DocumentAPI, basename="document_api")
router.register("message", MessageAPI, basename="message_api")


urlpatterns = router.urls
