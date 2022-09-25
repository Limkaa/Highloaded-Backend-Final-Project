from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.db import models

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

from apps.accounts.serializers import ProfileSerializer
from .validators import validate_cover_size, validate_youtube_link, validate_cover_type

class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = ('id', 'title')
        read_only_fields = ('id', 'title')
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['courses_count'] = instance.courses.count()
        return rep
    
    def create(self, validated_data):
        """ Category is created in admin panel"""
        pass

    def update(self, instance, validated_data):
        """ Category is updated in admin panel"""
        pass


class BaseInformationSerializer(serializers.Serializer):
    """ Base serializer of information for Course, Lesson, Task models"""
    
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=300, required=True)
    description = serializers.CharField(max_length=2000, required=True, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class CourseGeneralFeedSerializer(BaseInformationSerializer):
    cover_photo = serializers.ImageField(required=False, validators=[validate_cover_size, validate_cover_type])
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['students_count'] = instance.students.count()
        rep['reviews_count'] = instance.reviews.count()
        rating_average = instance.reviews.aggregate(models.Avg('rating')).get('rating__avg')
        rep['rating_average'] = float("{:.2f}".format(rating_average)) if rating_average else None
        return rep


class CategoryCoursesListSerializer(CategorySerializer):
    courses = CourseGeneralFeedSerializer(read_only=True, many=True)
    
    class Meta(CategorySerializer.Meta):
        fields = CategorySerializer.Meta.fields + ('courses',)


class CourseDetailSerializer(CourseGeneralFeedSerializer):
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    category = CategorySerializer(read_only=True)
    owner = ProfileSerializer(source='owner.profile', read_only=True)
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['students_count'] = instance.students.count()
        return rep
    
    def create(self, validated_data):
        course = Course.objects.create(
            owner = self.context['request'].user, 
            **validated_data)
        return course
    
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.category_id = validated_data.get('category_id', instance.category_id)
        instance.cover_photo = validated_data.get('cover_photo', instance.cover_photo)
        
        instance.save()
        return instance


class LearningCourseListSerializer(serializers.Serializer):
    course = CourseGeneralFeedSerializer(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)


class TeachersListSerializer(ProfileSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['courses_total'] = instance.user.own_courses.count()
        return rep


class TeacherDetailSerializer(TeachersListSerializer):
    courses = CourseGeneralFeedSerializer(source='user.own_courses', many=True)


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ('id', 'owner', 'lesson')
        read_only_fields = ('id', 'lesson')
        extra_kwargs = {
            'owner': {
                'write_only': True
            }
        }


class LessonSerializer(BaseInformationSerializer):
    videolink = serializers.URLField(required=False, validators=[validate_youtube_link])
    tasks = BaseInformationSerializer(read_only=True, many=True)
    
    def create(self, validated_data):
        course = Lesson.objects.create(
            course_id = self.context['course_id'], 
            **validated_data)
        return course
    
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.videolink = validated_data.get('videolink', instance.videolink)
        instance.save()
        return instance


class MembershipSerializer(serializers.ModelSerializer):
    course = CourseGeneralFeedSerializer(read_only=True)
    
    class Meta:
        model = Membership
        fields = ('id', 'owner', 'course', 'date_joined')
        read_only_fields = ('id', 'date_joined')
        extra_kwargs = {
            'owner': {
                'write_only': True
            }
        }


class CourseStudentsSerializer(serializers.ModelSerializer):
    student = ProfileSerializer(source='owner.profile', read_only=True)
    
    class Meta:
        model = Membership
        fields = ('id', 'student', 'date_joined')
        read_only_fields = ('id', 'date_joined')


class ReviewSerializer(serializers.ModelSerializer):
    owner = ProfileSerializer(source='owner.profile', read_only=True)
    rating = serializers.IntegerField(min_value=1, max_value=5)
    
    class Meta:
        model = Review
        fields = ('id', 'rating', 'text', 'created_at', 'owner')
        read_only_fields = ('id', 'created_at')
        extra_kwargs = {
            'rating': {
                'required': True
            }
        }

    def create(self, validated_data):
        review = Review.objects.get_or_create(
            course_id = self.context['course_id'],
            owner = self.context['request'].user,
            **validated_data
        )
        return review


class CommentSerializer(serializers.ModelSerializer):
    owner = ProfileSerializer(source='owner.profile', read_only=True)
    
    class Meta:
        model = Comment
        fields = ('id', 'text', 'owner', 'created_at')
        read_only = ('id', 'created_at')
    
    def create(self, validated_data):
        comment = Comment.objects.create(
            lesson_id = self.context['lesson_id'],
            owner = self.context['request'].user,
            **validated_data
        )
        return comment


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        extra_kwargs = {
            'lesson': {
                'required': False
            }
        }


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ('id', 'title', 'text', 'created_at')
        read_only = ('id', 'created')