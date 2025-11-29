#!/usr/bin/env python
"""
Task Analyzer - Diagnostic Test Script
Tests if the backend is properly configured and working.
"""

import requests
import json
import sys
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://127.0.0.1:8000/api/tasks"
COLORS = {
    'green': '\033[92m',
    'red': '\033[91m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'end': '\033[0m'
}

def print_status(test_name, passed, message=""):
    status = f"{COLORS['green']}✓ PASS{COLORS['end']}" if passed else f"{COLORS['red']}✗ FAIL{COLORS['end']}"
    print(f"  [{status}] {test_name}")
    if message:
        print(f"         {message}")

def print_header(title):
    print(f"\n{COLORS['blue']}{'='*60}")
    print(f"{title:^60}")
    print(f"{'='*60}{COLORS['end']}\n")

def test_server_connection():
    """Test if Django server is running"""
    print_header("1. Testing Server Connection")
    try:
        response = requests.get(f"{BASE_URL}/list/", timeout=5)
        if response.status_code == 200:
            print_status("Server accessible", True)
            print_status("CORS headers present", 'access-control-allow-origin' in response.headers.keys() if hasattr(response, 'headers') else False,
                        f"Headers: {list(response.headers.keys())[:3]}...")
            return True
        else:
            print_status("Server accessible", False, f"Status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_status("Server accessible", False, "Connection refused - is Django running?")
        return False
    except requests.exceptions.Timeout:
        print_status("Server accessible", False, "Connection timeout")
        return False
    except Exception as e:
        print_status("Server accessible", False, str(e))
        return False

def test_analyze_endpoint():
    """Test the /analyze/ endpoint"""
    print_header("2. Testing /analyze/ Endpoint")
    
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)
    
    test_data = {
        "tasks": [
            {
                "title": "Urgent Task",
                "due_date": tomorrow.strftime("%Y-%m-%d"),
                "importance": 8,
                "estimated_hours": 1,
                "dependencies": []
            },
            {
                "title": "Regular Task",
                "due_date": next_week.strftime("%Y-%m-%d"),
                "importance": 5,
                "estimated_hours": 2,
                "dependencies": []
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/analyze/",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_status("POST request successful", True, f"Received {data.get('count', '?')} tasks")
            
            # Check response structure
            has_count = 'count' in data
            has_tasks = 'tasks' in data
            print_status("Response has 'count' field", has_count)
            print_status("Response has 'tasks' field", has_tasks)
            
            if has_tasks and len(data['tasks']) > 0:
                task = data['tasks'][0]
                has_score = 'score' in task
                print_status("Tasks have 'score' field", has_score, f"Score: {task.get('score', 'N/A')}")
                
                # Print sample scores
                print(f"\n         Sample Scores:")
                for i, task in enumerate(data['tasks'], 1):
                    print(f"           {i}. {task['title']}: {task.get('score', '?')}")
            
            return True
        else:
            print_status("POST request successful", False, f"Status: {response.status_code}")
            print(f"         Response: {response.text[:100]}")
            return False
            
    except Exception as e:
        print_status("POST request successful", False, str(e))
        return False

def test_suggest_endpoint():
    """Test the /suggest/ endpoint"""
    print_header("3. Testing /suggest/ Endpoint")
    
    try:
        response = requests.get(
            f"{BASE_URL}/suggest/",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_status("GET request successful", True, f"Received {data.get('count', '?')} suggestions")
            
            # Check response structure
            has_count = 'count' in data
            has_today = 'today' in data
            has_top_tasks = 'top_tasks' in data
            
            print_status("Response has 'count' field", has_count)
            print_status("Response has 'today' field", has_today, f"Today: {data.get('today', 'N/A')}")
            print_status("Response has 'top_tasks' field", has_top_tasks)
            
            if has_top_tasks and len(data['top_tasks']) > 0:
                print(f"\n         Top {data.get('count', '?')} Tasks for Today:")
                for i, task in enumerate(data['top_tasks'], 1):
                    score = task.get('priority_score', '?')
                    print(f"           {i}. {task.get('title', 'Untitled')}: Score {score}")
            
            return True
        else:
            print_status("GET request successful", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_status("GET request successful", False, str(e))
        return False

def test_list_endpoint():
    """Test the /list/ endpoint"""
    print_header("4. Testing /list/ Endpoint")
    
    try:
        response = requests.get(
            f"{BASE_URL}/list/",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            task_count = len(data) if isinstance(data, list) else len(data.get('results', []))
            print_status("GET request successful", True, f"Database has {task_count} task(s)")
            
            if task_count > 0:
                print(f"\n         Sample Tasks in Database:")
                items = data if isinstance(data, list) else data.get('results', [])
                for i, task in enumerate(items[:3], 1):
                    print(f"           {i}. {task.get('title', 'Untitled')} (ID: {task.get('id', '?')})")
            
            return True
        else:
            print_status("GET request successful", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_status("GET request successful", False, str(e))
        return False

def test_edge_cases():
    """Test edge case handling"""
    print_header("5. Testing Edge Cases")
    
    # Test 1: Missing fields
    test_data = {
        "tasks": [
            {
                "title": "Missing importance",
                "due_date": "2025-12-01",
                # Missing: importance
                "estimated_hours": 1,
                "dependencies": []
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/analyze/",
            json=test_data,
            timeout=5
        )
        print_status("Handles missing fields", response.status_code == 200, 
                    f"Status: {response.status_code}")
    except Exception as e:
        print_status("Handles missing fields", False, str(e))
    
    # Test 2: Past date
    test_data = {
        "tasks": [
            {
                "title": "Old task from 1990",
                "due_date": "1990-01-01",
                "importance": 5,
                "estimated_hours": 1,
                "dependencies": []
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/analyze/",
            json=test_data,
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            score = data['tasks'][0].get('score', 0)
            is_high = score >= 100
            print_status("Past date gets +100 urgency", is_high, f"Score: {score}")
        else:
            print_status("Past date handling", False, f"Status: {response.status_code}")
    except Exception as e:
        print_status("Past date handling", False, str(e))
    
    # Test 3: Invalid JSON
    try:
        response = requests.post(
            f"{BASE_URL}/analyze/",
            data="invalid json",
            timeout=5
        )
        print_status("Rejects invalid JSON", response.status_code == 400, 
                    f"Status: {response.status_code}")
    except Exception as e:
        print_status("Rejects invalid JSON", False, str(e))

def main():
    """Run all tests"""
    print(f"{COLORS['blue']}")
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║      Task Analyzer - Diagnostic Test Suite                   ║")
    print("║              Backend Configuration Check                      ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print(f"{COLORS['end']}")
    
    print(f"\nTesting backend at: {BASE_URL}\n")
    
    results = []
    
    # Run tests
    results.append(("Server Connection", test_server_connection()))
    results.append(("Analyze Endpoint", test_analyze_endpoint()))
    results.append(("Suggest Endpoint", test_suggest_endpoint()))
    results.append(("List Endpoint", test_list_endpoint()))
    test_edge_cases()
    
    # Summary
    print_header("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓" if result else "✗"
        print(f"  [{status}] {test_name}")
    
    print(f"\n{COLORS['blue']}{'─'*60}{COLORS['end']}")
    if passed == total:
        print(f"{COLORS['green']}All tests passed! ✓{COLORS['end']}")
        print("Your Task Analyzer backend is ready to use.")
    else:
        print(f"{COLORS['yellow']}{passed}/{total} tests passed{COLORS['end']}")
        print("Check the errors above and see CORS_FIX.md for help.")
    
    print(f"{COLORS['blue']}{'─'*60}{COLORS['end']}\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
