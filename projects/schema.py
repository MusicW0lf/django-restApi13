import graphene
from graphene_django.types import DjangoObjectType
from .models import Project
from .models import CustomUser
from graphene import ObjectType, Mutation, String, Int
from .models import Project
from django.shortcuts import get_object_or_404
from RestrictedPython import compile_restricted, safe_globals
from RestrictedPython.Guards import safe_builtins
from graphql import GraphQLError
from functools import wraps
from rest_framework_simplejwt.tokens import RefreshToken
from projects.serializers import UserSerializer
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth import authenticate
from random import randint

class UserType(DjangoObjectType):
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "projects")

    projects = graphene.List(lambda: ProjectType)

    def resolve_projects(self, info):
        return self.projects.all()  # Because of related_name='projects' in the Project model


class ProjectType(DjangoObjectType):
    class Meta:
        model = Project
        fields = ("project_id", "name", "language", "code", "author", "random_colors", "create_date", "update_date")

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        info = args[1]
        user = info.context.user
        if not user or not user.is_authenticated:
            raise GraphQLError("Authentication required.")
        return func(*args, **kwargs)
    return wrapper

class Query(graphene.ObjectType):
    my_projects = graphene.List(ProjectType)
    project = graphene.Field(ProjectType, project_id=graphene.Int())
    user = graphene.Field(UserType)

    @login_required
    def resolve_user(self, info):
        return info.context.user

    @login_required
    def resolve_my_projects(root, info):
        return Project.objects.filter(author=info.context.user)

    @login_required
    def resolve_project(root, info, project_id):
        try:
            return Project.objects.get(project_id=project_id)
        except Project.DoesNotExist:
            return None
        


class ExecuteCode(graphene.Mutation):
    class Arguments:
        project_id = Int(required=True)
        code = String(required=True)

    stdout = graphene.List(graphene.String)
    error = graphene.String()

    @login_required
    def mutate(self, info, project_id, code):

        project = get_object_or_404(Project, project_id=project_id)
        project.code = code
        project.save()

        if not code:
            return ExecuteCode(stdout=None, error="No code given")

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

        result = []

        def _print_(*args):
            result.append(" ".join(map(str, args)))

        # Add allowed built-ins and _print_
        allowed_builtins['print'] = _print_
        exec_globals['__builtins__'].update(allowed_builtins)
        exec_globals['_print_'] = _print_
        exec_globals['_getattr_'] = getattr
        exec_globals['_getitem_'] = lambda obj, index: obj[index]
        exec_globals['_getiter_'] = iter

        try:
            compiled_code = compile_restricted(code, '<string>', 'exec', policy=None)
            exec(compiled_code, exec_globals, {})
            output = result if result else ["Execution completed."]
            return ExecuteCode(stdout=output, error=None)
        except Exception as e:
            return ExecuteCode(stdout=None, error=str(e))
        

class RenameProject(graphene.Mutation):
    class Arguments:
        project_id = graphene.Int(required=True)
        name = graphene.String(required=True)

    project = graphene.Field(ProjectType)

    @login_required
    def mutate(self, info, project_id, name):
        user = info.context.user
        try:
            project = Project.objects.get(project_id=project_id, author=user)
        except Project.DoesNotExist:
            raise GraphQLError("Project not found or unauthorized.")

        project.name = name
        project.save()
        return RenameProject(project=project)


class DeleteProject(graphene.Mutation):
    class Arguments:
        project_id = graphene.Int(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info, project_id):
        user = info.context.user
        try:
            project = Project.objects.get(project_id=project_id, author=user)
        except Project.DoesNotExist:
            raise GraphQLError("Project not found or unauthorized.")
        project.delete()
        return DeleteProject(success=True)



class CreateProject(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        language = graphene.String(required=True)

    project = graphene.Field(ProjectType)

    @login_required
    def mutate(self, info, name, language):
        user = info.context.user
        random_colors = [f"#{randint(0, 0xFFFFFF):06x}" for _ in range(2)]
        project = Project.objects.create(
        name=name,
        language=language,
        code="You can write your code here!",
        author=user,
        random_colors=random_colors,
        )
        return CreateProject(project=project)

class Mutation(ObjectType):
    execute_code = ExecuteCode.Field()
    create_project = CreateProject.Field()
    rename_project = RenameProject.Field()
    delete_project = DeleteProject.Field()



schema = graphene.Schema(query=Query, mutation=Mutation)

