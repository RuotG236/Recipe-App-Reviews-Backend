from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object
        # Handle different models
        if hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit, but everyone can read.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to admin users
        return request.user and request.user.is_staff