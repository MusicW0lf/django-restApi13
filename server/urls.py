from django.urls import path
from projects import views
urlpatterns = [
    path('login',views.login),
    path('logout',views.logout),
    path('signup',views.signup),
    path('user-projects/',views.user_projects),
    path('user-details', views.get_user_details),
    path('create-project', views.create_project),
    path('project/<int:project_id>/', views.get_project_for_author),
    path('project/<int:project_id>/delete/', views.delete_project),
    path('project/<int:project_id>/rename/', views.rename_project),
    path('project/execute/', views.execute)
]
