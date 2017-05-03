from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import BasePermission


class IsManager(BasePermission):
    def has_permission(self, request, view):
        if not request.user == AnonymousUser():
            return request.user.is_manager
