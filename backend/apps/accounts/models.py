from django.db import models

from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import AbstractBaseUser

from .managers import ProfileManager, UserManager
from .utils import avatarFilePath

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, blank=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self) -> str:
        return self.email


class Profile(models.Model):
    """ Profile with additional info for User instance (One to one) """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    bio = models.TextField(max_length=500, null=True, blank=True)
    avatar = models.ImageField(upload_to=avatarFilePath, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = ProfileManager()
    
    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
    
    def save(self, *args, **kwargs) -> None:
        try:
            this = Profile.objects.get(id=self.id)
            if this.avatar:
                this.avatar.delete()
        except:
            pass
        super(Profile, self).save(*args, **kwargs)
    
    def __str__(self) -> str:
        return str(self.user)
