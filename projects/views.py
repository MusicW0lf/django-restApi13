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
    
    print(serializer.data)
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
    # Assuming you have a serializer to handle user registration
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()  # Create the user
        
        # Set password securely
        user.set_password(request.data['password'])
        user.save()

        # Create JWT token for the user (access token and refresh token)
        refresh = RefreshToken.for_user(user)
        
        # Set the access token in an HTTP-only cookie
        response = Response({'message': 'User created successfully.'})
        response.set_cookie(
            key='access_token',
            value=str(refresh.access_token),
            httponly=True,  # Ensures the cookie is not accessible via JavaScript
            #secure=True,  # Ensures the cookie is only sent over HTTPS
            samesite='Lax',  # Prevents cross-site request forgery (CSRF)
            expires=timezone.now() + timedelta(minutes=60),  # Set the expiration time
        )
        return response
    else:
        return Response(serializer.errors, status=400)