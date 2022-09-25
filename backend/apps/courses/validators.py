from rest_framework import serializers

def validate_cover_size(temp_file):
    if temp_file.size > 500000:
        raise serializers.ValidationError('Too big image size for course cover, we allow only 500kb maximum')

def validate_cover_type(temp_file):
    if temp_file.content_type != "image/jpeg":
        raise serializers.ValidationError('Cover photo must be in JPEG format only')

def validate_youtube_link(link: str):
    if not link.startswith('https://youtu.be/'):
        raise serializers.ValidationError("We allow videolinks only from youtube, so your url must start with https://youtu.be/")
