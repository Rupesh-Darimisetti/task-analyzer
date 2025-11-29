from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Task
from .serializers import TaskSerializer
from .scoring import calculate_task_score
from datetime import date

# Create your views here.
@api_view(['GET'])
def get_task_list(request):
    tasks = Task.objects.all()
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def analyze(request):
    """
    Endpoint: /analyze/
    
    Accepts a POST request with a list of tasks.
    Calculates priority scores for each task and returns them sorted by score (highest first).
    
    Expected request body:
    {
        "tasks": [
            {
                "id": 1,
                "title": "Task title",
                "due_date": "2025-12-01",
                "importance": 8,
                "estimated_hours": 2,
                "dependencies": []
            },
            ...
        ]
    }
    """
    try:
        tasks_data = request.data.get('tasks', [])
        
        if not isinstance(tasks_data, list):
            return Response(
                {"error": "Invalid request. 'tasks' must be a list."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Score each task
        scored_tasks = []
        for task in tasks_data:
            # Convert due_date string to date object if needed
            if isinstance(task.get('due_date'), str):
                task['due_date'] = date.fromisoformat(task['due_date'])
            
            score = calculate_task_score(task)
            task['score'] = score
            scored_tasks.append(task)
        
        # Sort by score (highest first)
        sorted_tasks = sorted(scored_tasks, key=lambda x: x['score'], reverse=True)
        
        return Response({
            "count": len(sorted_tasks),
            "tasks": sorted_tasks
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
def suggest(request):
    """
    Endpoint: /suggest/
    
    Returns the top 3 tasks for "today" with a text explanation.
    Fetches all tasks from the database, scores them, and returns the top 3
    with reasoning for why they are recommended.
    """
    try:
        # Get all tasks from the database
        all_tasks = Task.objects.all()
        
        # Convert to dict format for scoring
        tasks_data = []
        for task in all_tasks:
            task_dict = {
                'id': task.id,
                'title': task.title,
                'due_date': task.due_date,
                'importance': task.importance,
                'estimated_hours': task.estimated_hours,
                'dependencies': task.dependencies
            }
            score = calculate_task_score(task_dict)
            tasks_data.append({
                'task': task_dict,
                'score': score
            })
        
        # Sort by score (highest first) and get top 3
        sorted_tasks = sorted(tasks_data, key=lambda x: x['score'], reverse=True)[:3]
        
        # Build response with explanations
        suggestions = []
        today = date.today()
        
        for item in sorted_tasks:
            task = item['task']
            score = item['score']
            
            # Generate explanation
            explanation = ""
            days_until_due = (task['due_date'] - today).days
            
            if days_until_due < 0:
                explanation = f"OVERDUE by {abs(days_until_due)} days! This task needs immediate attention."
            elif days_until_due == 0:
                explanation = "Due TODAY! This is your most urgent task."
            elif days_until_due <= 3:
                explanation = f"Due in {days_until_due} day(s). High urgency."
            else:
                explanation = f"Due in {days_until_due} days. Important with high priority score."
            
            if task['estimated_hours'] < 2:
                explanation += " Quick win - can be completed in under 2 hours."
            
            suggestions.append({
                'id': task['id'],
                'title': task['title'],
                'due_date': str(task['due_date']),
                'importance': task['importance'],
                'estimated_hours': task['estimated_hours'],
                'priority_score': score,
                'explanation': explanation
            })
        
        return Response({
            "count": len(suggestions),
            "today": str(today),
            "top_tasks": suggestions
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )