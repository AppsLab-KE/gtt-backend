from rest_framework.permissions import BasePermission

class IsSuperuser(BasePermission):
    message = 'You do not have permission to perform this action.'

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        else:
            False