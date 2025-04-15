from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project


class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ['id', 'username', 'password', 'email']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['project_id', 'name', 'language', 'random_colors', 'code', 'create_date', 'update_date']
