from rest_framework import permissions

from django.contrib.auth import get_user_model


User = get_user_model()


class IsAdmin(permissions.BasePermission):
    allowed_user_roles = ('admin', )

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.role in self.allowed_user_roles:
                return True
        return False


class IsAnonim(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS 


class IsUser(permissions.BasePermission):
    allowed_user_roles = ('user', )

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.role in self.allowed_user_roles:
                return True
        return False


class IsModerator(permissions.BasePermission):
    allowed_user_roles = ('moderator', )
    
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.role in self.allowed_user_roles:
                return True
        return False


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return obj.author == request.user
        else:
            return False


class IsAdminUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user.is_staff
