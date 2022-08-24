from tkinter.messagebox import RETRY
from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):

    def has_permission(self, request, view):
        return request.user.role.lower() == "owner"
