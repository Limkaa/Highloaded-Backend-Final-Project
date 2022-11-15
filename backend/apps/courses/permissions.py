from email import message
from rest_framework import permissions
from .models import Membership

import logging

logger = logging.getLogger(__name__)

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    message = "Only owner can perform this action"

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owner manage object.
    Assumes the model instance has an `owner` attribute.
    """
    message = "Only owner has access to that action"
    
    def has_object_permission(self, request, view, obj):
        is_owner = obj.owner == request.user
        if not is_owner:
            logger.warning(f'Not owner (user id {request.user.id}) tried to get access to object ({obj.__class__.__name__} with id {obj.id})')
        return is_owner


class IsCourseStudent(permissions.BasePermission):
    """ Object-level permission to only allow students see and work with course """
    message = "You can't perform this action"
    
    def has_object_permission(self, request, view, obj):
        is_student = Membership.objects.user_is_student_of(request.user, obj)
        if not is_student:
            logger.warning(f'Not student (user id {request.user.id}) tried to get access to course (course id {obj.id})')
        return is_student


class NotCourseStudentOrOwner(permissions.BasePermission):
    """ Object-level permission to only allow new people to register on course (not students) """
    message = "Students and teacher have no access to that action"
    
    def has_object_permission(self, request, view, obj):
        return not (Membership.objects.user_is_student_of(request.user, obj) or obj.owner == request.user)