from rest_framework.permissions import BasePermission


class BatchCreatePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        role = user.role.lower()
        if(role == "owner"):
            return True

        if(role == "teacher"):
            return True


class IsUserAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return (bool(request.user and request.user.is_authenticated) and
                request.user.is_created)
