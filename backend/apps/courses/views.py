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


class CategoriesListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None


class CategoryRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryCoursesListSerializer
    permission_classes = [AllowAny]


class TeachersListView(generics.ListAPIView):
    queryset = Profile.objects.teachers()
    serializer_class = TeachersListSerializer
    permission_classes = [AllowAny]


class TeacherDetailView(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = TeacherDetailSerializer
    permission_classes = [AllowAny]


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
                logger.info(f'Lesson created')
                return Response(serializer.data)
            logger.warning(f'Invalid data for lesson create')
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


class BookmarksViewSet(viewsets.ViewSet):
    permission_classes = (IsCourseStudent | IsOwner,)
    
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


class TasksViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = (IsOwner,)
    
    def get_permissions(self):
        if self.action in ['retrieve', 'list']:
            permission_classes = (IsCourseStudent | IsOwner,)
        else:
            permission_classes = (IsOwner, )
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        lesson = Lesson.objects.filter(
            id=self.kwargs.get('lesson_pk'),
            course_id=self.kwargs.get('course_pk')).first()
        if lesson:
            self.check_object_permissions(self.request, lesson.course)
            serializer.save(lesson=lesson)
        raise Http404
    
    def get_queryset(self):
        lesson = Lesson.objects.filter(
            id=self.kwargs.get('lesson_pk'),
            course_id=self.kwargs.get('course_pk')).first()
        if lesson:
            self.check_object_permissions(self.request, lesson.course)
            return Task.objects.filter(lesson=lesson)
        raise Http404


class CourseNewsViewSet(viewsets.ModelViewSet):
    serializer_class = NewsSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    
    def perform_create(self, serializer):
        serializer.save(course_id=self.kwargs.get('course_pk'))
    
    def get_queryset(self):
        return News.objects.filter(course_id=self.kwargs.get('course_pk'))
    
    def create(self, request, *args, **kwargs):
        course = Course.objects.filter(id=self.kwargs.get('course_pk')).first()
        self.check_object_permissions(request, course)
        serializer = NewsSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            logger.info('New course news created')
            return Response(serializer.data)
        logger.error('Invalid info for news create')
        return Response(serializer.errors)


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
    
    def get_object(self):
        object = self.get_queryset().filter(id=self.kwargs.get('pk')).first()
        if object:
            return object
        raise Http404()
    
    def get_queryset(self):
        return Review.objects.filter(course__id=self.kwargs.get('course_pk'))
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['course_id'] = self.kwargs.get('course_pk')
        return context
    
    def create(self, request, *args, **kwargs):
        review = Review.objects.of_user_for_course(self.request.user, self.kwargs.get('course_pk'))
        if not review:
            serializer = ReviewSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                logger.info('New review created')
                return Response(serializer.data)
            logger.warning('Invalid info for review create')
            return Response(serializer.errors)
        logger.error('Review not found')
        return Response(status=status.HTTP_404_NOT_FOUND)


class LessonCommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'destroy', 'partial-update']:
            permission_classes = (IsOwner,)
        else:
            permission_classes = (IsCourseStudent | IsOwner,)
        return [permission() for permission in permission_classes]
    
    def get_object(self):
        object = self.get_queryset().filter(id=self.kwargs.get('pk')).first()
        if object:
            return object
        raise Http404
    
    def get_queryset(self):
        lesson = Lesson.objects.filter(
            id=self.kwargs.get('lesson_pk'),
            course_id=self.kwargs.get('course_pk')).first()
        
        if not lesson:
            raise Http404
        
        return lesson.comments.all()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['lesson_id'] = self.kwargs.get('lesson_id')
        return context
    
    def create(self, request, *args, **kwargs):
        course = Course.objects.filter(id=self.kwargs.get('course_pk')).first()
        if course:
            serializer = CommentSerializer(data=request.data, context=self.get_serializer_context())
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                logger.info('New comment created')
                return Response(serializer.data)
            logger.warning('Invalid data for comment create')
            return Response(serializer.errors)
        logger.error('Course not found')
        raise Http404()
