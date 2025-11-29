from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from datetime import date, timedelta
from .models import Task
from .scoring import calculate_task_score
import json


# ============================================
# MODEL TESTS
# ============================================

class TaskModelTest(TestCase):
    """Test the Task model"""
    
    def setUp(self):
        """Create test data"""
        self.today = date.today()
        self.task = Task.objects.create(
            title="Test Task",
            due_date=self.today + timedelta(days=5),
            importance=7,
            estimated_hours=3,
            dependencies=[]
        )
    
    def test_task_creation(self):
        """Test creating a task"""
        self.assertEqual(self.task.title, "Test Task")
        self.assertEqual(self.task.importance, 7)
        self.assertEqual(self.task.estimated_hours, 3)
        self.assertEqual(self.task.dependencies, [])
    
    def test_task_defaults(self):
        """Test default values"""
        task = Task.objects.create(
            title="Simple Task",
            due_date=self.today + timedelta(days=1)
        )
        self.assertEqual(task.importance, 5)
        self.assertEqual(task.estimated_hours, 1)
        self.assertEqual(task.dependencies, [])
    
    def test_task_string_representation(self):
        """Test task string representation"""
        self.assertEqual(str(self.task), "Test Task")
    
    def test_task_with_dependencies(self):
        """Test task with dependencies"""
        task = Task.objects.create(
            title="Dependent Task",
            due_date=self.today + timedelta(days=2),
            dependencies=[1, 2, 3]
        )
        self.assertEqual(task.dependencies, [1, 2, 3])
    
    def test_task_max_importance(self):
        """Test task with maximum importance"""
        task = Task.objects.create(
            title="Critical Task",
            due_date=self.today,
            importance=10
        )
        self.assertEqual(task.importance, 10)
    
    def test_task_min_importance(self):
        """Test task with minimum importance"""
        task = Task.objects.create(
            title="Low Priority Task",
            due_date=self.today + timedelta(days=30),
            importance=1
        )
        self.assertEqual(task.importance, 1)


# ============================================
# SCORING ALGORITHM TESTS
# ============================================

class ScoringAlgorithmTest(TestCase):
    """Test the scoring algorithm"""
    
    def setUp(self):
        """Setup for scoring tests"""
        self.today = date.today()
    
    def test_overdue_task_scores_high(self):
        """Test that overdue tasks get high urgency score"""
        task = {
            'title': 'Overdue Task',
            'due_date': self.today - timedelta(days=5),
            'importance': 5,
            'estimated_hours': 2,
            'dependencies': []
        }
        score = calculate_task_score(task)
        # Should include: 100 (overdue) + 25 (importance 5 * 5) + 10 (< 2 hours)
        self.assertGreaterEqual(score, 100)
    
    def test_due_today_scores_high(self):
        """Test that tasks due today score high"""
        task = {
            'title': 'Due Today',
            'due_date': self.today,
            'importance': 5,
            'estimated_hours': 1,
            'dependencies': []
        }
        score = calculate_task_score(task)
        # No urgency bonus for today (< 0 days), but base + importance
        self.assertGreater(score, 0)
    
    def test_due_within_3_days(self):
        """Test urgency for tasks due within 3 days"""
        task = {
            'title': 'Soon',
            'due_date': self.today + timedelta(days=2),
            'importance': 5,
            'estimated_hours': 1,
            'dependencies': []
        }
        score = calculate_task_score(task)
        # Should include: 50 (within 3 days) + 25 (importance) + 10 (quick)
        self.assertGreaterEqual(score, 50)
    
    def test_due_within_week(self):
        """Test urgency for tasks due within a week"""
        task = {
            'title': 'This Week',
            'due_date': self.today + timedelta(days=5),
            'importance': 5,
            'estimated_hours': 1,
            'dependencies': []
        }
        score = calculate_task_score(task)
        # Should include: 25 (within week) + 25 (importance)
        self.assertGreaterEqual(score, 25)
    
    def test_due_far_future(self):
        """Test urgency for tasks far in future"""
        task = {
            'title': 'Future',
            'due_date': self.today + timedelta(days=30),
            'importance': 5,
            'estimated_hours': 1,
            'dependencies': []
        }
        score = calculate_task_score(task)
        # Should include: 0 (no urgency) + 25 (importance) + 10 (quick)
        self.assertEqual(score, 35)
    
    def test_importance_weighting(self):
        """Test that importance is correctly weighted"""
        low_importance = {
            'due_date': self.today + timedelta(days=10),
            'importance': 1,
            'estimated_hours': 5,
            'dependencies': []
        }
        high_importance = {
            'due_date': self.today + timedelta(days=10),
            'importance': 10,
            'estimated_hours': 5,
            'dependencies': []
        }
        low_score = calculate_task_score(low_importance)
        high_score = calculate_task_score(high_importance)
        # Difference should be 5 * 5 = 25
        self.assertEqual(high_score - low_score, 45)
    
    def test_quick_win_bonus(self):
        """Test that quick tasks get bonus"""
        quick_task = {
            'due_date': self.today + timedelta(days=5),
            'importance': 5,
            'estimated_hours': 1,
            'dependencies': []
        }
        slow_task = {
            'due_date': self.today + timedelta(days=5),
            'importance': 5,
            'estimated_hours': 5,
            'dependencies': []
        }
        quick_score = calculate_task_score(quick_task)
        slow_score = calculate_task_score(slow_task)
        # Difference should be 10 (quick win bonus)
        self.assertEqual(quick_score - slow_score, 10)
    
    def test_dependency_penalty(self):
        """Test that dependencies reduce score"""
        no_deps = {
            'due_date': self.today + timedelta(days=5),
            'importance': 5,
            'estimated_hours': 1,
            'dependencies': []
        }
        one_dep = {
            'due_date': self.today + timedelta(days=5),
            'importance': 5,
            'estimated_hours': 1,
            'dependencies': [1]
        }
        three_deps = {
            'due_date': self.today + timedelta(days=5),
            'importance': 5,
            'estimated_hours': 1,
            'dependencies': [1, 2, 3]
        }
        no_deps_score = calculate_task_score(no_deps)
        one_dep_score = calculate_task_score(one_dep)
        three_deps_score = calculate_task_score(three_deps)
        
        # Each dependency is -30, but it can't go below 0
        # Base score: 25 (urgency for 5 days) + 25 (importance) + 10 (quick win) = 60
        # With 3 deps: 60 - 90 = -30, floored to 0
        self.assertEqual(no_deps_score, 60)  # 25 + 25 + 10
        self.assertEqual(one_dep_score, 30)  # 60 - 30 = 30
        self.assertEqual(three_deps_score, 0)  # 60 - 90 = -30, floored to 0
    
    def test_score_never_negative(self):
        """Test that scores never go below 0"""
        highly_blocked = {
            'due_date': self.today + timedelta(days=30),
            'importance': 1,
            'estimated_hours': 10,
            'dependencies': [1, 2, 3, 4, 5]
        }
        score = calculate_task_score(highly_blocked)
        self.assertGreaterEqual(score, 0)
    
    def test_string_date_parsing(self):
        """Test that string dates are parsed correctly"""
        task = {
            'due_date': self.today.isoformat(),
            'importance': 5,
            'estimated_hours': 1,
            'dependencies': []
        }
        score = calculate_task_score(task)
        self.assertGreater(score, 0)
    
    def test_missing_fields_use_defaults(self):
        """Test that missing fields use defaults"""
        minimal_task = {
            'due_date': self.today + timedelta(days=5)
        }
        score = calculate_task_score(minimal_task)
        # Should use defaults: importance=5 (*5=25) + no urgency bonus (10 days)
        self.assertGreater(score, 0)
    
    def test_invalid_input_returns_neutral(self):
        """Test that invalid input returns neutral score"""
        invalid_task = {
            'due_date': 'invalid-date',
            'importance': 'not-a-number'
        }
        score = calculate_task_score(invalid_task)
        # Should return neutral score of 50
        self.assertEqual(score, 50)


# ============================================
# API ENDPOINT TESTS
# ============================================

class TaskAPITest(TestCase):
    """Test the Task API endpoints"""
    
    def setUp(self):
        """Setup for API tests"""
        self.client = Client()
        self.today = date.today()
        
        # Create test tasks
        self.task1 = Task.objects.create(
            title="Urgent Bug Fix",
            due_date=self.today,
            importance=9,
            estimated_hours=4,
            dependencies=[]
        )
        self.task2 = Task.objects.create(
            title="Code Review",
            due_date=self.today + timedelta(days=3),
            importance=7,
            estimated_hours=2,
            dependencies=[self.task1.id]
        )
    
    def test_list_tasks(self):
        """Test listing all tasks"""
        response = self.client.get(reverse('tasks:task_list'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['title'], "Urgent Bug Fix")
    
    def test_analyze_tasks_valid(self):
        """Test analyzing tasks with valid input"""
        payload = {
            'tasks': [
                {
                    'title': 'Task 1',
                    'due_date': str(self.today + timedelta(days=1)),
                    'importance': 8,
                    'estimated_hours': 2,
                    'dependencies': []
                },
                {
                    'title': 'Task 2',
                    'due_date': str(self.today + timedelta(days=5)),
                    'importance': 5,
                    'estimated_hours': 3,
                    'dependencies': []
                }
            ]
        }
        response = self.client.post(
            reverse('tasks:analyze'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 2)
        # First task should have higher score (due sooner)
        self.assertGreater(data['tasks'][0]['score'], data['tasks'][1]['score'])
    
    def test_analyze_tasks_empty(self):
        """Test analyzing empty tasks list"""
        payload = {'tasks': []}
        response = self.client.post(
            reverse('tasks:analyze'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_analyze_tasks_non_array(self):
        """Test analyzing non-array input"""
        payload = {'tasks': 'not-an-array'}
        response = self.client.post(
            reverse('tasks:analyze'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_analyze_invalid_date(self):
        """Test analyzing tasks with invalid date"""
        payload = {
            'tasks': [
                {
                    'title': 'Bad Date Task',
                    'due_date': 'not-a-date',
                    'importance': 5,
                    'estimated_hours': 1,
                    'dependencies': []
                }
            ]
        }
        response = self.client.post(
            reverse('tasks:analyze'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_suggest_tasks(self):
        """Test getting task suggestions"""
        response = self.client.get(reverse('tasks:suggest'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('count', data)
        self.assertIn('today', data)
        self.assertIn('top_tasks', data)
    
    def test_save_single_task(self):
        """Test saving a single task"""
        payload = {
            'title': 'New Task',
            'due_date': str(self.today + timedelta(days=5)),
            'importance': 6,
            'estimated_hours': 2,
            'dependencies': []
        }
        response = self.client.post(
            reverse('tasks:save_task'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['title'], 'New Task')
        self.assertTrue('id' in data)
    
    def test_save_task_invalid(self):
        """Test saving task with invalid data"""
        payload = {
            'title': 'Bad Task',
            'due_date': 'invalid-date'
        }
        response = self.client.post(
            reverse('tasks:save_task'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_save_analysis_multiple(self):
        """Test saving multiple tasks from analysis"""
        payload = {
            'tasks': [
                {
                    'title': 'Analyzed Task 1',
                    'due_date': str(self.today + timedelta(days=2)),
                    'importance': 7,
                    'estimated_hours': 1,
                    'dependencies': []
                },
                {
                    'title': 'Analyzed Task 2',
                    'due_date': str(self.today + timedelta(days=5)),
                    'importance': 5,
                    'estimated_hours': 3,
                    'dependencies': []
                }
            ]
        }
        response = self.client.post(
            reverse('tasks:save_analysis'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['saved'], 2)
        self.assertEqual(data['failed'], 0)
        # Verify tasks were saved to database
        self.assertEqual(Task.objects.filter(title='Analyzed Task 1').count(), 1)
    
    def test_delete_task(self):
        """Test deleting a task"""
        task_id = self.task1.id
        response = self.client.delete(reverse('tasks:delete_task', args=[task_id]))
        self.assertEqual(response.status_code, 200)
        # Verify task was deleted
        self.assertEqual(Task.objects.filter(id=task_id).count(), 0)
    
    def test_delete_nonexistent_task(self):
        """Test deleting a task that doesn't exist"""
        response = self.client.delete(reverse('tasks:delete_task', args=[9999]))
        self.assertEqual(response.status_code, 404)


# ============================================
# INTEGRATION TESTS
# ============================================

class TaskIntegrationTest(TestCase):
    """Test complete workflows"""
    
    def setUp(self):
        """Setup for integration tests"""
        self.client = Client()
        self.today = date.today()
    
    def test_complete_workflow(self):
        """Test complete workflow: analyze -> save -> list -> delete"""
        # 1. Analyze tasks
        analyze_payload = {
            'tasks': [
                {
                    'title': 'Workflow Task 1',
                    'due_date': str(self.today + timedelta(days=1)),
                    'importance': 8,
                    'estimated_hours': 2,
                    'dependencies': []
                }
            ]
        }
        analyze_response = self.client.post(
            reverse('tasks:analyze'),
            data=json.dumps(analyze_payload),
            content_type='application/json'
        )
        self.assertEqual(analyze_response.status_code, 200)
        
        # 2. Save analyzed tasks
        save_response = self.client.post(
            reverse('tasks:save_analysis'),
            data=json.dumps(analyze_payload),
            content_type='application/json'
        )
        self.assertEqual(save_response.status_code, 200)
        
        # 3. List tasks
        list_response = self.client.get(reverse('tasks:task_list'))
        self.assertEqual(list_response.status_code, 200)
        tasks = list_response.json()
        self.assertGreater(len(tasks), 0)
        
        # 4. Delete task
        task_id = tasks[0]['id']
        delete_response = self.client.delete(reverse('tasks:delete_task', args=[task_id]))
        self.assertEqual(delete_response.status_code, 200)
        
        # 5. Verify deletion
        final_list = self.client.get(reverse('tasks:task_list')).json()
        self.assertEqual(len(final_list), len(tasks) - 1)
    
    def test_scoring_consistency(self):
        """Test that scoring is consistent across analyze and save"""
        task_data = {
            'title': 'Consistency Check',
            'due_date': str(self.today + timedelta(days=2)),
            'importance': 7,
            'estimated_hours': 2,
            'dependencies': []
        }
        
        # Analyze it
        analyze_response = self.client.post(
            reverse('tasks:analyze'),
            data=json.dumps({'tasks': [task_data]}),
            content_type='application/json'
        )
        analyzed_score = analyze_response.json()['tasks'][0]['score']
        
        # Calculate score directly
        direct_score = calculate_task_score({
            'due_date': self.today + timedelta(days=2),
            'importance': 7,
            'estimated_hours': 2,
            'dependencies': []
        })
        
        # Should match
        self.assertEqual(analyzed_score, direct_score)
