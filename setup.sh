#!/bin/bash

# =====================================================
# Urban Growth Detection System — Setup Script
# AI212 Course Project
# =====================================================

echo ""
echo "======================================"
echo " Urban Growth Detection System Setup"
echo "======================================"
echo ""

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'  # No Color

# Function to check if a command exists
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✓ $1 is installed${NC}"
    else
        echo -e "${RED}✗ $1 is NOT installed — please install it first${NC}"
        exit 1
    fi
}

# Step 1: Check prerequisites
echo -e "${BLUE}[1/5] Checking prerequisites...${NC}"
check_command python3
check_command node
check_command npm
check_command docker
echo ""

# Step 2: Set up Python virtual environment
echo -e "${BLUE}[2/5] Setting up Python environment...${NC}"
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi
source venv/bin/activate
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Python dependencies installed${NC}"
cd ..
echo ""

# Step 3: Install frontend dependencies
echo -e "${BLUE}[3/5] Installing frontend dependencies...${NC}"
cd frontend
npm install --silent
echo -e "${GREEN}✓ Node dependencies installed${NC}"
cd ..
echo ""

# Step 4: Create .env file if not exists
echo -e "${BLUE}[4/5] Creating environment file...${NC}"
if [ ! -f ".env" ]; then
    echo "GEMINI_API_KEY=" > .env
    echo -e "${GREEN}✓ .env file created (add your Gemini key if available)${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi
echo ""

# Step 5: Done — show run instructions
echo -e "${BLUE}[5/5] Setup complete!${NC}"
echo ""
echo "======================================"
echo " How to Run the Project"
echo "======================================"
echo ""
echo "Option A: Run with Docker (Recommended):"
echo "  docker compose up --build"
echo ""
echo "Option B: Run locally (Development):"
echo "  Terminal 1 (Backend):"
echo "    cd backend && source venv/bin/activate"
echo "    uvicorn main:app --reload --port 8000"
echo ""
echo "  Terminal 2 (Frontend):"
echo "    cd frontend && npm run dev"
echo ""
echo "Open browser: http://localhost:5173"
echo "API docs:     http://localhost:8000/docs"
echo ""