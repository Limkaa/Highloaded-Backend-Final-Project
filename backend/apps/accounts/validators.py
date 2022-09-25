from rest_framework import serializers

def validate_avatar_size(temp_file):
    if temp_file.size > 100000:
        raise serializers.ValidationError('Too big image size for profile picture, we allow only 100kb maximum')

def validate_avatar_type(temp_file):
    if temp_file.content_type != "image/webp":
        raise serializers.ValidationError('Profile photo must be in WEBP format only')
