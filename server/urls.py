from django.urls import re_path
from projects import views
urlpatterns = [
    re_path('login',views.login),
    re_path('logout',views.logout),
    re_path('signup',views.signup),
    re_path('user-projects',views.user_projects),
    re_path('user-details', views.get_user_details)
]
