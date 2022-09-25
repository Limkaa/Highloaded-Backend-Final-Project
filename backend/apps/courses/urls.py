from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import views

general_feed_router = DefaultRouter()
general_feed_router.register('', views.CoursesViewSet, basename='courses')

course_router = DefaultRouter()
course_router.register(r'lessons', views.LessonsViewSet, basename='lessons')
course_router.register(r'lessons/(?P<lesson_pk>\d+)/comments', views.LessonCommentsViewSet, basename='comments')
course_router.register(r'lessons/(?P<lesson_pk>\d+)/tasks', views.TasksViewSet, basename='tasks')
course_router.register(r'news', views.CourseNewsViewSet, basename='news')
course_router.register(r'reviews', views.CourseReviewsViewSet, basename='reviews')

urlpatterns = [
    # General course feed
    path('', include(general_feed_router.urls)),
    
    # Categories of courses
    path('categories', views.CategoriesListAPIView.as_view()),
    path('categories/<int:pk>', views.CategoryRetrieveAPIView.as_view()),
    
    # Teachers of courses
    path('teachers', views.TeachersListView.as_view()),
    path('teachers/<int:pk>', views.TeacherDetailView.as_view()),
    
    # More information about specific course
    path('<int:course_pk>/', include(course_router.urls)),
    path('<int:course_pk>/lessons/bookmarks', views.BookmarksViewSet.as_view({'get': 'list'})),
    path('<int:course_pk>/lessons/<int:pk>/bookmark', views.BookmarksViewSet.as_view({'post': 'create', 'delete': 'destroy'})),
]