#!/bin/bash
# Craft-AI State Initializer Hook
# Only initializes state for CAI/ATDD workflows
# Preserves other framework states

set -euo pipefail

# Check if this is a CAI workflow
is_cai_workflow() {
    # Check for CAI indicators
    [[ -f "state/craft-ai/pipeline-state.json" ]] || \
    [[ "${CLAUDE_AGENT:-}" =~ ^cai- ]] || \
    [[ "${ACTIVE_WORKFLOW:-}" = "atdd" ]] || \
    [[ "${PWD}" =~ craft-ai ]] || \
    [[ -d ".claude/agents/cai" ]] || \
    grep -q "cai/atdd\|acceptance-designer\|test-first-developer" <<< "${*:-}" 2>/dev/null
}

# Only proceed if this is a CAI workflow
if ! is_cai_workflow "$@"; then
    exit 0  # Skip for non-CAI workflows
fi

# Initialize CAI-specific state
STATE_DIR="state/craft-ai"
PIPELINE_STATE_FILE="$STATE_DIR/pipeline-state.json"
WAVE_STATE_FILE="$STATE_DIR/wave-state.json"

# Create state directory if it doesn't exist
mkdir -p "$STATE_DIR"

# Initialize pipeline state if not present
if [[ ! -f "$PIPELINE_STATE_FILE" ]]; then
    cat > "$PIPELINE_STATE_FILE" << 'EOF'
{
  "stage": "DISCUSS",
  "agent": "business-analyst",
  "status": "pending",
  "feature_id": "",
  "started_at": "",
  "stage_history": [],
  "context": {
    "project_type": "unknown",
    "complexity": "medium",
    "requirements_source": "user_input"
  }
}
EOF
fi

# Initialize wave state if not present
if [[ ! -f "$WAVE_STATE_FILE" ]]; then
    cat > "$WAVE_STATE_FILE" << 'EOF'
{
  "wave_id": "",
  "wave_count": 0,
  "current_wave": 0,
  "wave_status": "not_started",
  "waves": [],
  "coordination_mode": "sequential"
}
EOF
fi

# Set environment variables for CAI session
export ATDD_STAGE=$(python3 "$HOME/.claude/hooks/cai/workflow/json-utils.py" get "$PIPELINE_STATE_FILE" "stage" "DISCUSS")
export ACTIVE_AGENT=$(python3 "$HOME/.claude/hooks/cai/workflow/json-utils.py" get "$PIPELINE_STATE_FILE" "agent" "business-analyst")
export CAI_STATE_DIR="$STATE_DIR"
export CAI_WORKFLOW_ACTIVE="true"

# Log state initialization
if [[ -w "$STATE_DIR" ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] CAI state initialized: stage=$ATDD_STAGE, agent=$ACTIVE_AGENT" >> "$STATE_DIR/session.log"
fi

exit 0