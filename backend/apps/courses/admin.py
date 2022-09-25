from django.contrib import admin

from .models import (
    Category,
    Course,
    Membership,
    Lesson,
    Task,
    Comment,
    Review,
    Bookmark,
    News
)

# Register your models here.
admin.site.register(Category)
admin.site.register(News)
admin.site.register(Course)
admin.site.register(Membership)
admin.site.register(Lesson)
admin.site.register(Task)
admin.site.register(Comment)
admin.site.register(Review)
admin.site.register(Bookmark)