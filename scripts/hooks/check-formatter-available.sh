#!/bin/bash
# Code Formatter Availability Check Hook
# Detects when code formatter tools are not available
# Provides installation instructions and alternatives

set -e

# Color codes
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Checking code formatter availability...${NC}"

# Check if any Python files are being staged
PYTHON_FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null | grep '\.py$' || true)

if [ -z "$PYTHON_FILES" ]; then
    echo -e "${BLUE}No Python files to check${NC}"
    exit 0
fi

# Formatters to check
FORMATTERS=("ruff" "mypy")
MISSING_FORMATTERS=()

# Check each formatter
for FORMATTER in "${FORMATTERS[@]}"; do
    if ! command -v "$FORMATTER" &> /dev/null; then
        MISSING_FORMATTERS+=("$FORMATTER")
    fi
done

if [ ${#MISSING_FORMATTERS[@]} -eq 0 ]; then
    echo -e "${GREEN}All required formatters available${NC}"
    exit 0
fi

# Formatters are missing
echo ""
echo -e "${RED}FORMATTER NOT FOUND ERROR${NC}"
echo ""
echo -e "${RED}Missing formatters:${NC}"
for FORMATTER in "${MISSING_FORMATTERS[@]}"; do
    echo "  - $FORMATTER"
done
echo ""

echo -e "${YELLOW}Installation Instructions:${NC}"
echo ""

if [[ " ${MISSING_FORMATTERS[@]} " =~ " ruff " ]]; then
    echo "For Ruff (combined formatter, linter, import sorter):"
    echo "  pip install ruff"
    echo "  # or if using system package manager:"
    echo "  # apt install ruff  (Debian/Ubuntu)"
    echo "  # brew install ruff (macOS)"
    echo ""
fi

if [[ " ${MISSING_FORMATTERS[@]} " =~ " mypy " ]]; then
    echo "For Mypy (type checker):"
    echo "  pip install mypy"
    echo "  # or if using system package manager:"
    echo "  # apt install mypy   (Debian/Ubuntu)"
    echo "  # brew install mypy  (macOS)"
    echo ""
fi

echo -e "${YELLOW}Alternative Formatter Configurations:${NC}"
echo ""
echo "If you prefer different tools, alternatives include:"
echo ""
echo "  Code Formatters (like Ruff):"
echo "    - Black        : pip install black      (strict formatting)"
echo "    - Autopep8     : pip install autopep8   (PEP 8 compliant)"
echo "    - YAPF         : pip install yapf       (flexible formatting)"
echo ""
echo "  Type Checkers (like Mypy):"
echo "    - Pyright      : pip install pyright    (VSCode native)"
echo "    - Pydantic     : pip install pydantic   (runtime validation)"
echo ""
echo "Configuration can be updated in .pre-commit-config.yaml"
echo ""

echo -e "${YELLOW}Quick setup:${NC}"
echo "  pip install ruff mypy"
echo "  pre-commit run --all-files"
echo ""

echo -e "${RED}COMMIT BLOCKED: Formatter tools not available${NC}"
echo -e "${YELLOW}Emergency bypass: git commit --no-verify${NC}"
exit 1
