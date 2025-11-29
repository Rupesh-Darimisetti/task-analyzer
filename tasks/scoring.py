from datetime import date

def calculate_task_score(task_data):
    """
    Calculates a priority score for a task.
    
    Args:
        task_data (dict): Dictionary containing task information with keys:
            - due_date (date): The due date of the task
            - importance (int): Importance level (1-10, default 5)
            - estimated_hours (int): Estimated hours to complete (default 1)
            - dependencies (list): List of task IDs this task depends on (optional)
    
    Returns:
        float: Priority score (higher score = higher priority)
    
    Scoring breakdown:
        - Urgency: Overdue tasks get +100, tasks due within 3 days get +50
        - Importance: Weighted at 5x (max +50 for importance 10)
        - Effort: Quick wins (< 2 hours) get +10 bonus
        - Dependencies: Penalty of -30 for each blocking dependency
    
    Edge Cases Handled:
        - Past due dates (1990): Treated as overdue (+100)
        - Missing importance: Uses default of 5
        - Missing estimated_hours: Uses default of 1
        - Missing dependencies: Assumes empty list
        - Zero/negative estimated_hours: Still considered quick win if < 2
    """
    score = 0
    
    # Defensive: Handle missing or invalid fields with sensible defaults
    try:
        today = date.today()
        due_date = task_data.get('due_date')
        importance = task_data.get('importance', 5)
        estimated_hours = task_data.get('estimated_hours', 1)
        dependencies = task_data.get('dependencies', [])
        
        # Validate and normalize inputs
        if not isinstance(importance, (int, float)):
            importance = 5
        if not isinstance(estimated_hours, (int, float)):
            estimated_hours = 1
        if not isinstance(dependencies, list):
            dependencies = []
        
        # Clamp importance to reasonable range (though frontend should prevent this)
        importance = max(1, min(10, importance))
        
        # Handle due_date conversion if it's a string
        if isinstance(due_date, str):
            due_date = date.fromisoformat(due_date)
        
        # 1. Urgency Calculation
        if due_date:
            days_until_due = (due_date - today).days
            
            if days_until_due < 0:
                score += 100  # OVERDUE! Huge priority boost (handles 1990 dates)
            elif days_until_due <= 3:
                score += 50   # Due very soon
            elif days_until_due <= 7:
                score += 25   # Due within a week
            # Beyond 7 days: no urgency bonus (score += 0)
        else:
            # No due date provided: assume very low urgency
            score += 0
        
        # 2. Importance Weighting (1-10 scale)
        score += (importance * 5)
        
        # 3. Effort (Quick wins logic)
        if estimated_hours < 2:
            score += 10  # Small bonus for quick tasks
        
        # 4. Dependencies Check
        # If a task has dependencies, reduce its priority (blocking tasks should be done first)
        if dependencies:
            # Penalty for each dependency - this task is blocked
            score -= (len(dependencies) * 30)
        
        # Ensure score never goes below 0 (negative scores are demotivating)
        score = max(0, score)
        
        return score
    
    except Exception as e:
        # Fallback: If something goes wrong, return a neutral score
        # This prevents crashes from malformed input
        print(f"Warning: Error calculating score for task: {e}")
        return 50  # Neutral middle score


