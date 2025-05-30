import jwt
from rest_framework.authentication import BaseAuthentication
from django.conf import settings
from .models import CustomUser
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class CookieJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get('access_token')
        
        if not token:
            return None

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            user = CustomUser.objects.get(id=payload['user_id'])

            return (user, token)
        
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('token is expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('invalid token')
        except CustomUser.DoesNotExist:
            raise AuthenticationFailed('user not found')

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        email = kwargs.get('email', username)  # Support both styles
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None

