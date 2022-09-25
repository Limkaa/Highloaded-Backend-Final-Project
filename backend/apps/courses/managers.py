from calendar import c
from django.db import models
from django.db.models import Count, Avg


class MembershipsManager(models.Manager):
    def courses_learned_by(self, user):
        """ Returns all courses, which user is learning """
        return self.filter(owner=user).select_related('course')
    
    def user_is_student_of(self, user, course):
        return self.filter(owner=user, course=course).exists()


class CoursesManager(models.Manager):
    def with_statistics(self):
        """ Returns reviews statistics for each course """
        return self.annotate(reviews_num=Count('reviews'), rating=Avg('reviews__rating')).order_by('-id')
    
    def teached_by(self, user):
        """ Returns courses, which are owned by user (with reviews statistics) """
        return self.with_statistics().filter(owner=user)


class BookmarksManager(models.Manager):
    def of_user_in_course(self, user, course):
        return self.filter(owner=user, lesson__course=course)
    
    def of_lesson(self, user, lesson):
        return self.filter(owner=user, lesson=lesson).first()


class TasksManager(models.Manager):
    def of_course(self, course):
        return self.filter(lesson__course_id = course)


class ReviewsManager(models.Manager):
    def of_user_for_course(self, user, course):
        return self.filter(owner=user, course_id=course).first()