from django.contrib.auth.base_user import BaseUserManager
from accounts.roles import Roles
from accounts.utils import _validate_mobile
from django.contrib.auth.hashers import make_password
from django.db import models


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, mobile, password, **extra_fields):
        if(not mobile):
            raise ValueError("Invalid Mobile Number...")

        # Extra Fields
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user = self.model(mobile=mobile, password=password, **extra_fields)
        user.save(using=self._db)

        return user


class StudentManager(BaseUserManager):

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=Roles.STUDENT)


class OwnerManager(BaseUserManager):

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=Roles.OWNER)


class TeacherManager(BaseUserManager):

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=Roles.TEACHER)
