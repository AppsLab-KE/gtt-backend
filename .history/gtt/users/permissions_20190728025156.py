from rest_framework.permissions import BasePermission

class IsSuperuser(BasePermission):
    message = 'You do not have permission to perform this action.'
    
    def has_permission(self, request, view):
        return request.user.is_superuser