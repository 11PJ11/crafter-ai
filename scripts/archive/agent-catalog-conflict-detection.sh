#!/bin/bash
# Agent-Catalog Conflict Detection Hook
# Detects when agent definitions and their catalog files change together
# Prevents divergence between agent behavior and documentation
#
# Conflict pairs monitored:
# - Agent file changes + agent catalog changes = possible divergence
# - Agent specification changes + command changes = coordination required

set -e

# Color codes
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Checking for agent-catalog conflicts...${NC}"

# Get list of staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || echo "")

if [ -z "$STAGED_FILES" ]; then
    echo -e "${BLUE}No staged files to check${NC}"
    exit 0
fi

# Define agent-catalog conflict pairs
# Format: agent_pattern:catalog_pattern
CONFLICT_PAIRS=(
    "nWave/agents/agent-builder.md:nWave/catalogs/agent-builder-catalog.md"
    "nWave/agents/agent-builder-reviewer.md:nWave/catalogs/agent-builder-reviewer-catalog.md"
    "nWave/agents/acceptance-designer.md:nWave/catalogs/acceptance-designer-catalog.md"
    "nWave/agents/acceptance-designer-reviewer.md:nWave/catalogs/acceptance-designer-reviewer-catalog.md"
    "nWave/agents/data-engineer.md:nWave/catalogs/data-engineer-catalog.md"
    "nWave/agents/data-engineer-reviewer.md:nWave/catalogs/data-engineer-reviewer-catalog.md"
    "nWave/commands/:nWave/agents/"
    "nWave/templates/:nWave/agents/"
)

CONFLICTS_FOUND=0

# Check for conflict pairs
for PAIR in "${CONFLICT_PAIRS[@]}"; do
    IFS=':' read -r AGENT_PATTERN CATALOG_PATTERN <<< "$PAIR"

    AGENT_MODIFIED=false
    CATALOG_MODIFIED=false

    # Check if agent file is staged
    if echo "$STAGED_FILES" | grep -q "^${AGENT_PATTERN}"; then
        AGENT_MODIFIED=true
    fi

    # Check if catalog file is staged
    if echo "$STAGED_FILES" | grep -q "^${CATALOG_PATTERN}"; then
        CATALOG_MODIFIED=true
    fi

    # If both agent and catalog modified, flag as conflict
    if [ "$AGENT_MODIFIED" = true ] && [ "$CATALOG_MODIFIED" = true ]; then
        CONFLICTS_FOUND=1

        echo ""
        echo -e "${YELLOW}CONFLICT DETECTED: Agent and catalog changed together${NC}"
        echo -e "${YELLOW}Agent files:${NC}"
        echo "$STAGED_FILES" | grep "^${AGENT_PATTERN}" | sed 's/^/  [Agent] /'
        echo -e "${YELLOW}Catalog files:${NC}"
        echo "$STAGED_FILES" | grep "^${CATALOG_PATTERN}" | sed 's/^/  [Catalog] /'
        echo ""

        echo -e "${YELLOW}Risk Analysis:${NC}"
        echo "  - Agent behavior and documentation may have diverged"
        echo "  - Changes to agent specification require catalog updates"
        echo "  - Command definitions must match agent expectations"
        echo ""

        echo -e "${YELLOW}Verification Checklist:${NC}"
        echo "  [ ] Agent commands match catalog documentation"
        echo "  [ ] Agent specification describes actual behavior"
        echo "  [ ] Dependencies in agent match those in catalog"
        echo "  [ ] Error handling documented in both files"
        echo ""

        echo -e "${YELLOW}Recommendation:${NC}"
        echo "  - Review changes for consistency between agent and catalog"
        echo "  - Verify specification accuracy in both files"
        echo "  - Ensure command definitions are synchronized"
        echo "  - Test agent behavior against updated specifications"
        echo ""
    fi
done

if [ $CONFLICTS_FOUND -eq 1 ]; then
    echo -e "${YELLOW}Review suggested before committing${NC}"
    echo -e "${YELLOW}Bypass with: git commit --no-verify${NC}"
    exit 0  # Warning only, non-blocking
else
    echo -e "${BLUE}No agent-catalog conflicts detected${NC}"
    exit 0
fi
