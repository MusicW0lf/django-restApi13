from datetime import timedelta
from django.utils import timezone
from projects.auth import CookieJWTAuthentication
from rest_framework.decorators import api_view ,authentication_classes, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from .serializers import UserSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from .models import Project
from .serializers import ProjectSerializer
from random import randint
from RestrictedPython import compile_restricted, safe_globals
from RestrictedPython.Guards import safe_builtins

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
    response = Response({"message": "Logged out"}, status=status.HTTP_200_OK)
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
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAuthenticated])
def execute(request):
    try:
        # Extract code and project_id from request data
        code = request.data.get('code', '')
        project_id = request.data.get('project_id')

        if not project_id:
            return Response({'stdout': None, 'error': 'project_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        project = get_object_or_404(Project, project_id=project_id)

        # Save the code to the project
        project.code = code
        project.save()

        if not code:
            return Response({'stdout': None, 'error': 'No code provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare restricted execution environment
        exec_globals = safe_globals.copy()
        exec_globals['__builtins__'] = safe_builtins.copy()

        # Define allowed built-ins
        allowed_builtins = {
            'range': range,
            'len': len,
            'int': int,
            'float': float,
            'str': str,
            'list': list,
            'dict': dict,
            'set': set,
            'tuple': tuple,
            'sorted': sorted,
            'min': min,
            'max': max,
            'sum': sum,
            'any': any,
            'all': all,
            'enumerate': enumerate,
            'zip': zip,
            'next': next,
        }

        # Capture printed output
        result = []

        def custom_print(*args, **kwargs):
            result.append(" ".join(map(str, args)))

        allowed_builtins['print'] = custom_print
        exec_globals['__builtins__'].update(allowed_builtins)
        exec_globals['result'] = result.append

        # Compile and execute the code
        compiled_code = compile_restricted(code, '<string>', 'exec', policy=None)
        exec(compiled_code, exec_globals, {})

        output = result if result else 'Execution completed without output.'

        return Response({'stdout': output, 'error': None}, status=status.HTTP_200_OK)
    
    except Exception as e:
            # Handle errors gracefully
        return JsonResponse({'stdout': None, 'error': str(e)})

@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(request, email=email, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        
        response = Response({'message': 'Login successful.'}, status=status.HTTP_200_OK)
        response.set_cookie(
            key='access_token',
            value=str(refresh.access_token),
            httponly=True,
            secure=False,  # Use True in production with HTTPS
            samesite='Lax',
            expires=timezone.now() + timedelta(minutes=60),
        )
        return response
    else:
        return Response({'detail': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)


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
    project = get_object_or_404(Project, project_id=project_id)
    if project.author != request.user:
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

    new_name = request.data.get('name')
    if not new_name:
        return Response({'detail': 'Missing new name'}, status=status.HTTP_400_BAD_REQUEST)

    project.name = new_name
    project.save()
    return Response({'detail': 'Project renamed'}, status=status.HTTP_200_OK)