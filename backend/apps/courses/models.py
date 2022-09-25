from django.db import models
from .managers import (
    BookmarksManager,
    MembershipsManager,
    CoursesManager,
    ReviewsManager,
    TasksManager
)

from project.settings import AUTH_USER_MODEL
from .utils import courseCoverFilePath

class Category(models.Model):
    title = models.CharField(unique=True, max_length=100, null=False, blank=False)
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    
    def __str__(self) -> str:
        return self.title


class Course(models.Model):
    owner = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='own_courses')
    title = models.CharField(max_length=300, null=False, blank=False)
    description = models.CharField(max_length=2000, null=False, blank=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    cover_photo = models.ImageField(upload_to=courseCoverFilePath, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CoursesManager()
    
    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
    
    def save(self, *args, **kwargs) -> None:
        try:
            this = Course.objects.get(id=self.id)
            if this.cover_photo:
                this.cover_photo.delete()
        except:
            pass
        super(Course, self).save(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.title


class Membership(models.Model):
    """ Many to Many relationship between Course and User """
    owner = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memberships')
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='students')
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = MembershipsManager()

    class Meta:
        verbose_name = 'Course membership'
        verbose_name_plural = 'Memberships of courses'
        unique_together = ('owner', 'course')

    def __str__(self) -> str:
        return str(self.course)


class Lesson(models.Model):
    """ Each course have some lessons """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=300, null=False, blank=False)
    description = models.CharField(max_length=2000, null=False, blank=False)
    videolink = models.URLField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
    
    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    """ User can write comment to lessons """
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='comments')
    owner = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='comments_to_lessons')
    text = models.CharField(max_length=500, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
    
    def __str__(self) -> str:
        return self.text


class Task(models.Model):
    """ Each lesson also can include some tasks """
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=300, null=False, blank=False)
    description = models.CharField(max_length=2000, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TasksManager()

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self) -> str:
        return self.title


class Review(models.Model):
    """ User can write course review and put it's rating """
    GREAT = 5
    GOOD = 4
    NORMAL = 3
    BAD = 2
    AWFUL = 1
    
    RATING_CHOICES = [
        (GREAT, 'Great'),
        (GOOD, 'Good'),
        (NORMAL, 'Normal'),
        (BAD, 'Bad'),
        (AWFUL, 'Awful'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    owner = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='reviews_of_courses')
    text = models.CharField(max_length=500, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.SmallIntegerField(choices=RATING_CHOICES, default=GREAT)
    
    objects = ReviewsManager()
    
    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ('course', 'owner')
    
    def __str__(self) -> str:
        return self.text


class Bookmark(models.Model):
    """ 
    User can manage bookmarks of lessons.
    Uses Many to Many relationship between User and Lesson. 
    """
    owner = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='bookmarked_by')
    
    objects = BookmarksManager()
    
    class Meta:
        verbose_name = 'Bookmark'
        verbose_name_plural = 'Bookmarks'
        unique_together = ('owner', 'lesson')
    
    def __str__(self) -> str:
        return str(self.lesson)


class News(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='news')
    title = models.CharField(max_length=150, null=False, blank=False)
    text = models.CharField(max_length=2000, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'News'
        verbose_name_plural = 'News'
    
    def __str__(self) -> str:
        return self.title