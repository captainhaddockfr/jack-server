from rest_framework import permissions

class PostOrIsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method=='POST' or (request.method=='GET' and request.user.is_authenticated)


    def has_object_permission(self, request, view, obj):
        return True