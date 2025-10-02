#!/bin/bash
# AI-Craft Framework - Managed File
# Part of Claude Code SuperClaude modular hook system
# Craft-AI State Initializer Hook - Modular Version
# Uses new modular hook architecture
# Only initializes state for CAI/ATDD workflows

set -euo pipefail

# Source modular hook system
HOOK_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_DIR}/lib/HookManager.sh"

# Initialize hook system
if ! init_hook_system; then
    hook_log "$LOG_LEVEL_ERROR" "StateInitializer" "Failed to initialize hook system"
    exit 1
fi

# Check if this is a CAI workflow
is_cai_workflow() {
    hook_log "$LOG_LEVEL_DEBUG" "StateInitializer" "Checking for CAI workflow indicators"

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
    hook_log "$LOG_LEVEL_DEBUG" "StateInitializer" "Non-CAI workflow detected, skipping"
    exit 0  # Skip for non-CAI workflows
fi

hook_log "$LOG_LEVEL_INFO" "StateInitializer" "CAI workflow detected, initializing state"

# Initialize CAI-specific state
STATE_DIR="state/craft-ai"
PIPELINE_STATE_FILE="$STATE_DIR/pipeline-state.json"
WAVE_STATE_FILE="$STATE_DIR/wave-state.json"

# Create state directory if it doesn't exist
mkdir -p "$STATE_DIR"
hook_log "$LOG_LEVEL_DEBUG" "StateInitializer" "State directory created: $STATE_DIR"

# Initialize pipeline state if not present
if [[ ! -f "$PIPELINE_STATE_FILE" ]]; then
    hook_log "$LOG_LEVEL_INFO" "StateInitializer" "Creating pipeline state file"
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
    hook_log "$LOG_LEVEL_INFO" "StateInitializer" "Creating wave state file"
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
# Note: Using new config system for paths
json_utils_path="$(resolve_hook_path "cai/workflow/json-utils.py")"
if [[ -f "$json_utils_path" ]]; then
    export ATDD_STAGE=$(python3 "$json_utils_path" get "$PIPELINE_STATE_FILE" "stage" "DISCUSS")
    export ACTIVE_AGENT=$(python3 "$json_utils_path" get "$PIPELINE_STATE_FILE" "agent" "business-analyst")
else
    # Fallback for compatibility
    export ATDD_STAGE="DISCUSS"
    export ACTIVE_AGENT="business-analyst"
    hook_log "$LOG_LEVEL_WARN" "StateInitializer" "json-utils.py not found, using defaults"
fi

export CAI_STATE_DIR="$STATE_DIR"
export CAI_WORKFLOW_ACTIVE="true"

# Log state initialization using new logging system
hook_log "$LOG_LEVEL_INFO" "StateInitializer" "CAI state initialized: stage=$ATDD_STAGE, agent=$ACTIVE_AGENT"

# Also log to session.log for backward compatibility
if [[ -w "$STATE_DIR" ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] CAI state initialized: stage=$ATDD_STAGE, agent=$ACTIVE_AGENT" >> "$STATE_DIR/session.log"
fi

hook_log "$LOG_LEVEL_INFO" "StateInitializer" "State initialization completed successfully"
exit 0