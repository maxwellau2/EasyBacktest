#!/bin/bash
# Build script for EasyBacktest framework
# Creates a distributable .whl file

set -e  # Exit on any error

echo "================================="
echo "Building EasyBacktest Wheel"
echo "================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Clean previous builds
echo -e "${BLUE}Cleaning previous builds...${NC}"
rm -rf build/
rm -rf dist/
rm -rf *.egg-info
rm -rf easy_backtest.egg-info
echo -e "${GREEN}✓ Cleaned${NC}"
echo ""

# Build the wheel
echo -e "${BLUE}Building wheel package...${NC}"
python3 setup.py sdist bdist_wheel

echo ""
echo -e "${GREEN}✓ Build complete!${NC}"
echo ""

# Show the created files
echo -e "${YELLOW}Created files:${NC}"
ls -lh dist/
echo ""

# Get the wheel file name
WHEEL_FILE=$(ls dist/*.whl 2>/dev/null | head -n 1)

if [ -n "$WHEEL_FILE" ]; then
    echo -e "${GREEN}Wheel file created: ${WHEEL_FILE}${NC}"
    echo ""
    echo "To install:"
    echo "  pip install ${WHEEL_FILE}"
    echo ""
    echo "To install in editable mode (for development):"
    echo "  pip install -e ."
else
    echo -e "${YELLOW}Warning: No .whl file found in dist/${NC}"
fi

echo "================================="
