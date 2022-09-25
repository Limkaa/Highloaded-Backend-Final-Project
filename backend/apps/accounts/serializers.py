from rest_framework import serializers

from .models import User, Profile
from .validators import validate_avatar_size, validate_avatar_type

class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def create(self, validated_data):
        email = validated_data.get('email')
        password = validated_data.pop('password')
        user = User(email=email)
        user.set_password(password)
        user.save()
        return user


class ProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    bio = serializers.CharField(max_length=500, required=False, allow_blank=True)
    avatar = serializers.ImageField(required=False, validators=[validate_avatar_size, validate_avatar_type])
    updated_at = serializers.DateTimeField(read_only=True)
    
    def update(self, instance: Profile, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance