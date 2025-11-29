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
    
    Edge cases handled:
    - Missing importance: defaults to 5
    - Missing estimated_hours: defaults to 1
    - Past due dates (e.g., 1990): treated as overdue (+100 urgency)
    - Invalid dates: returns 400 error
    - Non-array tasks: returns 400 error
    """
    try:
        tasks_data = request.data.get('tasks', [])
        
        if not isinstance(tasks_data, list):
            return Response(
                {"error": "Invalid request. 'tasks' must be a list."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(tasks_data) == 0:
            return Response(
                {"error": "Tasks list is empty. Please provide at least one task."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Score each task
        scored_tasks = []
        for idx, task in enumerate(tasks_data):
            try:
                # Validate required fields
                if not task.get('title'):
                    task['title'] = f'Untitled Task {idx + 1}'
                
                # Convert due_date string to date object if needed
                if isinstance(task.get('due_date'), str):
                    task['due_date'] = date.fromisoformat(task['due_date'])
                
                # Apply defaults for missing fields
                if 'importance' not in task:
                    task['importance'] = 5
                if 'estimated_hours' not in task:
                    task['estimated_hours'] = 1
                if 'dependencies' not in task:
                    task['dependencies'] = []
                
                score = calculate_task_score(task)
                task['score'] = score
                scored_tasks.append(task)
            
            except ValueError as e:
                # Handle invalid date format
                return Response(
                    {"error": f"Task {idx + 1}: Invalid date format. Use YYYY-MM-DD format. Details: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                # Handle other parsing errors
                return Response(
                    {"error": f"Task {idx + 1}: Error processing task. Details: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Sort by score (highest first)
        sorted_tasks = sorted(scored_tasks, key=lambda x: x.get('score', 0), reverse=True)
        
        return Response({
            "count": len(sorted_tasks),
            "tasks": sorted_tasks
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {"error": f"Server error: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def save_task(request):
    """
    Endpoint: /save/
    
    Saves a single task to the database.
    
    Expected request body:
    {
        "title": "Task title",
        "due_date": "2025-12-01",
        "importance": 8,
        "estimated_hours": 2,
        "dependencies": []
    }
    """
    try:
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": f"Failed to save task: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def save_tasks_from_analysis(request):
    """
    Endpoint: /save-analysis/
    
    Saves multiple tasks from analysis to the database.
    
    Expected request body:
    {
        "tasks": [
            {
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
                {"error": "'tasks' must be a list"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        saved_tasks = []
        errors = []
        
        for idx, task_data in enumerate(tasks_data):
            try:
                # Remove score field if present (not a model field)
                if 'score' in task_data:
                    del task_data['score']
                
                serializer = TaskSerializer(data=task_data)
                if serializer.is_valid():
                    saved_task = serializer.save()
                    saved_tasks.append(serializer.data)
                else:
                    errors.append({"task_index": idx, "errors": serializer.errors})
            except Exception as e:
                errors.append({"task_index": idx, "error": str(e)})
        
        return Response({
            "saved": len(saved_tasks),
            "failed": len(errors),
            "saved_tasks": saved_tasks,
            "errors": errors if errors else None
        }, status=status.HTTP_200_OK if saved_tasks else status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response(
            {"error": f"Server error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
def delete_task(request, task_id):
    """
    Endpoint: /delete/<task_id>/
    
    Deletes a task from the database.
    """
    try:
        task = Task.objects.get(id=task_id)
        task.delete()
        return Response(
            {"message": f"Task {task_id} deleted successfully"},
            status=status.HTTP_200_OK
        )
    except Task.DoesNotExist:
        return Response(
            {"error": f"Task {task_id} not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"Failed to delete task: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
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