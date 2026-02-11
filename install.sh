#!/bin/bash
#
# MyWork-AI Framework Installation Script
# ========================================
# Installs the MyWork-AI framework and its dependencies.
#
# Usage:
#   ./install.sh                    # Standard installation
#   ./install.sh --dev              # Development installation with test tools
#   ./install.sh --all              # Full installation with all extras
#   ./install.sh --user             # Install to user directory only
#   ./install.sh --no-venv          # Skip virtual environment creation
#   ./install.sh --help             # Show this help
#

set -e

# Exit on any error with helpful message
trap 'echo -e "\n${RED}❌ Installation failed at line $LINENO. Check the error above.${NC}" >&2' ERR

# Colors for output (enhanced)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Emojis for better UX
SUCCESS="✅"
ERROR="❌"
WARNING="⚠️"
INFO="ℹ️"
ROCKET="🚀"

# Auto-detect Operating System
detect_os() {
    local os=""
    local arch=""
    
    case "$(uname -s)" in
        Linux*)     os="linux" ;;
        Darwin*)    os="macos" ;;
        CYGWIN*)    os="windows" ;;
        MINGW*)     os="windows" ;;
        MSYS*)      os="windows" ;;
        *)          os="unknown" ;;
    esac
    
    case "$(uname -m)" in
        x86_64|amd64)   arch="x64" ;;
        arm64|aarch64)  arch="arm64" ;;
        armv7l)         arch="armv7" ;;
        i386|i686)      arch="x86" ;;
        *)              arch="unknown" ;;
    esac
    
    echo "${os}-${arch}"
}

# Display help
show_help() {
    echo -e "${BOLD}MyWork-AI Installation Script${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dev          Install with development dependencies"
    echo "  --all          Install with all optional dependencies"
    echo "  --user         Install to user directory only (no sudo)"
    echo "  --no-venv      Skip virtual environment creation"
    echo "  --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                  # Standard installation"
    echo "  $0 --dev           # Development setup"
    echo "  $0 --user --no-venv # Minimal user installation"
    exit 0
}

# Enhanced error handling
error_exit() {
    echo -e "${ERROR} ${RED}$1${NC}" >&2
    echo -e "${INFO} ${YELLOW}For help, run: $0 --help${NC}" >&2
    exit "${2:-1}"
}

# Success message with emojis
success_msg() {
    echo -e "${SUCCESS} ${GREEN}$1${NC}"
}

# Info message with emojis
info_msg() {
    echo -e "${INFO} ${BLUE}$1${NC}"
}

# Warning message with emojis
warn_msg() {
    echo -e "${WARNING} ${YELLOW}$1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Get script directory (MyWork root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse arguments first
INSTALL_MODE="standard"
USER_INSTALL=false
NO_VENV=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)      INSTALL_MODE="dev"; shift ;;
        --all)      INSTALL_MODE="all"; shift ;;
        --user)     USER_INSTALL=true; shift ;;
        --no-venv)  NO_VENV=true; shift ;;
        --help|-h)  show_help ;;
        *)          error_exit "Unknown option: $1" ;;
    esac
done

# Display banner
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                    ${BOLD}MyWork-AI Framework Installer${NC}${CYAN}                    ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# System information
SYSTEM_INFO=$(detect_os)
info_msg "System detected: ${BOLD}${SYSTEM_INFO}${NC}"
info_msg "Install mode: ${BOLD}${INSTALL_MODE}${NC}"
[[ "$USER_INSTALL" == true ]] && info_msg "User installation: ${BOLD}enabled${NC}"
[[ "$NO_VENV" == true ]] && info_msg "Virtual environment: ${BOLD}disabled${NC}"
echo ""

# Check dependencies
info_msg "Checking system dependencies..."

# Check Python
if ! command_exists python3; then
    case "$SYSTEM_INFO" in
        linux-*)
            error_exit "Python 3 not found. Install with: sudo apt install python3 python3-pip python3-venv"
            ;;
        macos-*)
            error_exit "Python 3 not found. Install with: brew install python3"
            ;;
        windows-*)
            error_exit "Python 3 not found. Download from: https://python.org/downloads"
            ;;
        *)
            error_exit "Python 3 not found. Please install Python 3.8+ first."
            ;;
    esac
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)
REQUIRED_MAJOR=3
REQUIRED_MINOR=8

if [[ "$PYTHON_MAJOR" -lt "$REQUIRED_MAJOR" ]] || [[ "$PYTHON_MAJOR" -eq "$REQUIRED_MAJOR" && "$PYTHON_MINOR" -lt "$REQUIRED_MINOR" ]]; then
    error_exit "Python 3.8+ required, found $PYTHON_VERSION. Please upgrade Python."
fi
success_msg "Python $PYTHON_VERSION detected"

# Check Git
if ! command_exists git; then
    case "$SYSTEM_INFO" in
        linux-*)
            warn_msg "Git not found. Install with: sudo apt install git"
            ;;
        macos-*)
            warn_msg "Git not found. Install with: brew install git"
            ;;
        windows-*)
            warn_msg "Git not found. Download from: https://git-scm.com"
            ;;
    esac
else
    success_msg "Git $(git --version | cut -d' ' -f3) detected"
fi

# Check Node.js (optional)
if command_exists node; then
    NODE_VERSION=$(node --version 2>/dev/null | sed 's/v//')
    success_msg "Node.js $NODE_VERSION detected"
elif [[ "$INSTALL_MODE" == "all" ]]; then
    warn_msg "Node.js not found (needed for web projects)"
    case "$SYSTEM_INFO" in
        linux-*)
            info_msg "Install with: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt install nodejs"
            ;;
        macos-*)
            info_msg "Install with: brew install node"
            ;;
    esac
fi

echo ""

# Virtual environment setup
if [[ "$NO_VENV" != true ]]; then
    VENV_DIR="$SCRIPT_DIR/.venv"
    if [[ ! -d "$VENV_DIR" ]]; then
        info_msg "Creating virtual environment..."
        if ! python3 -m venv "$VENV_DIR"; then
            error_exit "Failed to create virtual environment. Try installing python3-venv package."
        fi
        success_msg "Virtual environment created"
    else
        info_msg "Virtual environment already exists"
    fi
    
    info_msg "Activating virtual environment..."
    source "$VENV_DIR/bin/activate" || error_exit "Failed to activate virtual environment"
    success_msg "Virtual environment activated"
else
    warn_msg "Skipping virtual environment creation"
fi

# Upgrade pip
info_msg "Upgrading pip..."
if ! pip install --upgrade pip --quiet; then
    error_exit "Failed to upgrade pip"
fi
success_msg "Pip upgraded successfully"

# Install the package
info_msg "Installing MyWork-AI framework (mode: ${BOLD}$INSTALL_MODE${NC})..."
cd "$SCRIPT_DIR"

case $INSTALL_MODE in
    "dev")
        if ! pip install -e ".[dev]" --quiet; then
            error_exit "Failed to install MyWork-AI with dev dependencies"
        fi
        success_msg "Development installation completed"
        ;;
    "all")
        if ! pip install -e ".[all]" --quiet; then
            error_exit "Failed to install MyWork-AI with all dependencies"
        fi
        success_msg "Full installation completed"
        ;;
    *)
        if ! pip install -e . --quiet; then
            error_exit "Failed to install MyWork-AI"
        fi
        success_msg "Standard installation completed"
        ;;
esac

# Create necessary directories
info_msg "Creating directory structure..."
mkdir -p "$SCRIPT_DIR/.planning"
mkdir -p "$SCRIPT_DIR/.tmp"
mkdir -p "$SCRIPT_DIR/projects"
mkdir -p "$SCRIPT_DIR/workflows"
mkdir -p "$SCRIPT_DIR/examples"
mkdir -p "$SCRIPT_DIR/docs"
success_msg "Directory structure created"

# Set MYWORK_ROOT environment variable
info_msg "Setting up environment configuration..."

# Check if .env exists, create if not
if [[ ! -f "$SCRIPT_DIR/.env" ]]; then
    cat > "$SCRIPT_DIR/.env" << EOF
# MyWork-AI Environment Configuration
MYWORK_ROOT=$SCRIPT_DIR
PYTHON_VERSION=$PYTHON_VERSION
SYSTEM_INFO=$SYSTEM_INFO
INSTALL_MODE=$INSTALL_MODE
INSTALL_DATE=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
EOF
    success_msg "Created .env configuration file"
else
    info_msg ".env file already exists"
fi

# Add to shell profile if not already present (only if not user install)
if [[ "$USER_INSTALL" != true ]]; then
    SHELL_PROFILE=""
    case "$SHELL" in
        */zsh)      SHELL_PROFILE="$HOME/.zshrc" ;;
        */bash)     SHELL_PROFILE="$HOME/.bashrc" ;;
        *)          [[ -f "$HOME/.bashrc" ]] && SHELL_PROFILE="$HOME/.bashrc" || SHELL_PROFILE="$HOME/.bash_profile" ;;
    esac

    if [[ -n "$SHELL_PROFILE" ]]; then
        if ! grep -q "MYWORK_ROOT" "$SHELL_PROFILE" 2>/dev/null; then
            cat >> "$SHELL_PROFILE" << EOF

# MyWork-AI Framework (added $(date))
export MYWORK_ROOT="$SCRIPT_DIR"
export PATH="\$MYWORK_ROOT/.venv/bin:\$MYWORK_ROOT/tools:\$PATH"
EOF
            success_msg "Added MYWORK_ROOT to $SHELL_PROFILE"
        else
            info_msg "MYWORK_ROOT already configured in shell profile"
        fi
    fi
fi

# Verify installation
info_msg "Verifying installation..."
if python3 -c "import sys; sys.path.insert(0, '$SCRIPT_DIR'); from tools.config import MYWORK_ROOT; print(f'MYWORK_ROOT: {MYWORK_ROOT}')" 2>/dev/null; then
    success_msg "Configuration module loaded successfully"
else
    warn_msg "Configuration module test failed (this is normal for first install)"
    info_msg "Run 'source ~/.bashrc' or restart terminal to complete setup"
fi

# Run health check if available
if [[ -f "$SCRIPT_DIR/tools/health_check.py" ]]; then
    info_msg "Running health check..."
    if python3 "$SCRIPT_DIR/tools/health_check.py" quick 2>/dev/null; then
        success_msg "Health check passed"
    else
        warn_msg "Health check failed (this may be normal for first install)"
    fi
fi

# Final success message
echo ""
echo -e "${GREEN}${BOLD}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                    ${ROCKET} Installation Complete! ${ROCKET}                    ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo -e "${BOLD}${BLUE}Next Steps:${NC}"
echo -e "  ${CYAN}1.${NC} Restart your terminal or run: ${YELLOW}source ~/.bashrc${NC}"
echo -e "  ${CYAN}2.${NC} Test the installation: ${YELLOW}mw status${NC}"
echo -e "  ${CYAN}3.${NC} View available commands: ${YELLOW}mw --help${NC}"
echo -e "  ${CYAN}4.${NC} Create your first project: ${YELLOW}mw create saas my-app${NC}"
echo ""
echo -e "${BOLD}${PURPLE}Quick Commands:${NC}"
echo -e "  ${YELLOW}mw status${NC}        - Check system health"
echo -e "  ${YELLOW}mw version${NC}       - Show version information"
echo -e "  ${YELLOW}mw create${NC}        - Create a new project"
echo -e "  ${YELLOW}mw docs${NC}          - Generate documentation"
echo ""
echo -e "${BOLD}${GREEN}System Information:${NC}"
echo -e "  OS: $SYSTEM_INFO"
echo -e "  Python: $PYTHON_VERSION"
echo -e "  Install Mode: $INSTALL_MODE"
echo -e "  Install Path: $SCRIPT_DIR"
echo ""
echo -e "${CYAN}${INFO} For help and documentation, visit: https://github.com/yourorg/MyWork-AI${NC}"
echo ""
