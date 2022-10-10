import json
import random

from django.core.management.base import BaseCommand
from apps.courses.models import (
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

from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Fills new database with mock data'

    def _create_superuser(self):
        return User.objects.create_superuser(email="admin@gmail.com", password="admin")

    def _create_categories(self, categories):
        categories_objects = []
        for index, category in enumerate(categories):
            categories_objects.append(Category(title=category))
        
        if categories_objects:
            Category.objects.bulk_create(categories_objects)
            self.stdout.write(self.style.SUCCESS('Categories successfully created'))

        return categories_objects
    
    def _create_courses(self, courses):
        while True:
            try:
                courses_num = int(input('\nCourse number to generate (1-100): '))
                if not (courses_num <= 100 and courses_num > 0):
                    self.stdout.write(self.style.ERROR('Course number must be from 1 to 100'))
                    continue
                break
            except:
                self.stdout.write(self.style.ERROR('Course number must be integer'))
        
        courses_objects = []
        for index, course in enumerate(random.sample(courses, courses_num)):
            courses_objects.append(Course(
                title=course.get('title'),
                description=course.get('description'),
                owner=random.choice(self.users),
                category=random.choice(self.categories)
                )
            )
        
        if courses_objects:
            Course.objects.bulk_create(courses_objects)
            self.stdout.write(self.style.SUCCESS('Courses successfully created'))

        return courses_objects
    
    def _create_lessons(self, lessons):
        lessons_objects = []
        for course in self.courses:
            lessons_num = random.randint(0, 30)
            course_lessons = random.sample(lessons, lessons_num)
            for lesson in course_lessons:
                lesson_url_kwarg = "".join(random.sample('ABCDEFGHIJKLMPabcdefghjklmp', 10))
                videolink = f'https://youtu.be/{lesson_url_kwarg}'
                lessons_objects.append(Lesson(
                    course=course, 
                    title=lesson.get('title'),
                    description=lesson.get('description'), 
                    videolink=videolink))
        
        if lessons_objects:
            Lesson.objects.bulk_create(lessons_objects)
            self.stdout.write(self.style.SUCCESS('Lessons successfully created'))

        return lessons_objects
    
    def _create_bookmarks(self):
        bookmarks_objects = []
        for course in self.courses:
            memberships = [membership for membership in self.memberships if membership.course == course]
            lessons = [lesson for lesson in self.lessons if lesson.course == course]

            for membership in random.sample(memberships, random.randint(len(memberships)*0,2, len(memberships))):
                bookmarks_num = random.randint(0, len(lessons))
                lessons_to_bookmark = random.sample(lessons, bookmarks_num)

                for lesson in lessons_to_bookmark:
                    bookmarks_objects.append(Bookmark(
                        lesson=lesson, 
                        owner=membership.owner))
        
        if bookmarks_objects:
            Bookmark.objects.bulk_create(bookmarks_objects)
            self.stdout.write(self.style.SUCCESS('Bookmarks successfully created'))

        return bookmarks_objects
    
    def _create_course_news(self, news):
        news_objects = []
        for course in self.courses:
            news_num = random.randint(0, 5)
            course_news = random.sample(news, news_num)
            for article in course_news:
                news_objects.append(News.objects.create(
                    course=course, 
                    title=article.get('title'),
                    text=article.get('description')))
        
        if news_objects:
            self.stdout.write(self.style.SUCCESS('News successfully created'))

        return news_objects
    
    def _create_comments(self, comments):
        comments_objects = []
        for course in self.courses:
            memberships = [membership for membership in self.memberships if membership.course == course]
            lessons = [lesson for lesson in self.lessons if lesson.course == course]
            
            for index, lesson in enumerate(lessons):
                comments_num = random.randint(0, len(memberships))
                students_who_comment = random.sample(memberships, comments_num)
                comments_for_lesson = random.sample(comments, comments_num)
                
                for index, membership in enumerate(students_who_comment):
                    comments_objects.append(Comment(lesson=lesson, owner=membership.owner,
                        text=comments_for_lesson[index].get('description')))
        
        if comments_objects:
            Comment.objects.bulk_create(comments_objects)
            self.stdout.write(self.style.SUCCESS('Comments successfully created'))

        return comments_objects
    
    def _create_tasks(self, tasks):
        tasks_objects = []
        for course in self.courses:
            lessons = [lesson for lesson in self.lessons if lesson.course == course]
            
            for index, lesson in enumerate(lessons):
                tasks_num = random.randint(0, 2)
                tasks_for_lesson = random.sample(tasks, tasks_num)
                
                for index, task in enumerate(tasks_for_lesson):
                    tasks_objects.append(Task(
                        lesson=lesson, 
                        title=task.get('title'),
                        description=task.get('description')))
        
        if tasks_objects:
            Task.objects.bulk_create(tasks_objects)
            self.stdout.write(self.style.SUCCESS('Lessons tasks successfully created'))

        return tasks_objects
    
    def _create_memberships(self):
        memberships = []
        for course in self.courses:
            students_num = random.randint(0, len(self.users)-1)
            possible_students = random.sample(self.users, students_num)
            
            for student in possible_students:
                if course.owner == student:
                    continue
                memberships.append(Membership(owner=student, course=course))
        
        if memberships:
            Membership.objects.bulk_create(memberships)
            self.stdout.write(self.style.SUCCESS('Memberships successfully created'))
        
        return memberships
    
    def _create_reviews(self, reviews):
        reviews_objects = []
        for course in self.courses:
            memberships = [membership for membership in self.memberships if membership.course == course]
            reviews_num = random.randint(0, len(memberships))
            students_who_review = random.sample(memberships, reviews_num)
            reviews_for_course = random.sample(reviews, reviews_num)
            
            for index, membership in enumerate(students_who_review):
                reviews_objects.append(Review(
                    owner=membership.owner, 
                    course=course,
                    text=reviews_for_course[index].get('description'), 
                    rating=random.randint(1, 5)))
        
        if reviews_objects:
            Review.objects.bulk_create(reviews_objects)
            self.stdout.write(self.style.SUCCESS('Reviews successfully created'))
        
        return reviews_objects
    
    def _create_users(self, users):
        users_objects = []
        while True:
            try:
                users_num = int(input('Users number to generate (1-100): '))
                if not (users_num <= 100 and users_num > 0):
                    self.stdout.write(self.style.ERROR('Users number must be from 1 to 100'))
                    continue
                break
            except:
                self.stdout.write(self.style.ERROR('Users number must be integer'))

        for index, user in enumerate(random.sample(users, users_num)):
            user_object = User.objects.create_user(
                email=f'user{index+1}@gmail.com',
                password=f'user{index+1}'
            )
            users_objects.append(user_object)
            profile = user_object.profile
            profile.first_name = user.get('first_name', None)
            profile.last_name = user.get('last_name', None)
            profile.bio = user.get('bio', None)
            profile.save()
        
        if users_objects:
            self.stdout.write(self.style.SUCCESS('Users successfully created'))
        return users_objects

    def handle(self, *args, **options):
        mock_data = []
        with open('mock_data/mock.json') as file:
            try:
                mock_data =  json.load(file)
            except ValueError as err:
                print(err)

        self.admin = self._create_superuser()
        self.users = self._create_users(mock_data.get('users', None))
        self.categories = self._create_categories(mock_data.get('categories', None))
        self.courses = self._create_courses(mock_data.get('full_general', None))
        self.memberships = self._create_memberships()
        self.lessons = self._create_lessons(mock_data.get('full_general', None))
        self.tasks = self._create_tasks(mock_data.get('full_general', None))
        self.reviews = self._create_reviews(mock_data.get('full_general', None))
        self.comments = self._create_comments(mock_data.get('full_general', None))
        self.courses_news = self._create_course_news(mock_data.get('full_general', None))