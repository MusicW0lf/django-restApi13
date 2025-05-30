from graphene_django.views import GraphQLView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from projects.auth import CookieJWTAuthentication
from django.contrib.auth.models import AnonymousUser

class CustomGraphQLView(GraphQLView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        user = AnonymousUser()
        auth_result = CookieJWTAuthentication().authenticate(request)
        if auth_result:
            user, token = auth_result
            request.user = user

        return super().dispatch(request, *args, **kwargs)