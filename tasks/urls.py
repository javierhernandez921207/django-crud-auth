from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.singin, name='login'),
    path('logout/', views.singout, name='logout'),
    path('tasks/', views.tasks, name='tasks'),
    path('tasks_completed/', views.tasks_completed, name='tasks_completed'),
    path('tasks/create', views.create_task, name='create_task'),
    path('tasks/<int:task_pk>', views.view_task, name='view_task'),
    path('tasks/<int:task_pk>/complete', views.complete_task, name='complete_task'),
    path('tasks/<int:task_pk>/delete', views.delete_task, name='delete_task'),
]
