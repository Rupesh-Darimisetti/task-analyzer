// ============================================
// TASK ANALYZER - INTERACTIVE JAVASCRIPT
// ============================================

const API_BASE = 'http://127.0.0.1:8000/api/tasks';

// DOM Elements
const taskInput = document.getElementById('taskInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const suggestBtn = document.getElementById('suggestBtn');
const sortingStrategy = document.getElementById('sortingStrategy');
const taskForm = document.getElementById('taskForm');
const resultsContainer = document.getElementById('resultsContainer');
const errorContainer = document.getElementById('errorContainer');
const errorText = document.getElementById('errorText');
const loadingContainer = document.getElementById('loadingContainer');
const resultCount = document.getElementById('resultCount');
const explanationPanel = document.getElementById('explanationPanel');
const explanationContent = document.getElementById('explanationContent');

// Event Listeners
analyzeBtn.addEventListener('click', analyzeTasks);
suggestBtn.addEventListener('click', getSuggestions);
taskForm.addEventListener('submit', addTaskToInput);

// Load tasks from database on page load
document.addEventListener('DOMContentLoaded', function () {
    console.log('✅ Task Analyzer loaded successfully!');
    console.log(`📡 API Base: ${API_BASE}`);
    loadTasksFromDatabase();
});

// ============================================
// LOAD TASKS FROM DATABASE
// ============================================

async function loadTasksFromDatabase() {
    try {
        const response = await fetch(`${API_BASE}/list/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            console.log('No tasks in database yet');
            return;
        }

        const tasks = await response.json();

        if (tasks.length > 0) {
            // Display loaded tasks with scores
            const scoredTasks = tasks.map(task => ({
                ...task,
                score: 0  // Will be scored if needed
            }));

            resultCount.textContent = `${tasks.length} tasks (from database)`;
            displayResults(scoredTasks);

            // Also populate the textarea with JSON for editing
            taskInput.value = JSON.stringify(tasks, null, 2);

            console.log(`✅ Loaded ${tasks.length} tasks from database`);
        }
    } catch (error) {
        console.log('Could not load tasks from database:', error.message);
    }
}

// ============================================
// PARSE AND READ INPUT DATA
// ============================================

function getTasksFromInput() {
    const input = taskInput.value.trim();

    if (!input) {
        showError('Please enter tasks or add a task using the form.');
        return null;
    }

    try {
        const tasks = JSON.parse(input);

        if (!Array.isArray(tasks)) {
            showError('Tasks must be a JSON array.');
            return null;
        }

        return tasks;
    } catch (error) {
        showError(`Invalid JSON format: ${error.message}`);
        return null;
    }
}

// Remove duplicate tasks based on title, due_date, importance, estimated_hours, dependencies
function dedupeTasks(tasks) {
    const seen = new Map();
    const result = [];

    for (const t of tasks) {
        const key = [
            (t.title || '').trim().toLowerCase(),
            t.due_date || '',
            String(t.importance || ''),
            String(t.estimated_hours || ''),
            JSON.stringify(t.dependencies || [])
        ].join('||');

        if (!seen.has(key)) {
            seen.set(key, true);
            result.push(t);
        }
    }

    if (result.length !== tasks.length) {
        console.log(`Deduplicated tasks: ${tasks.length} -> ${result.length}`);
    }

    return result;
}

// ============================================
// ADD INDIVIDUAL TASK TO INPUT
// ============================================

function addTaskToInput(e) {
    e.preventDefault();

    const title = document.getElementById('title').value;
    const dueDate = document.getElementById('dueDate').value;
    const importance = parseInt(document.getElementById('importance').value);
    const estimatedHours = parseFloat(document.getElementById('estimatedHours').value);
    const dependenciesInput = document.getElementById('dependencies').value;

    // Parse dependencies
    const dependencies = dependenciesInput
        ? dependenciesInput.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id))
        : [];

    const newTask = {
        title,
        due_date: dueDate,
        importance,
        estimated_hours: estimatedHours,
        dependencies
    };

    // Get existing tasks from textarea
    let tasks = [];
    if (taskInput.value.trim()) {
        try {
            tasks = JSON.parse(taskInput.value);
        } catch (error) {
            showError('Could not parse existing tasks. Please fix the JSON.');
            return;
        }
    }

    // Add new task
    tasks.push(newTask);

    // Update textarea
    taskInput.value = JSON.stringify(tasks, null, 2);

    // Reset form
    taskForm.reset();
    document.getElementById('importance').value = 5;
    document.getElementById('estimatedHours').value = 1;

    // Show success feedback
    showSuccess(`Task "${title}" added successfully!`);
}

// ============================================
// ANALYZE TASKS - MAIN FUNCTION
// ============================================

async function analyzeTasks() {
    clearMessages();
    showLoading(true);

    const tasks = getTasksFromInput();
    if (!tasks) {
        showLoading(false);
        return;
    }

    // Deduplicate input tasks to avoid duplicate entries (based on key fields)
    const dedupedInput = dedupeTasks(tasks);

    try {
        const response = await fetch(`${API_BASE}/analyze/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ tasks: dedupedInput })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Apply sorting strategy
        const sortedTasks = applySortingStrategy(data.tasks);

        // Display results
        displayResults(sortedTasks);

        // Save only new tasks (those without an `id`) to avoid duplicates in DB
        const newTasksToSave = sortedTasks.filter(t => !t.id && !(t.saved === true));
        if (newTasksToSave.length > 0) {
            await saveTasksToDatabase(newTasksToSave);
        } else {
            console.log('No new tasks to save (all tasks already have IDs)');
        }

        showLoading(false);
    } catch (error) {
        showError(`Failed to analyze tasks: ${error.message}`);
        showLoading(false);
    }
}

// ============================================
// GET SUGGESTIONS FOR TODAY
// ============================================

async function getSuggestions() {
    clearMessages();
    showLoading(true);

    try {
        const response = await fetch(`${API_BASE}/suggest/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Display suggestions
        displaySuggestions(data);

        showLoading(false);
    } catch (error) {
        showError(`Failed to get suggestions: ${error.message}`);
        showLoading(false);
    }
}

// ============================================
// APPLY SORTING STRATEGY
// ============================================

function applySortingStrategy(tasks) {
    const strategy = sortingStrategy.value;
    const tasksCopy = [...tasks];

    switch (strategy) {
        case 'deadline':
            // Sort by due date (earliest first)
            return tasksCopy.sort((a, b) => {
                const dateA = new Date(a.due_date);
                const dateB = new Date(b.due_date);
                return dateA - dateB;
            });

        case 'quickWins':
            // Sort by estimated hours (shortest first)
            return tasksCopy.sort((a, b) => a.estimated_hours - b.estimated_hours);

        case 'importance':
            // Sort by importance (highest first)
            return tasksCopy.sort((a, b) => b.importance - a.importance);

        case 'priority':
            return tasksCopy.sort((a, b) => (a.priority - b.priority))
        default:
            // Sort by score (highest first) - default
            return tasksCopy.sort((a, b) => (b.score || 0) - (a.score || 0));
    }
}

// ============================================
// DISPLAY RESULTS
// ============================================

function displayResults(tasks) {
    clearMessages();
    explanationPanel.style.display = 'none';

    if (!tasks || tasks.length === 0) {
        resultsContainer.innerHTML = '<div class="no-results"><p>No tasks to display</p></div>';
        resultCount.textContent = '0 tasks';
        return;
    }

    resultCount.textContent = `${tasks.length} tasks`;
    resultsContainer.innerHTML = '';

    tasks.forEach((task, index) => {
        const card = createTaskCard(task, index + 1);
        resultsContainer.appendChild(card);
    });
}

// ============================================
// CREATE TASK CARD
// ============================================

function createTaskCard(task, rank) {
    const card = document.createElement('div');
    card.className = 'task-card';

    // Determine priority level and color
    const score = task.score || 0;
    let priorityClass = 'priority-low';
    let scoreClass = 'score-low';

    if (score >= 150) {
        priorityClass = 'priority-critical';
        scoreClass = 'score-critical';
    } else if (score >= 100) {
        priorityClass = 'priority-high';
        scoreClass = 'score-high';
    } else if (score >= 50) {
        priorityClass = 'priority-medium';
        scoreClass = 'score-medium';
    }

    card.classList.add(priorityClass);

    // Calculate days until due
    const today = new Date();
    const dueDate = new Date(task.due_date);
    const daysUntilDue = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));

    let dueStatus = '';
    if (daysUntilDue < 0) {
        dueStatus = `⚠️ OVERDUE (${Math.abs(daysUntilDue)} days)`;
    } else if (daysUntilDue === 0) {
        dueStatus = '🔴 Due TODAY';
    } else if (daysUntilDue <= 3) {
        dueStatus = `⏰ Due in ${daysUntilDue} day(s)`;
    } else {
        dueStatus = `📅 Due in ${daysUntilDue} days`;
    }

    // Build card HTML with delete button if task has ID
    const deleteBtn = task.id ? `<button class="delete-btn" onclick="deleteTaskFromDatabase(${task.id})">🗑️ Delete</button>` : '';

    card.innerHTML = `
        <div class="task-header">
            <h3 class="task-title">#${rank} ${task.title || 'Untitled Task'}</h3>
            <span class="task-score ${scoreClass}">${Math.round(score)}</span>
        </div>
        
        <div class="task-meta">
            <div class="meta-item">
                <strong>⏱️ Effort:</strong> ${task.estimated_hours}h
            </div>
            <div class="meta-item">
                <strong>⭐ Importance:</strong> ${task.importance}/10
            </div>
            <div class="meta-item">
                <strong>📌 Status:</strong> ${dueStatus}
            </div>
        </div>
        
        ${task.dependencies && task.dependencies.length > 0 ? `
            <div class="task-dependencies">
                <strong>🔗 Dependencies:</strong> ${task.dependencies.join(', ')}
            </div>
        ` : ''}

        ${deleteBtn}
    `;

    return card;
}

// ============================================
// DISPLAY SUGGESTIONS
// ============================================

function displaySuggestions(data) {
    resultsContainer.innerHTML = '';
    resultCount.textContent = `${data.count} recommendations`;

    explanationPanel.style.display = 'block';
    explanationContent.innerHTML = '';

    if (!data.top_tasks || data.top_tasks.length === 0) {
        explanationContent.innerHTML = '<p>No tasks found for today.</p>';
        return;
    }

    data.top_tasks.forEach((task, index) => {
        const suggestionItem = document.createElement('div');
        suggestionItem.className = 'suggestion-item';
        suggestionItem.innerHTML = `
            <strong>${index + 1}. ${task.title}</strong>
            <p>${task.explanation}</p>
            <small>
                Priority Score: <strong>${task.priority_score}</strong> | 
                Importance: <strong>${task.importance}/10</strong> | 
                Effort: <strong>${task.estimated_hours}h</strong>
            </small>
        `;
        explanationContent.appendChild(suggestionItem);
    });
}

// ============================================
// SAVE TASKS TO DATABASE
// ============================================

async function saveTasksToDatabase(tasks) {
    try {
        // Remove score field (not a database field)
        const tasksToSave = tasks.map(({ score, ...task }) => task);

        const response = await fetch(`${API_BASE}/save-analysis/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ tasks: tasksToSave })
        });

        if (response.ok) {
            const result = await response.json();
            console.log(`✅ Saved ${result.saved} task(s) to database`);
            showSuccess(`Saved ${result.saved} task(s) to database!`);
        } else {
            console.log('Could not save tasks to database');
        }
    } catch (error) {
        console.log('Save error (non-critical):', error.message);
    }
}

// ============================================
// DELETE TASK FROM DATABASE
// ============================================

async function deleteTaskFromDatabase(taskId) {
    try {
        const response = await fetch(`${API_BASE}/delete/${taskId}/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            console.log(`✅ Task ${taskId} deleted from database`);
            // Reload tasks from database
            loadTasksFromDatabase();
        } else {
            showError(`Failed to delete task ${taskId}`);
        }
    } catch (error) {
        showError(`Error deleting task: ${error.message}`);
    }
}

// ============================================
// UI HELPERS
// ============================================

function showLoading(show) {
    if (show) {
        loadingContainer.style.display = 'flex';
    } else {
        loadingContainer.style.display = 'none';
    }
}

function showError(message) {
    errorContainer.style.display = 'block';
    errorText.textContent = message;
    resultsContainer.innerHTML = '<div class="no-results"><p>👈 Fix the error and try again</p></div>';
}

function showSuccess(message) {
    console.log('✅ Success:', message);
    // You can enhance this with a toast notification if desired
}

function clearMessages() {
    errorContainer.style.display = 'none';
    errorText.textContent = '';
}

// ============================================
// INITIALIZATION
// ============================================
