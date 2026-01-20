#!/bin/bash
# Formatter Tools Availability Check Hook
# Detects when code formatter and type checker tools are not available
# Provides clear installation instructions and alternatives
#
# Required tools:
# - ruff: Combined Python formatter, linter, and import sorter
# - mypy: Static type checker for Python

set -e

# Color codes
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Checking code formatter and type checker availability...${NC}"

# Check if any Python files are being staged
PYTHON_FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null | grep '\.py$' || true)

if [ -z "$PYTHON_FILES" ]; then
    echo -e "${BLUE}No Python files to check${NC}"
    exit 0
fi

# Tools to check
FORMATTERS=("ruff" "mypy")
MISSING_TOOLS=()

# Check each formatter tool
for TOOL in "${FORMATTERS[@]}"; do
    if ! command -v "$TOOL" &> /dev/null; then
        MISSING_TOOLS+=("$TOOL")
    fi
done

if [ ${#MISSING_TOOLS[@]} -eq 0 ]; then
    echo -e "${GREEN}All required formatters available${NC}"
    exit 0
fi

# Tools are missing - provide installation guidance
echo ""
echo -e "${RED}FORMATTER NOT FOUND ERROR${NC}"
echo ""
echo -e "${RED}Missing tools:${NC}"
for TOOL in "${MISSING_TOOLS[@]}"; do
    echo "  - $TOOL"
done
echo ""

echo -e "${YELLOW}Installation Instructions:${NC}"
echo ""

if [[ " ${MISSING_TOOLS[@]} " =~ " ruff " ]]; then
    echo "For Ruff (Python formatter, linter, import sorter):"
    echo "  Quick: pip install ruff"
    echo "  System: apt install ruff  (Debian/Ubuntu)"
    echo "          brew install ruff (macOS)"
    echo "  Docker: docker run --rm charliermarsh/ruff check ."
    echo ""
    echo "  Ruff Configuration: pyproject.toml or .ruff.toml"
    echo "  More info: https://docs.astral.sh/ruff/"
    echo ""
fi

if [[ " ${MISSING_TOOLS[@]} " =~ " mypy " ]]; then
    echo "For Mypy (Python static type checker):"
    echo "  Quick: pip install mypy"
    echo "  System: apt install mypy  (Debian/Ubuntu)"
    echo "          brew install mypy (macOS)"
    echo "  Docker: docker run --rm -v \$(pwd):/app mypy/mypy ."
    echo ""
    echo "  Mypy Configuration: mypy.ini or [tool.mypy] in pyproject.toml"
    echo "  More info: http://www.mypy-lang.org/"
    echo ""
fi

echo -e "${YELLOW}Alternative Tool Configurations:${NC}"
echo ""
echo "Code Formatters (alternative to Ruff):"
echo "  - Black        : pip install black      (strict, opinionated formatting)"
echo "  - Autopep8     : pip install autopep8   (flexible PEP 8 compliance)"
echo "  - YAPF         : pip install yapf       (highly customizable formatting)"
echo "  - Isort        : pip install isort      (import sorting only)"
echo ""
echo "Type Checkers (alternative to Mypy):"
echo "  - Pyright      : pip install pyright    (VSCode native, fast)"
echo "  - Pydantic     : pip install pydantic   (runtime validation)"
echo "  - Pytype       : pip install pytype     (Google's type checker)"
echo ""

echo -e "${YELLOW}Development Environment Setup:${NC}"
echo ""
echo "Option 1: Virtual Environment"
echo "  python3 -m venv venv"
echo "  source venv/bin/activate  (Linux/macOS)"
echo "  .\\\\venv\\\\Scripts\\\\activate  (Windows)"
echo "  pip install ruff mypy"
echo ""

echo "Option 2: Using pipx (isolated tool environments)"
echo "  pipx install ruff mypy"
echo ""

echo "Option 3: Docker"
echo "  docker run --rm -v \$(pwd):/app ruffaustralia/ruff check ."
echo "  docker run --rm -v \$(pwd):/app mypy/mypy ."
echo ""

echo -e "${YELLOW}Quick Setup (All at Once):${NC}"
echo "  pip install ruff mypy"
echo "  pre-commit run --all-files"
echo ""

echo -e "${YELLOW}Environment Detection:${NC}"
echo "  Python version: $(python3 --version 2>/dev/null || echo 'Not found')"
echo "  Pip version: $(pip --version 2>/dev/null || echo 'Not found')"
echo "  OS: $(uname -s)"
echo ""

echo -e "${RED}COMMIT BLOCKED: Formatter tools not available${NC}"
echo ""
echo -e "${YELLOW}Resolution Options:${NC}"
echo "  1. Install tools: pip install ruff mypy"
echo "  2. Skip check: git commit --no-verify (not recommended)"
echo "  3. Check docs: See .pre-commit-config.yaml for configuration"
echo ""

exit 1
