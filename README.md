# 📋 Task Analyzer - Smart Priority Management

A Django + React-based task prioritization system that analyzes your tasks and recommends the best ones to work on today based on urgency, importance, and effort.

## 🎯 Overview

Task Analyzer implements an intelligent scoring algorithm that evaluates tasks across multiple dimensions to provide smart prioritization. It helps you answer the critical question: **"What should I work on right now?"**

### Key Features
- **Smart Scoring Algorithm** - Prioritizes tasks using urgency, importance, and effort metrics
- **Multiple Sorting Strategies** - Choose between priority score, deadline, quick wins, or importance
- **Daily Recommendations** - Get top 3 tasks recommended for "today" with explanations
- **Dependency Tracking** - Understand task dependencies and their impact on priority
- **Color-Coded UI** - Visual priority indicators (Red=Critical, Orange=High, Purple=Medium, Green=Low)
- **REST API** - Full API for task analysis and suggestions

---

## 🧮 Scoring Algorithm

The heart of Task Analyzer is the **Priority Scoring Algorithm**. Here's how it works:

### Scoring Breakdown

Each task receives a numerical score calculated from four factors:

```
PRIORITY_SCORE = URGENCY + IMPORTANCE_WEIGHT + EFFORT_BONUS - DEPENDENCY_PENALTY
```

#### 1. **URGENCY** (Most Important Factor: +25 to +100 points)

| Condition          | Points | Reasoning                                        |
| ------------------ | ------ | ------------------------------------------------ |
| Overdue (days < 0) | +100   | Task is already late - needs immediate attention |
| Due within 3 days  | +50    | Approaching deadline - high priority             |
| Due within 7 days  | +25    | Within the week - moderate urgency               |
| Beyond 7 days      | 0      | Lower urgency - can be deferred                  |

**Why Urgency is weighted most heavily:** Time is a hard constraint. Tasks with approaching deadlines create cascade risks - missing one deadline often blocks multiple other tasks.

#### 2. **IMPORTANCE WEIGHTING** (+5 to +50 points)

```
IMPORTANCE_SCORE = importance_level × 5
```

- Scale: 1-10 (user-defined)
- Maximum contribution: 50 points
- Applied to all tasks regardless of due date

**Why we multiply by 5:** A task's inherent importance should significantly influence priority, but not override urgency. The 5x multiplier gives importance substantial weight while maintaining urgency as the primary driver.

#### 3. **EFFORT BONUS** (+10 bonus for quick wins)

```
if estimated_hours < 2:
    EFFORT_BONUS = +10
else:
    EFFORT_BONUS = 0
```

**Why quick wins matter:** 
- Psychological momentum: Completing small tasks builds motivation
- Efficiency: Quick wins help you accumulate progress
- Context switching cost: Tasks under 2 hours minimize disruption
- However: We don't penalize longer tasks; we only reward quick wins

#### 4. **DEPENDENCY PENALTY** (-30 per dependency)

```
DEPENDENCY_PENALTY = number_of_dependencies × 30
```

**Why we penalize dependencies:**
- Blocked tasks should have lower priority until their dependencies are resolved
- Encourages completing "blocker" tasks first
- Prevents planning fallacies where you plan to work on tasks that are still blocked

### Example Scoring

**Task A: "Project Report"**
- Due: 2025-12-01 (3 days away) → +50 (urgency)
- Importance: 8/10 → 8 × 5 = +40 (importance)
- Estimated hours: 3 → 0 (no quick win bonus)
- Dependencies: 0 → 0 (no penalty)
- **TOTAL SCORE: 90** (High priority - Medium color)

**Task B: "Email Client"**
- Due: 2025-12-05 (7 days away) → +25 (urgency)
- Importance: 5/10 → 5 × 5 = +25 (importance)
- Estimated hours: 1 → +10 (quick win bonus!)
- Dependencies: 0 → 0 (no penalty)
- **TOTAL SCORE: 60** (Medium priority - Green color)

**Task C: "Review Code" (blocked)**
- Due: 2025-12-03 (5 days away) → +50 (urgency)
- Importance: 7/10 → 7 × 5 = +35 (importance)
- Estimated hours: 2 → 0 (no quick win bonus)
- Dependencies: [2, 4] → -60 (blocking penalty!)
- **TOTAL SCORE: 25** (Low priority - blocked, wait for dependencies)

### Priority Color Coding

| Score Range | Color             | Meaning                       | Recommendation     |
| ----------- | ----------------- | ----------------------------- | ------------------ |
| ≥ 150       | 🔴 Red (Critical)  | Overdue or very urgent        | Do immediately     |
| 100-149     | 🟠 Orange (High)   | Due soon with high importance | Do today           |
| 50-99       | 🟣 Purple (Medium) | Moderate urgency/importance   | Plan for this week |
| < 50        | 🟢 Green (Low)     | Low priority or far future    | Schedule later     |

---

## 📊 Sorting Strategies

The frontend allows you to re-sort results by different criteria:

1. **Priority Score** (Default) - Uses the algorithm above
2. **Deadline Driven** - Earliest due date first
3. **Fastest Wins** - Shortest duration first (best for productivity)
4. **Importance First** - Highest importance level first

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/Rupesh-Darimisetti/task-analyzer.git
cd task-analyzer
```

### Step 2: Create and Activate Virtual Environment

**On Windows (Git Bash):**
```bash
python -m venv venv
source venv/Scripts/activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install manually:
```bash
pip install django==5.2.8 djangorestframework
```

### Step 4: Initialize Database

```bash
python manage.py migrate
```

### Step 5: Run the Development Server

```bash
python manage.py runserver
```

The server will start at: **http://127.0.0.1:8000/**

### Step 6: Access the Frontend

Open `frontend/index.html` in your browser, or serve it via a local HTTP server:

```bash
# Using Python (Windows, macOS, Linux)
python -m http.server 8001 --directory frontend
```

Then visit: **http://127.0.0.1:8001/**

---

## 🔌 API Endpoints

### 1. POST `/api/tasks/analyze/`

**Analyze and score a list of tasks**

**Request:**
```json
{
  "tasks": [
    {
      "title": "Project Report",
      "due_date": "2025-12-01",
      "importance": 8,
      "estimated_hours": 3,
      "dependencies": []
    },
    {
      "title": "Email Client",
      "due_date": "2025-12-05",
      "importance": 5,
      "estimated_hours": 1,
      "dependencies": []
    }
  ]
}
```

**Response:**
```json
{
  "count": 2,
  "tasks": [
    {
      "title": "Project Report",
      "due_date": "2025-12-01",
      "importance": 8,
      "estimated_hours": 3,
      "dependencies": [],
      "score": 90
    },
    {
      "title": "Email Client",
      "due_date": "2025-12-05",
      "importance": 5,
      "estimated_hours": 1,
      "dependencies": [],
      "score": 60
    }
  ]
}
```

---

### 2. GET `/api/tasks/suggest/`

**Get top 3 recommended tasks for today with explanations**

**Response:**
```json
{
  "count": 3,
  "today": "2025-11-29",
  "top_tasks": [
    {
      "id": 1,
      "title": "Project Report",
      "due_date": "2025-12-01",
      "importance": 8,
      "estimated_hours": 3,
      "priority_score": 90,
      "explanation": "Due in 2 day(s). High urgency. This task needs immediate attention based on your deadline."
    },
    {
      "id": 2,
      "title": "Email Client",
      "due_date": "2025-12-05",
      "importance": 5,
      "estimated_hours": 1,
      "priority_score": 60,
      "explanation": "Due in 6 day(s). Quick win - can be completed in under 2 hours."
    },
    {
      "id": 3,
      "title": "Code Review",
      "due_date": "2025-12-10",
      "importance": 6,
      "estimated_hours": 2,
      "priority_score": 50,
      "explanation": "Due in 11 day(s). Important task that should be scheduled this week."
    }
  ]
}
```

---

### 3. GET `/api/tasks/list/`

**Get all tasks from the database**

**Response:**
```json
[
  {
    "id": 1,
    "title": "Project Report",
    "due_date": "2025-12-01",
    "importance": 8,
    "estimated_hours": 3,
    "dependencies": []
  },
  ...
]
```

---

## 🧪 Edge Case Handling

The application handles several edge cases gracefully:

### 1. **Past Due Dates**

```json
{
  "title": "Old Task from 1990",
  "due_date": "1990-01-01",
  "importance": 5,
  "estimated_hours": 2,
  "dependencies": []
}
```

**Result:** Score gets +100 (OVERDUE bonus), marking it as critical priority (🔴 Red)
**Explanation:** The algorithm assumes any past date is equally overdue and applies maximum urgency weight

### 2. **Missing Importance**

If `importance` is missing or null, the algorithm:
- Uses default value of 5 (medium importance) from the Task model
- Continues processing without errors
- Returns a valid score

### 3. **Invalid Importance Values**

- **Out of range (< 1):** Frontend validation prevents submission; backend treats as is (can result in negative scores)
- **Out of range (> 10):** Frontend validation prevents submission; can result in scores > 50 for importance
- **Non-numeric:** Model validation catches this and returns 400 error

### 4. **Zero Estimated Hours**

```json
{
  "title": "Instant Task",
  "due_date": "2025-12-01",
  "importance": 5,
  "estimated_hours": 0,
  "dependencies": []
}
```

**Result:** Gets quick win bonus (+10) since 0 < 2
**Explanation:** Task that takes no time should definitely be done!

### 5. **Circular Dependencies** (Not Currently Handled)

The current implementation does not validate for circular dependencies. Future enhancement could include:
```python
def has_circular_dependency(task_id, dependencies, task_map):
    visited = set()
    def dfs(current):
        if current in visited:
            return True
        visited.add(current)
        for dep in task_map.get(current, []):
            if dfs(dep):
                return True
        return False
    return dfs(task_id)
```

---

## 📁 Project Structure

```
task-analyzer/
├── backend/                   # Django project settings
│   ├── settings.py           # Configuration
│   ├── urls.py              # Main URL routing
│   ├── asgi.py              # ASGI config
│   └── wsgi.py              # WSGI config
├── tasks/                     # Django app for task management
│   ├── models.py            # Task database model
│   ├── views.py             # API endpoints (analyze, suggest, list)
│   ├── scoring.py           # Priority scoring algorithm ⭐
│   ├── serializers.py       # Django REST Framework serializers
│   ├── urls.py              # Task app URL routing
│   ├── admin.py             # Django admin configuration
│   └── migrations/          # Database migrations
├── frontend/                  # Frontend files
│   ├── index.html           # Main UI
│   ├── styles.css           # Styling with color-coded priorities
│   └── scripts.js           # JavaScript logic & fetch calls
├── db.sqlite3               # SQLite database
├── manage.py                # Django management script
└── README.md                # This file
```

---

## 🔍 Design Decisions & Rationale

### Why Urgency Over Effort?

**Q:** Why is urgency weighted so heavily compared to effort?

**A:** In task management, **time is the ultimate constraint**. Here's why:

1. **Hard Deadlines:** A task with a deadline in 2 hours must be done before then, regardless of effort
2. **Cascade Effects:** Missing a deadline often blocks other dependent tasks and creates scheduling chaos
3. **Motivation:** Overdue tasks create stress and mental burden, reducing overall productivity
4. **Reversibility:** You can always postpone a low-urgency task; you cannot postpone a deadline once it's passed

**Example:** A 10-hour task due in 1 day is universally higher priority than a 30-minute task due in 2 months.

### Why Penalize Dependencies?

**Q:** Why does Task C get a negative penalty for having dependencies?

**A:** This prevents the "Planning Fallacy":

- **Problem:** Without penalties, blocked tasks would rank high, leading to wasted planning and context switching
- **Solution:** By penalizing dependencies, we naturally bubble up "blocker" tasks to the top
- **Result:** You work on tasks that unblock others first, creating a natural workflow

---

## 🚀 Future Enhancements

Potential improvements for v2.0:

- [ ] **Circular dependency detection** - Warn users about impossible task orderings
- [ ] **Recurring tasks** - Support weekly/daily tasks
- [ ] **Time-tracking integration** - Actual vs. estimated hours comparison
- [ ] **Machine learning** - Learn from user behavior to improve estimates
- [ ] **Collaboration** - Multi-user task assignment and team views
- [ ] **Mobile app** - React Native version for mobile devices
- [ ] **Export features** - Generate reports and calendar exports
- [ ] **Persistence** - Save tasks to database and retrieve them
- [ ] **Authentication** - User accounts and task privacy

---

## 📝 Example Workflows

### Workflow 1: Morning Planning

1. Open frontend at `http://127.0.0.1:8001/`
2. Click "💡 Get Suggestions"
3. See top 3 tasks recommended for today with explanations
4. Plan your day based on recommendations

### Workflow 2: Task Analysis

1. Paste a JSON array of tasks
2. Click "🚀 Analyze Tasks"
3. Select sorting strategy (Priority Score, Deadline, Quick Wins, etc.)
4. Review results with color-coded priorities
5. Identify which tasks to tackle first

### Workflow 3: Adding Individual Tasks

1. Fill in the form on the left side:
   - Task title
   - Due date
   - Importance (1-10)
   - Estimated hours
   - Dependencies (if any)
2. Click "Add Task"
3. Task is added to the JSON array
4. Click "Analyze Tasks" to see updated priorities

---

## 🐛 Troubleshooting

### Server won't start: "No module named 'rest_framework'"

```bash
./venv/Scripts/pip install djangorestframework
```

### CORS errors in frontend

Add to `backend/settings.py`:
```python
INSTALLED_APPS = [
    ...
    "corsheaders",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8001",
    "http://localhost:8001",
]
```

Then install: `pip install django-cors-headers`

### Tasks not appearing in `/api/tasks/suggest/`

The endpoint fetches from the database. You need to:
1. Create tasks via Django admin: `http://127.0.0.1:8000/admin/`
2. Or save tasks programmatically via the API

---

## 📚 Technologies Used

- **Backend:** Django 5.2.8, Django REST Framework
- **Frontend:** Vanilla JavaScript (ES6), HTML5, CSS3
- **Database:** SQLite3
- **API:** RESTful architecture with JSON

---

## 📄 License

This project is open-source and available under the MIT License.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📧 Contact

For questions or suggestions, reach out to: **Rupesh Darimisetti**

Repository: https://github.com/Rupesh-Darimisetti/task-analyzer

---

**Happy task analyzing! 🎯**
