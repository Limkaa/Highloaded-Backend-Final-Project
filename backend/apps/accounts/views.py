from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes

from .models import Profile

from .serializers import UserSerializer, ProfileSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([~IsAuthenticated])
def register(request):
    serializer = UserSerializer(data = request.data)
    if serializer.is_valid():
        try:
            serializer.save()
            logger.info('New user registered')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"error": "User with same email already exists"}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    profile = Profile.objects.filter(user__id = request.user.id).first()
    
    if profile:
        if request.method == 'GET':
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        
        elif request.method == 'PUT':
            serializer = ProfileSerializer(instance=profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                logger.info('Profile updated')
                return Response(serializer.data)
            return Response(serializer.errors)
        
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)