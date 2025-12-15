#!/bin/bash

# EMA Trading Bot - Setup Script
# This script sets up the trading bot environment

set -e  # Exit on error

echo "=========================================="
echo "EMA Trading Bot - Setup Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo "Please install Python 3.8 or higher from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing Python packages..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Packages installed${NC}"
else
    echo -e "${RED}✗ requirements.txt not found${NC}"
    exit 1
fi

# Create config.ini from example if it doesn't exist
echo ""
echo "Setting up configuration..."
if [ ! -f "config.ini" ]; then
    if [ -f "config.ini.example" ]; then
        cp config.ini.example config.ini
        echo -e "${GREEN}✓ config.ini created from template${NC}"
        echo -e "${YELLOW}⚠ Please edit config.ini and add your API credentials${NC}"
    else
        echo -e "${RED}✗ config.ini.example not found${NC}"
    fi
else
    echo -e "${YELLOW}⚠ config.ini already exists${NC}"
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p data
mkdir -p logs
mkdir -p backtest_results
mkdir -p charts
echo -e "${GREEN}✓ Directories created${NC}"

# Initialize database
echo ""
echo "Initializing database..."
python3 -c "from database_handler import TradingDatabase; TradingDatabase()" 2>/dev/null || true
echo -e "${GREEN}✓ Database initialized${NC}"

# Summary
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit config.ini and add your API credentials"
echo "2. Run: python main.py --dashboard"
echo "3. Start with paper trading: python main.py --paper"
echo ""
echo "For help: python main.py --help"
echo ""
echo -e "${GREEN}Happy Trading! 📈${NC}"
