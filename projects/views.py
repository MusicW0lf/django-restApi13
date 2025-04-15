from datetime import timedelta
from django.utils import timezone
from projects.auth import CookieJWTAuthentication
from rest_framework.decorators import api_view ,authentication_classes, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from .models import Project
from .serializers import ProjectSerializer
from random import randint


@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAuthenticated]) 
def get_user_details(request):
    user = request.user


    if user.username:
        return Response({'username': user.username})
    return Response({'username': "Guest"})

@api_view(['POST'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAuthenticated]) 
def logout(request):
    response = Response({"message": "Logged out"})
    response.delete_cookie('access_token')  # Match name and path
    return response

@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAuthenticated]) 
def user_projects(request):
    # Get the projects of the currently authenticated user
    projects = Project.objects.filter(author=request.user)
    
    # Serialize the projects
    serializer = ProjectSerializer(projects, many=True)
    
    return JsonResponse(serializer.data, safe=False)


@api_view(['POST'])
def login(request):
    # Get the user by email
    user = get_object_or_404(get_user_model(), email=request.data['email'])
    
    # Check if the password is correct
    if not user.check_password(request.data['password']):
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate JWT token (access token and refresh token)
    refresh = RefreshToken.for_user(user)
    
    response = Response({'message': 'Login successful.'})
    response.set_cookie(
        key='access_token',
        value=str(refresh.access_token),
        httponly=True,  # Ensures the cookie is not accessible via JavaScript
        secure=False,  # Ensure this is True in production with HTTPS
        samesite='Lax',  # Helps prevent cross-site request forgery (CSRF)
        expires=timezone.now() + timedelta(minutes=60),  # Set the expiration time for 1 hour
    )
    
    return response

@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save() 

        user.set_password(request.data['password'])
        user.save()

        refresh = RefreshToken.for_user(user)

        response = Response({'message': 'User created successfully.'})
        response.set_cookie(
            key='access_token',
            value=str(refresh.access_token),
            httponly=True,
            #secure=True, 
            samesite='Lax', 
            expires=timezone.now() + timedelta(minutes=60),
        )
        return response
    else:
        return Response(serializer.errors, status=400)
    

@api_view(['POST'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAuthenticated]) 
def create_project(request):
    user = request.user
    name = request.data.get('name')
    language = request.data.get('language')

    if not name or not language:
        return Response({'error': 'Name and language are required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    random_colors = [f"#{randint(0, 0xFFFFFF):06x}" for _ in range(2)]

    project = Project.objects.create(
        name=name,
        language=language,
        code="You can write your code here!",
        author=user,
        random_colors=random_colors,
    )

    return Response({'project_id': project.project_id}, status=status.HTTP_201_CREATED)



@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAuthenticated])
def get_project_for_author(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

    if project.author.id != request.user.id:
        return Response({'error': 'Forbidden: You are not the author of this project.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = ProjectSerializer(project)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieJWTAuthentication])
def delete_project(request, project_id):
    project = get_object_or_404(Project, project_id=project_id)
    if project.author != request.user:
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

    project.delete()
    return Response({'detail': 'Project deleted'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieJWTAuthentication])
def rename_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.author != request.user:
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

    new_name = request.data.get('name')
    if not new_name:
        return Response({'detail': 'Missing new name'}, status=status.HTTP_400_BAD_REQUEST)

    project.name = new_name
    project.save()
    return Response({'detail': 'Project renamed'}, status=status.HTTP_200_OK)