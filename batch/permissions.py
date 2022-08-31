from rest_framework.permissions import BasePermission


class BatchCreatePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        role = request.user.role.lower()
        if(role == "owner"):
            return True

        if(role == "teacher"):
            data = request.data

            return True
