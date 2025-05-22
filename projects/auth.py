import jwt
from rest_framework.authentication import BaseAuthentication
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.exceptions import AuthenticationFailed

class CookieJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Look for the token in the cookies
        token = request.COOKIES.get('access_token')
        
        if not token:
            return None  # No token found, so no authentication

        try:
            # Decode the JWT token (use your secret key or public key here)
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            # Get the user from the payload (you may need to adjust the field name)
            user = User.objects.get(id=payload['user_id'])

            # Return the user and the token
            return (user, token)
        
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('token is expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('invalid token')
        except User.DoesNotExist:
            raise AuthenticationFailed('user not found')

