from django.http import Http404
from rest_framework.response import Response
from rest_framework import status, generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from apps.accounts.models import Profile

from .permissions import IsOwnerOrReadOnly, IsCourseStudent, IsOwner, NotCourseStudentOrOwner

from .models import (
    Category,
    Course,
    Lesson,
    Membership,
    Task,
    Comment,
    Review,
    Bookmark,
    News
)

from .serializers import (
    BookmarkSerializer,
    CategoryCoursesListSerializer,
    CategorySerializer,
    BaseInformationSerializer,
    CommentSerializer,
    CourseGeneralFeedSerializer,
    CourseDetailSerializer,
    CourseStudentsSerializer,
    LearningCourseListSerializer,
    LessonSerializer,
    MembershipSerializer,
    ReviewSerializer,
    TaskSerializer,
    TeacherDetailSerializer,
    TeachersListSerializer,
    NewsSerializer
)

import logging

logger = logging.getLogger(__name__)


# Works
class CategoriesListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None


# Works
class CategoryRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryCoursesListSerializer
    permission_classes = [AllowAny]


# Works
class TeachersListView(generics.ListAPIView):
    queryset = Profile.objects.teachers()
    serializer_class = TeachersListSerializer
    permission_classes = [AllowAny]


# Works
class TeacherDetailView(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = TeacherDetailSerializer
    permission_classes = [AllowAny]


# Works
class CoursesViewSet(viewsets.ViewSet):
    
    def get_permissions(self):
        if self.action in ['learn']:
            permission_classes = (NotCourseStudentOrOwner,)
        elif self.action in ['students']:
            permission_classes = (IsOwner,)
        else:
            permission_classes = (IsOwnerOrReadOnly,)
        return [permission() for permission in permission_classes] 
    
    def get_object(self):
        return Course.objects.filter(id=self.kwargs.get('pk')).first()
    
    def list(self, request):
        courses = Course.objects.all()
        serializer = CourseGeneralFeedSerializer(courses, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = CourseDetailSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            logger.info('New course created')
            return Response(serializer.data)
        logger.warning('Invalid info for course create')
        return Response(serializer.errors)
    
    def retrieve(self, request, pk=None):
        course = self.get_object()
        if course:
            serializer = CourseDetailSerializer(instance=course)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    def update(self, request, pk=None):
        course = self.get_object()
        if course:
            self.check_object_permissions(request, course)
            serializer = CourseDetailSerializer(instance=course, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                logger.info('Course info updated')
                return Response(serializer.data)
            logger.warning('Invalid info for course update')
            return Response(serializer.errors)
        logger.error('Course not found')
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def learning(self, request):
        courses = Membership.objects.courses_learned_by(request.user)
        serializer = LearningCourseListSerializer(courses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def teaching(self, request):
        courses = Course.objects.teached_by(request.user)
        serializer = CourseGeneralFeedSerializer(courses, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def learn(self, request, pk=None):
        course=self.get_object()
        if course:
            self.check_object_permissions(request, course)
            membership, created = Membership.objects.get_or_create(owner=request.user, course=course)
            serializer = MembershipSerializer(membership)
            logger.info('New membership created')
            return Response(serializer.data)
        logger.error('Course not found')
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        course=self.get_object()
        if course:
            self.check_object_permissions(request, course)
            serializer = CourseStudentsSerializer(course.students, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)


# Works
class LessonsViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action in ['retrieve', 'bookmarks']:
            permission_classes = (IsCourseStudent | IsOwner,)
        elif self.action in ['create', 'update', 'destroy']:
            permission_classes = (IsOwner, )
        else:
            permission_classes = (AllowAny, )
        return [permission() for permission in permission_classes]
    
    def get_object(self, *args, **kwargs):
        course_id = kwargs.get('course_pk', None)
        lesson_id = kwargs.get('pk', None)
        if lesson_id:
            return Lesson.objects.filter(id=lesson_id, course_id=course_id).first()
        return Course.objects.filter(id=course_id).first()
    
    def list(self, request, *args, **kwargs):
        course = self.get_object(**kwargs)
        if course:
            serializer = BaseInformationSerializer(course.lessons, many=True)
            return Response(serializer.data)
        logger.warning(f'Lesson not found')
        return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        course = self.get_object(**kwargs)
        if course:
            self.check_object_permissions(request, course)
            serializer = LessonSerializer(data=request.data, context={'course_id': course.id})
            if serializer.is_valid():
                serializer.save()
                logger.info(f'Lesson created')
                return Response(serializer.data)
            logger.warning(f'Invalid data for lesson create')
            return Response(serializer.errors)
        logger.error(f'Lesson not found')
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    def retrieve(self, request, *args, **kwargs):
        lesson = self.get_object(**kwargs)
        if lesson:
            self.check_object_permissions(request, lesson.course)
            serializer = LessonSerializer(instance=lesson)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    def update(self, request, *args, **kwargs):
        lesson = self.get_object(**kwargs)
        if lesson:
            self.check_object_permissions(request, lesson.course)
            serializer = LessonSerializer(instance=lesson, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                logger.info(f'Lesson updated')
                return Response(serializer.data)
            logger.warning(f'Invalid data for lesson update')
            return Response(serializer.errors)
        logger.error(f'Lesson not found')
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    def destroy(self, request, *args, **kwargs):
        lesson = self.get_object(**kwargs)
        if lesson:
            self.check_object_permissions(request, lesson.course)
            lesson.delete()
            return Response({"message": "Lesson deleted"}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


# Works (for SIS)
class BookmarksViewSet(viewsets.ViewSet):
    permission_classes = [IsCourseStudent | IsOwner]
    
    def get_object(self, *args, **kwargs):
        course_id = kwargs.get('course_pk', None)
        lesson_id = kwargs.get('pk', None)
        if lesson_id:
            return Lesson.objects.filter(id=lesson_id, course_id=course_id).first()
        return Course.objects.filter(id=course_id).first()
    
    def list(self, request, *args, **kwargs):
        course = self.get_object(**kwargs)
        if course:
            self.check_object_permissions(request, course)
            bookmarks = Bookmark.objects.of_user_in_course(user=request.user, course=course)
            serializer = BookmarkSerializer(bookmarks, many=True)
            return Response(serializer.data)
        return Response({"message": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request, *args, **kwargs):
        lesson = self.get_object(**kwargs)
        if lesson:
            self.check_object_permissions(request, lesson.course)
            bookmark, created = Bookmark.objects.get_or_create(owner=request.user, lesson=lesson)
            serializer = BookmarkSerializer(bookmark)
            logger.info(f'Bookmark created')
            return Response(serializer.data)
        return Response({"message": "Course or lesson not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def destroy(self, request, *args, **kwargs):
        lesson = self.get_object(**kwargs)
        if lesson:
            self.check_object_permissions(request, lesson.course)
            bookmark = Bookmark.objects.of_lesson(user=request.user, lesson=lesson)
            if bookmark:
                bookmark.delete()
                logger.info(f'Bookmark deleted')
                return Response({"message": "Bookmark deleted"}, status=status.HTTP_200_OK)
            logger.warning(f'Bookmark not found')
            return Response({"message": "Bookmark not found"}, status=status.HTTP_404_NOT_FOUND)
        logger.error(f'Lesson not found')
        return Response({"message": "Lesson not found"}, status=status.HTTP_404_NOT_FOUND)


# Works (for SIS)
class TasksViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    
    def get_permissions(self):
        if self.action in ['retrieve', 'list']:
            permission_classes = (IsCourseStudent | IsOwner,)
        else:
            permission_classes = (IsOwner, )
        return [permission() for permission in permission_classes]
    
    def get_object(self):
        object = self.get_queryset().filter(id=self.kwargs.get('pk')).first()
        if object:
            return object
        raise Http404
    
    def get_lesson(self):
        course_id = self.kwargs.get('course_pk')
        lesson_id = self.kwargs.get('lesson_pk')
        lesson = Lesson.objects.filter(id=lesson_id, course_id=course_id).first()
        if lesson:
            self.check_object_permissions(self.request, lesson.course)
            return lesson
        raise Http404
    
    def get_queryset(self):
        lesson = self.get_lesson()
        return Task.objects.filter(lesson_id=lesson.id)
    
    def create(self, request, *args, **kwargs):
        lesson = self.get_lesson()
        self.check_object_permissions(request, lesson.course)
        
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(lesson=lesson)
            logger.info('New task created')
            return Response(serializer.data)
        logger.warning('Invalid info for task create')
        return Response(serializer.errors)


# Works (for SIS)
class CourseNewsViewSet(viewsets.ModelViewSet):
    serializer_class = NewsSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    
    def get_object(self, *args, **kwargs):
        news_id = self.kwargs.get('pk', None)
        news = self.get_queryset().filter(id=news_id).first()
        if news: 
            self.check_object_permissions(self.request, news.course)
            return news
        raise Http404
    
    def get_queryset(self):
        course = Course.objects.get(id=self.kwargs.get('course_pk', None))
        news = News.objects.filter(course=course)
        return news
    
    def create(self, request, *args, **kwargs):
        course = Course.objects.filter(id=self.kwargs.get('course_pk')).first()
        self.check_object_permissions(request, course)
        serializer = NewsSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(course=course)
            logger.info('New course news created')
            return Response(serializer.data)
        logger.error('Invalid info for news create')
        return Response(serializer.errors)


# Works (for SIS)
class CourseReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    
    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = (IsCourseStudent,)
        elif self.action in ['update', 'destroy', 'partial-update']:
            permission_classes = (IsOwner,)
        else:
            permission_classes = (AllowAny, )
        return [permission() for permission in permission_classes]
    
    def get_course(self):
        course = Course.objects.filter(id=self.kwargs.get('course_pk')).first()
        if course:
            return course
        raise Http404    
    
    def get_object(self):
        review = self.get_queryset().filter(id=self.kwargs.get('pk')).first()
        if review:
            self.check_object_permissions(self.request, review)
            return review
        raise Http404
    
    def get_queryset(self):
        course = self.get_course()
        return Review.objects.filter(course=course)
    
    def create(self, request, *args, **kwargs):
        course = self.get_course()
        review = Review.objects.of_user_for_course(request.user, course.id)
        
        if not review:
            self.check_object_permissions(request, course)
            serializer = ReviewSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(owner=request.user, course=course)
                return Response(serializer.data)
            return Response(serializer.errors)
        
        serializer = ReviewSerializer(review)
        return Response(
            {
                "message": "Review already exists from you", 
                "review": serializer.data
            }, 
            status=status.HTTP_403_FORBIDDEN
        )


# Works (for SIS)
class LessonCommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'destroy']:
            permission_classes = (IsOwner,)
        else:
            permission_classes = (IsCourseStudent | IsOwner,)
        return [permission() for permission in permission_classes]
    
    def get_object(self):
        comment = self.get_lesson().comments.filter(id=self.kwargs.get('pk')).first()
        if comment:
            self.check_object_permissions(self.request, comment)
            return comment
        raise Http404
    
    def get_lesson(self):
        course_id = self.kwargs.get('course_pk')
        lesson_id = self.kwargs.get('lesson_pk')
        lesson = Lesson.objects.filter(id=lesson_id, course_id=course_id).first()
        if lesson:
            return lesson
        raise Http404
    
    def get_queryset(self):
        lesson = self.get_lesson()
        self.check_object_permissions(self.request, lesson.course)
        return Comment.objects.filter(lesson_id=lesson.id)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['lesson_id'] = self.kwargs.get('lesson_pk')
        return context
    
    def create(self, request, *args, **kwargs):
        lesson = self.get_queryset().first().lesson
        if lesson:
            self.check_object_permissions(request, lesson.course)
            serializer = CommentSerializer(data=request.data, context=self.get_serializer_context())
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors)
        raise Http404()
