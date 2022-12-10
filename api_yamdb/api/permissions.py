from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class IsAdmin(permissions.BasePermission):
    allowed_user_roles = ('admin',)

    def has_permission(self, request, view):
        return request.user.is_superuser or (request.user.is_authenticated
                                             and request.user.is_admin)


class IsAnonim(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsUser(permissions.BasePermission):
    allowed_user_roles = ('user', )

    def has_permission(self, request, view):
        request.user.role in self.allowed_user_roles


class IsModerator(permissions.BasePermission):
    allowed_user_roles = ('moderator', )

    def has_permission(self, request, view):
        request.user.role in self.allowed_user_roles


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        obj.author == request.user


class IsAdminUserOrReadOnly(permissions.BasePermission):
    # def has_permission(self, request, view):
    #    return request.method in
    #    permissions.SAFE_METHODS or request.user.is_staff
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.is_admin
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated and (
                    request.user.is_admin or request.user.is_superuser)))


class IsAdminModeratorOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin
                or request.user.is_moderator
                or obj.author == request.user)

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)
