#!/bin/bash
#
# MyWork-AI Framework Installation Script
# ========================================
# Installs the MyWork-AI framework and its dependencies.
#
# Usage:
#   ./install.sh              # Standard installation
#   ./install.sh --dev        # Development installation with test tools
#   ./install.sh --all        # Full installation with all extras
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory (MyWork root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════╗"
echo "║           MyWork-AI Framework Installer            ║"
echo "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.10"

if [[ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]]; then
    echo -e "${RED}Error: Python $REQUIRED_VERSION or higher is required (found $PYTHON_VERSION)${NC}"
    exit 1
fi
echo -e "${GREEN}Python $PYTHON_VERSION detected${NC}"

# Parse arguments
INSTALL_MODE="standard"
if [[ "$1" == "--dev" ]]; then
    INSTALL_MODE="dev"
elif [[ "$1" == "--all" ]]; then
    INSTALL_MODE="all"
fi

# Create virtual environment if it doesn't exist
VENV_DIR="$SCRIPT_DIR/.venv"
if [[ ! -d "$VENV_DIR" ]]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip --quiet

# Install the package
echo -e "${YELLOW}Installing MyWork-AI framework (mode: $INSTALL_MODE)...${NC}"
cd "$SCRIPT_DIR"

case $INSTALL_MODE in
    "dev")
        pip install -e ".[dev]" --quiet
        ;;
    "all")
        pip install -e ".[all]" --quiet
        ;;
    *)
        pip install -e . --quiet
        ;;
esac

# Create necessary directories
echo -e "${YELLOW}Creating directory structure...${NC}"
mkdir -p "$SCRIPT_DIR/.planning"
mkdir -p "$SCRIPT_DIR/.tmp"
mkdir -p "$SCRIPT_DIR/projects"
mkdir -p "$SCRIPT_DIR/workflows"

# Set MYWORK_ROOT environment variable hint
echo -e "${YELLOW}Setting up environment...${NC}"

# Check if .env exists, create if not
if [[ ! -f "$SCRIPT_DIR/.env" ]]; then
    echo "# MyWork-AI Environment Configuration" > "$SCRIPT_DIR/.env"
    echo "MYWORK_ROOT=$SCRIPT_DIR" >> "$SCRIPT_DIR/.env"
    echo -e "${GREEN}Created .env file${NC}"
fi

# Add to shell profile if not already present
SHELL_PROFILE=""
if [[ -f "$HOME/.zshrc" ]]; then
    SHELL_PROFILE="$HOME/.zshrc"
elif [[ -f "$HOME/.bashrc" ]]; then
    SHELL_PROFILE="$HOME/.bashrc"
elif [[ -f "$HOME/.bash_profile" ]]; then
    SHELL_PROFILE="$HOME/.bash_profile"
fi

if [[ -n "$SHELL_PROFILE" ]]; then
    if ! grep -q "MYWORK_ROOT" "$SHELL_PROFILE" 2>/dev/null; then
        echo "" >> "$SHELL_PROFILE"
        echo "# MyWork-AI Framework" >> "$SHELL_PROFILE"
        echo "export MYWORK_ROOT=\"$SCRIPT_DIR\"" >> "$SHELL_PROFILE"
        echo "export PATH=\"\$MYWORK_ROOT/tools:\$PATH\"" >> "$SHELL_PROFILE"
        echo -e "${GREEN}Added MYWORK_ROOT to $SHELL_PROFILE${NC}"
    fi
fi

# Verify installation
echo -e "${YELLOW}Verifying installation...${NC}"
if python3 -c "from tools.config import MYWORK_ROOT; print(f'MYWORK_ROOT: {MYWORK_ROOT}')" 2>/dev/null; then
    echo -e "${GREEN}Configuration module loaded successfully${NC}"
else
    echo -e "${YELLOW}Note: Run 'source $SHELL_PROFILE' to update your path${NC}"
fi

# Run health check if available
if [[ -f "$SCRIPT_DIR/tools/health_check.py" ]]; then
    echo -e "${YELLOW}Running health check...${NC}"
    python3 "$SCRIPT_DIR/tools/health_check.py" quick 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════╗"
echo "║         Installation Complete!                     ║"
echo "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "Next steps:"
echo "  1. Restart your terminal or run: source $SHELL_PROFILE"
echo "  2. Test the installation: mw status"
echo "  3. View available commands: mw --help"
echo ""
echo "Quick commands:"
echo "  mw status        - Check system health"
echo "  mw brain search  - Search the knowledge vault"
echo "  mw scaffold new  - Create a new project"
echo ""
