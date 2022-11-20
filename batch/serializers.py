from dataclasses import field, fields
from tkinter.tix import Tree
from accounts.models import User
from batch.models import Batch, Document, DocumentFile, Message, StudentRequest
from rest_framework.serializers import ModelSerializer
from accounts.serializers import UserSerializer
from rest_framework import serializers


class BatchSerializer(ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()

    def get_subject_name(self, instance):
        return instance.subject.subject_name

    def get_teacher_name(self, instance):
        return instance.teacher.first_name + " " + instance.teacher.last_name

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
