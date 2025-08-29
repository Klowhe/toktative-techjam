#!/bin/bash

# GeoReg Classifier - Full Stack Startup Script

echo "🚀 Starting GeoReg Compliance Classifier..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "📋 Checking dependencies..."

if ! command_exists python3; then
    echo -e "${RED}❌ Python3 is required but not installed.${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}❌ Node.js/npm is required but not installed.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dependencies check passed${NC}"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Python dependencies installed${NC}"
    else
        echo -e "${RED}❌ Failed to install Python dependencies${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  requirements.txt not found${NC}"
fi

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
if [ -f "package.json" ]; then
    npm install
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Node.js dependencies installed${NC}"
    else
        echo -e "${RED}❌ Failed to install Node.js dependencies${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  package.json not found${NC}"
fi

echo ""
echo "🎯 Ready to start services!"
echo ""
echo "To run the application:"
echo "1️⃣  Start the backend API server:"
echo "   ${YELLOW}cd src && python3 app.py${NC}"
echo ""
echo "2️⃣  In a new terminal, start the frontend dev server:"
echo "   ${YELLOW}npm run dev${NC}"
echo ""
echo "3️⃣  Open your browser to:"
echo "   ${GREEN}http://localhost:5173${NC}"
echo ""
echo "💡 The frontend will automatically detect if the backend is running:"
echo "   • 🟢 Green status = AI Backend Online"
echo "   • 🟡 Yellow status = Backend Offline (Mock Mode)"
echo ""
echo "📚 Backend API will be available at:"
echo "   ${GREEN}http://localhost:5000${NC}"
echo ""
