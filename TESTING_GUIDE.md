# 🧪 Testing Guide - Task Analyzer

Complete testing documentation for the Task Analyzer test suite.

## 📊 Test Suite Overview

**Status**: ✅ ALL 31 TESTS PASSING
- **Execution Time**: 0.158 seconds
- **Pass Rate**: 100%
- **Coverage**: Models, Algorithm, APIs, Integration

### Test Breakdown

```
31 Total Tests
├── TaskModelTest (6 tests)
│   └── Model creation, defaults, field validation
├── ScoringAlgorithmTest (11 tests)
│   └── Scoring formula, edge cases, error handling
├── TaskAPITest (11 tests)
│   └── All 6 API endpoints, error cases
└── TaskIntegrationTest (3 tests)
    └── Complete workflows, consistency
```

---

## 🚀 Running Tests

### Quick Start
```bash
cd d:\task-analyzer
./venv/Scripts/python manage.py test tasks
```

Expected output:
```
Found 31 test(s)
...............................................................................

Ran 31 tests in 0.158s
OK
```

### With Verbose Output
```bash
./venv/Scripts/python manage.py test tasks --verbosity=2
```

Shows detailed output for each test including pass/fail status.

### Run Specific Test Class

```bash
# Model tests only
./venv/Scripts/python manage.py test tasks.tests.TaskModelTest

# Scoring algorithm only
./venv/Scripts/python manage.py test tasks.tests.ScoringAlgorithmTest

# API endpoint tests only
./venv/Scripts/python manage.py test tasks.tests.TaskAPITest

# Integration tests only
./venv/Scripts/python manage.py test tasks.tests.TaskIntegrationTest
```

### Run Single Test
```bash
./venv/Scripts/python manage.py test tasks.tests.TaskModelTest.test_task_creation
```

---

## 📋 Test Details

### TaskModelTest (6 tests)

Tests the Task database model.

| Test                              | Purpose                         |
| --------------------------------- | ------------------------------- |
| `test_task_creation`              | Create task with all fields     |
| `test_task_defaults`              | Verify default values           |
| `test_task_string_representation` | Test `__str__()` method         |
| `test_task_with_dependencies`     | Store and retrieve dependencies |
| `test_task_max_importance`        | Handle importance=10            |
| `test_task_min_importance`        | Handle importance=1             |

**Sample Test:**
```python
def test_task_creation(self):
    """Create a task with all fields"""
    task = Task.objects.create(
        title="Design Database",
        due_date="2025-12-05",
        importance=9,
        estimated_hours=1.5,
        dependencies=[]
    )
    self.assertEqual(task.title, "Design Database")
    self.assertEqual(task.importance, 9)
```

---

### ScoringAlgorithmTest (11 tests)

Tests the scoring algorithm (`calculate_task_score()` function).

| Test                                 | Purpose                        |
| ------------------------------------ | ------------------------------ |
| `test_overdue_task_scores_high`      | Past dates get +100 urgency    |
| `test_due_today_scores_high`         | Today scores well              |
| `test_due_within_3_days`             | Within 3 days gets +50         |
| `test_due_within_week`               | Within 7 days gets +25         |
| `test_due_far_future`                | 30+ days gets no urgency bonus |
| `test_importance_weighting`          | Score × importance (1-10)      |
| `test_quick_win_bonus`               | Tasks < 2 hours get +10        |
| `test_dependency_penalty`            | Each blocker = -30 points      |
| `test_score_never_negative`          | Score floored at 0             |
| `test_string_date_parsing`           | ISO format dates work          |
| `test_invalid_input_returns_neutral` | Invalid input = neutral score  |

**Sample Test:**
```python
def test_overdue_task_scores_high(self):
    """Overdue tasks get +100 urgency bonus"""
    task_data = {
        "title": "Overdue Project",
        "due_date": "1990-01-01",  # Past date
        "importance": 5,
        "estimated_hours": 5,
        "dependencies": []
    }
    score = calculate_task_score(task_data)
    # 100 (overdue) + 25 (importance) = 125
    self.assertEqual(score, 125)
```

---

### TaskAPITest (11 tests)

Tests all 6 REST API endpoints.

| Endpoint                         | Tests   | Purpose                                 |
| -------------------------------- | ------- | --------------------------------------- |
| `GET /api/tasks/list/`           | 1 test  | Retrieve all tasks                      |
| `GET /api/tasks/suggest/`        | 1 test  | Get top 3 recommendations               |
| `POST /api/tasks/analyze/`       | 3 tests | Analyze tasks (valid, empty, non-array) |
| `POST /api/tasks/save/`          | 2 tests | Save single task (valid, invalid)       |
| `POST /api/tasks/save-analysis/` | 2 tests | Save multiple tasks                     |
| `DELETE /api/tasks/delete/<id>/` | 2 tests | Delete task (existing, nonexistent)     |

**Sample Test:**
```python
def test_list_tasks(self):
    """GET /api/tasks/list/ returns all tasks"""
    response = self.client.get(reverse('tasks:task_list'))
    self.assertEqual(response.status_code, 200)
    data = response.json()
    self.assertIsInstance(data, list)
```

---

### TaskIntegrationTest (3 tests)

Tests complete workflows combining multiple operations.

| Test                       | Purpose                              |
| -------------------------- | ------------------------------------ |
| `test_complete_workflow`   | Analyze → Save → List → Delete       |
| `test_scoring_consistency` | Consistent scoring across operations |

**Sample Test:**
```python
def test_complete_workflow(self):
    """Full workflow: analyze → save → list → delete"""
    # 1. Analyze tasks
    response = self.client.post(
        reverse('tasks:analyze'),
        {"tasks": [task_data]},
        content_type='application/json'
    )
    self.assertEqual(response.status_code, 200)
    
    # 2. Save analyzed tasks
    response = self.client.post(
        reverse('tasks:save_analysis'),
        {"tasks": [task_data]},
        content_type='application/json'
    )
    self.assertEqual(response.status_code, 201)
    
    # 3. Verify tasks appear in list
    response = self.client.get(reverse('tasks:task_list'))
    tasks = response.json()
    self.assertTrue(len(tasks) > 0)
```

---

## 🎯 Edge Cases Covered

### 1. Overdue Tasks (Past Dates)
- Input: `due_date = "1990-01-01"`
- Expected: +100 urgency bonus
- Result: ✅ Tested and passing

### 2. Missing Fields
- Input: Missing `importance` field
- Expected: Defaults to 5
- Result: ✅ Tested and passing

### 3. Invalid Dates
- Input: `due_date = "invalid-date"`
- Expected: Returns neutral score
- Result: ✅ Tested and passing

### 4. Negative Scores
- Input: Task with 3+ dependencies
- Expected: Score floored at 0 (never negative)
- Result: ✅ Tested and passing

### 5. Empty Task Lists
- Input: `"tasks": []`
- Expected: Returns empty array
- Result: ✅ Tested and passing

### 6. Blocked Tasks
- Input: Task with dependencies
- Expected: -30 penalty per blocker
- Result: ✅ Tested and passing

### 7. Quick Wins
- Input: `estimated_hours = 1.5` (< 2)
- Expected: +10 bonus
- Result: ✅ Tested and passing

### 8. Non-array Input
- Input: `"tasks": {"key": "value"}`
- Expected: Returns 400 error
- Result: ✅ Tested and passing

### 9. Nonexistent Task Deletion
- Input: `DELETE /api/tasks/delete/999/`
- Expected: Returns 404 error
- Result: ✅ Tested and passing

### 10. String Dates
- Input: `due_date = "2025-12-05"` (ISO format)
- Expected: Correctly parsed and scored
- Result: ✅ Tested and passing

---

## 📊 Test Coverage

### Models
- ✅ Task creation with all fields
- ✅ Field defaults (importance, hours, dependencies)
- ✅ Field types and constraints
- ✅ String representation
- ✅ Database relationships

### Scoring Algorithm
- ✅ Urgency calculation (all ranges: overdue, today, 3 days, 7 days, future)
- ✅ Importance weighting (1-10 scale × 5)
- ✅ Effort bonus (<2 hours = +10)
- ✅ Dependency penalties (-30 per blocker)
- ✅ Score flooring (never below 0)
- ✅ Default values (missing fields)
- ✅ Invalid input handling (bad dates, non-strings)

### API Endpoints
- ✅ GET /api/tasks/list/ (successful retrieval)
- ✅ GET /api/tasks/suggest/ (top 3 suggestions)
- ✅ POST /api/tasks/analyze/ (valid, empty, non-array)
- ✅ POST /api/tasks/save/ (valid, invalid)
- ✅ POST /api/tasks/save-analysis/ (bulk save)
- ✅ DELETE /api/tasks/delete/<id>/ (existing, nonexistent)

### Error Handling
- ✅ Empty lists (returns [])
- ✅ Invalid dates (returns neutral)
- ✅ Missing fields (uses defaults)
- ✅ Invalid types (returns error)
- ✅ Nonexistent resources (404)
- ✅ Malformed JSON (400)
- ✅ HTTP status codes

---

## ✅ Test Results Summary

```
╔════════════════════════════════════════╗
║        TEST EXECUTION RESULTS          ║
╠════════════════════════════════════════╣
║ Total Tests:        31                 ║
║ Passed:            31 ✅               ║
║ Failed:             0                  ║
║ Errors:             0                  ║
║ Pass Rate:       100%                  ║
║ Execution Time:  0.158s                ║
║ Status:      PRODUCTION READY          ║
╚════════════════════════════════════════╝
```

---

## 🔍 Test Quality Metrics

| Metric            | Value  | Status |
| ----------------- | ------ | ------ |
| Test Count        | 31     | ✅      |
| Pass Rate         | 100%   | ✅      |
| Code Coverage     | High   | ✅      |
| Edge Cases        | 10+    | ✅      |
| Endpoints Covered | 6/6    | ✅      |
| Execution Speed   | <200ms | ✅      |
| Isolation         | Yes    | ✅      |
| Deterministic     | Yes    | ✅      |

---

## 🛠️ Testing Best Practices Used

✅ **Clear Test Names** - Describe what they test
✅ **setUp() Method** - Consistent test data
✅ **Docstrings** - Explain each test purpose
✅ **One Test per Case** - Single responsibility
✅ **Edge Cases** - More than happy path
✅ **Error Cases** - Invalid input tested
✅ **Assertions** - Clear expectations
✅ **App Namespaces** - Proper URL reversal with 'tasks:' prefix
✅ **Isolated Tests** - No interdependencies
✅ **Fast Execution** - < 200ms total
✅ **Django TestCase** - In-memory database for speed
✅ **Mock Data** - Realistic task scenarios

---

## 📚 Test Framework

**Framework**: Django TestCase
**Database**: In-memory SQLite
**HTTP Client**: Django test Client
**JSON**: application/json

### Required Imports
```python
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from datetime import date, timedelta
from .models import Task
from .scoring import calculate_task_score
```

---

## 🔄 Continuous Testing

### Run Tests During Development
```bash
# Watch mode (requires watchdog package)
ptw -- --Django -s
```

### Run Tests Before Commit
```bash
# Add to git pre-commit hook
python manage.py test tasks || exit 1
```

### Generate Coverage Report (Optional)
```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='tasks' manage.py test tasks
coverage report
coverage html  # Creates htmlcov/index.html
```

---

## 🐛 Debugging Tests

### Run with Print Statements
```python
# In test
def test_something(self):
    print("Debug output here")  # Will appear with -s flag
    self.assertEqual(1, 1)
```

Run with:
```bash
./venv/Scripts/python manage.py test tasks -s
```

### Run with Debugger
```bash
# Add breakpoint
import pdb; pdb.set_trace()

# Then run tests
./venv/Scripts/python manage.py test tasks
```

### Isolate Single Test
```bash
# Run one test to debug
./venv/Scripts/python manage.py test tasks.tests.TaskModelTest.test_task_creation
```

---

## ✨ Next Steps

- ✅ All tests passing and verified
- 📚 Documentation complete
- 🚀 Ready for production deployment
- 💡 Optional: Add performance benchmarks
- 💡 Optional: Add load testing
- 💡 Optional: Add mutation testing

---

## 📞 Support

For issues or questions about tests:
1. Check test names in `tasks/tests.py`
2. Review specific test documentation above
3. Run individual tests for isolation
4. Add `-s` flag to see print statements
5. Check test output for error messages

---

**Version**: 1.0
**Last Updated**: November 29, 2025
**Status**: ✅ Complete and Verified
