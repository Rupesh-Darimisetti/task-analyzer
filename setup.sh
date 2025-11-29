#!/bin/bash
# Task Analyzer - Quick Start Setup Script
# This script automates the setup process

echo "═══════════════════════════════════════════════════════════"
echo "  Task Analyzer - Quick Start Setup"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check if in task-analyzer directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: Please run this script from the task-analyzer directory"
    echo "  cd /d/task-analyzer"
    exit 1
fi

echo "✓ Found task-analyzer directory"
echo ""

# Step 1: Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "1️⃣  Creating virtual environment..."
    python -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Step 2: Activate virtual environment
echo "2️⃣  Activating virtual environment..."
source venv/Scripts/activate
echo "✓ Virtual environment activated"
echo ""

# Step 3: Install dependencies
echo "3️⃣  Installing dependencies..."
pip install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo ""

# Step 4: Run migrations
echo "4️⃣  Setting up database..."
python manage.py migrate --quiet
if [ $? -eq 0 ]; then
    echo "✓ Database migrations complete"
else
    echo "❌ Migration failed"
    exit 1
fi
echo ""

# Step 5: Test backend
echo "5️⃣  Testing backend configuration..."
if python -c "import corsheaders" 2>/dev/null; then
    echo "✓ CORS headers installed"
else
    echo "❌ CORS headers not installed"
    exit 1
fi
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "✅ Setup Complete!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo ""
echo "Terminal 1 - Start Django Backend:"
echo "  python manage.py runserver"
echo ""
echo "Terminal 2 - Serve Frontend:"
echo "  python -m http.server 8001 --directory frontend"
echo ""
echo "Then open in browser:"
echo "  http://127.0.0.1:8001/"
echo ""
echo "Optional: Test backend"
echo "  python test_backend.py"
echo ""
