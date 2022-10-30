from rest_framework.permissions import BasePermission
from rest_framework import permissions


class BatchReadWritePermission(BasePermission):
    def has_permission(self, request, view):

        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            user = request.user
            role = user.role.lower()

            if(role == "owner" or role == "teacher"):
                return True


class IsUserAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return (bool(request.user and request.user.is_authenticated) and
                request.user.is_created)
