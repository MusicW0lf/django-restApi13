from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    username = models.CharField()
    email = models.EmailField(unique=True, db_index=True)

    USERNAME_FIELD = 'email'  # <-- this tells Django that 'email' is the login field
    REQUIRED_FIELDS = ['username']  # still required if you want to collect username too




LANG = ['python', 'js', 'java', 'c', 'csharp', 'ruby', 'go']

LANGUAGES = [
        ('Python', 'python'),
        ('JavaScript', 'js'),
        ('Java', 'java'),
        ('C', 'c'),
        ('C#', 'csharp'),
        ('Ruby', 'ruby'),
        ('Go', 'go'),
        ('HTML', 'html'),
        ('CSS', 'css'),
    ]

class Project(models.Model):
    
    project_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    language = models.CharField(max_length=20, choices=LANGUAGES)
    code = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="projects")
    random_colors = models.JSONField() 
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


    def clean(self):
        # Ensure the language is one of the predefined choices
        if self.language not in LANGUAGES:
            raise ValidationError(f"{self.language} is not a valid language.")
    
    def __str__(self):
        return self.name
