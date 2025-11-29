from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('list/', views.get_task_list, name='task_list'),
    path('analyze/', views.analyze, name='analyze'),
    path('suggest/', views.suggest, name='suggest'),
    path('save/', views.save_task, name='save_task'),
    path('save-analysis/', views.save_tasks_from_analysis, name='save_analysis'),
    path('delete/<int:task_id>/', views.delete_task, name='delete_task'),
]
