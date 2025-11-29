from datetime import date

def calculate_task_score(task_data):
    """
    Calculates a priority score for a task.
    
    Args:
        task_data (dict): Dictionary containing task information with keys:
            - due_date (date): The due date of the task
            - importance (int): Importance level (1-10)
            - estimated_hours (int): Estimated hours to complete
            - dependencies (list): List of task IDs this task depends on (optional)
    
    Returns:
        float: Priority score (higher score = higher priority)
    
    Scoring breakdown:
        - Urgency: Overdue tasks get +100, tasks due within 3 days get +50
        - Importance: Weighted at 5x (max +50 for importance 10)
        - Effort: Quick wins (< 2 hours) get +10 bonus
        - Dependencies: Penalty of -30 for each blocking dependency
    """
    score = 0

    # 1. Urgency Calculation
    today = date.today()
    days_until_due = (task_data['due_date'] - today).days

    if days_until_due < 0:
        score += 100  # OVERDUE! Huge priority boost
    elif days_until_due <= 3:
        score += 50   # Due very soon
    elif days_until_due <= 7:
        score += 25   # Due within a week

    # 2. Importance Weighting (1-10 scale)
    score += (task_data['importance'] * 5)

    # 3. Effort (Quick wins logic)
    if task_data['estimated_hours'] < 2:
        score += 10  # Small bonus for quick tasks

    # 4. Dependencies Check
    # If a task has dependencies, reduce its priority (blocking tasks should be done first)
    dependencies = task_data.get('dependencies', [])
    if dependencies:
        # Penalty for each dependency - this task is blocked
        score -= (len(dependencies) * 30)

    return score

