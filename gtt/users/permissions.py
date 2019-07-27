from rest_framework.permissions import BasePermission

class IsSuperuser(BasePermission):
    def has_permission(self, request, view):
        print(request.user.is_superuser)
        return request.user.is_superuser