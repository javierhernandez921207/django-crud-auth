from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.singin, name='login'),
    path('logout/', views.singout, name='logout'),
    path('tasks/', views.tasks, name='tasks'),
]
