from rest_framework.permissions import BasePermission

class CanCreatePost(BasePermission):
    def has_permission(self, request, view)

class CanCreateComment(BasePermission):

class CanCreateReply(BasePermission):

class CanCreateBookmark(BasePermission):