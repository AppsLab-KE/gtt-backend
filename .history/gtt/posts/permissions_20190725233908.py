from rest_framework.permissions import BasePermission

class CanCreatePost(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('add_post')

class CanCreateComment(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('add_comment')

class CanCreateReply(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('add_reply')

class CanCreateBookmark(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('add_bookmark')