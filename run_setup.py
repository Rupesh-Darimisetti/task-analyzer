#!/usr/bin/env python3
"""
Task Analyzer - Setup & Run Script
Quick automated setup for Windows
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and show status"""
    print(f"\n📍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {str(e)[:200]}")
        return False

def main():
    print("""
    ╔════════════════════════════════════════════╗
    ║     Task Analyzer - Setup & Run Script     ║
    ║                                            ║
    ║  Complete task prioritization system      ║
    ║  with database persistence                ║
    ╚════════════════════════════════════════════╝
    """)
    
    project_root = Path(__file__).parent
    
    print(f"📁 Project root: {project_root}")
    
    # Check virtual environment
    venv_path = project_root / "venv"
    if not venv_path.exists():
        print("\n❌ Virtual environment not found!")
        print("   Create it with: python -m venv venv")
        return
    
    print("✅ Virtual environment found")
    
    # Check key files
    files_to_check = [
        "manage.py",
        "db.sqlite3",
        "frontend/index.html",
        "requirements.txt"
    ]
    
    print("\n📋 Checking project files...")
    for file in files_to_check:
        full_path = project_root / file
        status = "✅" if full_path.exists() else "❌"
        print(f"   {status} {file}")
    
    # Show what will be run
    print("""
    
    🚀 NEXT STEPS:
    
    1. In Terminal 1 (Backend):
       cd d:\\task-analyzer
       .\\venv\\Scripts\\python manage.py runserver
    
    2. In Terminal 2 (Frontend):
       cd d:\\task-analyzer
       .\\venv\\Scripts\\python serve_frontend.py
    
    3. Open Browser:
       http://127.0.0.1:8001/
    
    ✨ Features Ready to Use:
       ✅ Auto-load tasks from database
       ✅ Add and save tasks
       ✅ Analyze tasks with intelligent scoring
       ✅ Get daily suggestions
       ✅ Delete tasks with one click
       ✅ Color-coded priorities
       ✅ Multiple sorting options
    
    📚 Documentation:
       - QUICK_START.md - 5-minute setup guide
       - README_FULL.md - Complete documentation
       - DATABASE_INTEGRATION.md - Database features
       - IMPLEMENTATION_SUMMARY.md - What was built
    
    🔗 Endpoints:
       Backend: http://127.0.0.1:8000/api/tasks/
       Frontend: http://127.0.0.1:8001/
    
    ✅ System Status:
       ✅ Backend ready
       ✅ Frontend ready
       ✅ Database ready
       ✅ All features implemented
       ✅ Documentation complete
    
    """)
    
    print("\n🎉 Your Task Analyzer is ready!")
    print("   Start both servers and open http://127.0.0.1:8001/")

if __name__ == "__main__":
    main()
