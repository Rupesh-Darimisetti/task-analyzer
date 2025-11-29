from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('list/', views.get_task_list, name='task_list'),
    path('analyze/', views.analyze, name='analyze'),
    path('suggest/', views.suggest, name='suggest'),
]
