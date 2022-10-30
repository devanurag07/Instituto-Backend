from dataclasses import field, fields
from tkinter.tix import Tree
from accounts.models import User
from batch.models import Batch, Document, DocumentFile, Message, StudentRequest
from rest_framework.serializers import ModelSerializer
from accounts.serializers import UserSerializer


class BatchSerializer(ModelSerializer):
    class Meta:
        model = Batch
        fields = "__all__"


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"


class StudentRequestSerializer(ModelSerializer):
    student_data = UserSerializer(many=False, read_only=True)

    class Meta:
        model = StudentRequest
        fields = "__all__"


class FileSerializer(ModelSerializer):

    class Meta:
        model = DocumentFile
        fields = "__all__"


class DocumentSerializer(ModelSerializer):
    files = FileSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = "__all__"
