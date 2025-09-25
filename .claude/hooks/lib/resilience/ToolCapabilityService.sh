#!/bin/bash
# ToolCapabilityService - Tool detection and health assessment
# Part of Claude Code SuperClaude hook system resilience components

set -euo pipefail

# Source dependencies
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_LIB_DIR}/config/HookConfig.sh"
source "${HOOK_LIB_DIR}/logging/LogManager.sh"
source "$(dirname "${BASH_SOURCE[0]}")/ResilienceConfiguration.sh"

# Check if circuit breaker functions are available (optional dependency)
CIRCUIT_BREAKER_AVAILABLE=false
if declare -f get_circuit_status >/dev/null 2>&1; then
    CIRCUIT_BREAKER_AVAILABLE=true
fi

# Tool capability cache - derived from configuration
readonly TOOL_CAPABILITY_CACHE_DIR="$RESILIENCE_STATE_BASE_DIR"

# Tool health states - use include guard to prevent redefinition
if [[ -z "${TOOL_STATE_HEALTHY:-}" ]]; then
    readonly TOOL_STATE_HEALTHY=0
    readonly TOOL_STATE_DEGRADED=1
    readonly TOOL_STATE_UNAVAILABLE=2
fi

# Initialize tool capability service
init_tool_capability_service() {
    mkdir -p "$TOOL_CAPABILITY_CACHE_DIR"
    hook_log "$LOG_LEVEL_DEBUG" "ToolCapabilityService" "Tool capability service initialized"
}

# Assess tool capability and health
assess_tool_capability() {
    local tool_name="$1"
    local install_method="${2:-}"
    local package_name="${3:-$tool_name}"

    hook_log "$LOG_LEVEL_DEBUG" "ToolCapabilityService" "Assessing capability for tool: $tool_name"

    # Check cache first
    local cached_result
    cached_result=$(get_cached_capability "$tool_name")
    if [[ -n "$cached_result" ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "ToolCapabilityService" "Using cached capability for $tool_name: $cached_result"
        echo "$cached_result"
        return 0
    fi

    # Perform fresh assessment
    local capability_result
    capability_result=$(perform_tool_assessment "$tool_name" "$install_method" "$package_name")

    # Cache the result
    cache_capability_result "$tool_name" "$capability_result"

    echo "$capability_result"
}

# Perform actual tool assessment
perform_tool_assessment() {
    local tool_name="$1"
    local install_method="$2"
    local package_name="$3"

    # Check if tool is available
    if ! command -v "$tool_name" >/dev/null 2>&1; then
        hook_log "$LOG_LEVEL_DEBUG" "ToolCapabilityService" "Tool $tool_name not found in PATH"

        # Check if tool can be automatically installed
        if can_auto_install_tool "$tool_name" "$install_method" "$package_name"; then
            echo "$TOOL_STATE_DEGRADED:auto_installable:$install_method:$package_name"
        else
            echo "$TOOL_STATE_UNAVAILABLE:missing:manual_install_required"
        fi
        return 0
    fi

    # Tool exists - check health
    local health_status
    health_status=$(check_tool_health "$tool_name")

    if [[ $health_status -eq 0 ]]; then
        echo "$TOOL_STATE_HEALTHY:available:$(command -v "$tool_name")"
    else
        echo "$TOOL_STATE_DEGRADED:unhealthy:exit_code_$health_status"
    fi
}

# Check tool health by running a simple test
check_tool_health() {
    local tool_name="$1"

    hook_log "$LOG_LEVEL_DEBUG" "ToolCapabilityService" "Checking health for tool: $tool_name"

    case "$tool_name" in
        "black")
            black --version >/dev/null 2>&1
            ;;
        "prettier")
            prettier --version >/dev/null 2>&1
            ;;
        "shellcheck")
            shellcheck --version >/dev/null 2>&1
            ;;
        "jq")
            echo '{}' | jq . >/dev/null 2>&1
            ;;
        "python"|"python3")
            "$tool_name" -c "print('test')" >/dev/null 2>&1
            ;;
        "node")
            node --version >/dev/null 2>&1
            ;;
        *)
            # Generic health check - just try to run with --version or --help
            if "$tool_name" --version >/dev/null 2>&1; then
                return 0
            elif "$tool_name" --help >/dev/null 2>&1; then
                return 0
            else
                return 1
            fi
            ;;
    esac
}

# Check if tool can be automatically installed
can_auto_install_tool() {
    local tool_name="$1"
    local install_method="$2"
    local package_name="$3"

    # Don't auto-install in CI environments
    if [[ "${CI:-false}" = "true" ]]; then
        return 1
    fi

    # Don't auto-install if not interactive
    if [[ ! -t 1 ]]; then
        return 1
    fi

    # Check if installation method is available
    case "$install_method" in
        "pipx")
            command -v pipx >/dev/null 2>&1
            ;;
        "pip"|"pip3")
            command -v pip >/dev/null 2>&1 || command -v pip3 >/dev/null 2>&1
            ;;
        "npm")
            command -v npm >/dev/null 2>&1
            ;;
        "yarn")
            command -v yarn >/dev/null 2>&1
            ;;
        "apt"|"apt-get")
            command -v apt-get >/dev/null 2>&1 && [[ -n "${DEBIAN_FRONTEND:-}" || -f /etc/debian_version ]]
            ;;
        *)
            return 1
            ;;
    esac
}

# Get cached capability result
get_cached_capability() {
    local tool_name="$1"
    local cache_file="$TOOL_CAPABILITY_CACHE_DIR/capability_${tool_name}.cache"
    local timestamp_file="$TOOL_CAPABILITY_CACHE_DIR/capability_${tool_name}.timestamp"

    if [[ ! -f "$cache_file" ]] || [[ ! -f "$timestamp_file" ]]; then
        return 0
    fi

    local cache_age
    local current_time
    cache_age=$(cat "$timestamp_file")
    current_time=$(date +%s)

    if [[ $((current_time - cache_age)) -lt $TOOL_CAPABILITY_CACHE_TTL_SECONDS ]]; then
        cat "$cache_file"
    fi
}

# Cache capability assessment result
cache_capability_result() {
    local tool_name="$1"
    local result="$2"
    local cache_file="$TOOL_CAPABILITY_CACHE_DIR/capability_${tool_name}.cache"
    local timestamp_file="$TOOL_CAPABILITY_CACHE_DIR/capability_${tool_name}.timestamp"

    echo "$result" > "$cache_file"
    date +%s > "$timestamp_file"

    hook_log "$LOG_LEVEL_DEBUG" "ToolCapabilityService" "Cached capability result for $tool_name: $result"
}

# Parse capability result
parse_capability_result() {
    local result="$1"

    IFS=':' read -r state reason detail <<< "$result"
    echo "state=$state reason=$reason detail=$detail"
}

# Check if tool is healthy based on capability assessment
is_tool_healthy() {
    local tool_name="$1"
    local capability_result

    capability_result=$(assess_tool_capability "$tool_name")
    local state
    state=$(echo "$capability_result" | cut -d':' -f1)

    [[ $state -eq $TOOL_STATE_HEALTHY ]]
}

# Get degradation reason for tool
get_degradation_reason() {
    local tool_name="$1"
    local capability_result

    capability_result=$(assess_tool_capability "$tool_name")
    local reason
    reason=$(echo "$capability_result" | cut -d':' -f2)

    echo "$reason"
}

# Attempt to remediate tool issues
attempt_tool_remediation() {
    local tool_name="$1"
    local install_method="${2:-}"
    local package_name="${3:-$tool_name}"

    hook_log "$LOG_LEVEL_INFO" "ToolCapabilityService" "Attempting remediation for tool: $tool_name"

    local capability_result
    capability_result=$(assess_tool_capability "$tool_name" "$install_method" "$package_name")
    local state reason detail
    IFS=':' read -r state reason detail <<< "$capability_result"

    case "$state" in
        $TOOL_STATE_HEALTHY)
            hook_log "$LOG_LEVEL_DEBUG" "ToolCapabilityService" "Tool $tool_name is already healthy"
            return 0
            ;;
        $TOOL_STATE_DEGRADED)
            if [[ "$reason" = "auto_installable" ]]; then
                attempt_auto_installation "$tool_name" "$detail" "$package_name"
            else
                hook_log "$LOG_LEVEL_WARN" "ToolCapabilityService" "Tool $tool_name is degraded but cannot be auto-remediated: $reason"
                return 1
            fi
            ;;
        $TOOL_STATE_UNAVAILABLE)
            hook_log "$LOG_LEVEL_WARN" "ToolCapabilityService" "Tool $tool_name is unavailable: $reason"
            return 1
            ;;
    esac
}

# Attempt automatic installation
attempt_auto_installation() {
    local tool_name="$1"
    local install_method="$2"
    local package_name="$3"

    hook_log "$LOG_LEVEL_INFO" "ToolCapabilityService" "Attempting to install $tool_name using $install_method"

    case "$install_method" in
        "pipx")
            pipx install "$package_name"
            ;;
        "pip")
            pip install --user "$package_name"
            ;;
        "pip3")
            pip3 install --user "$package_name"
            ;;
        "npm")
            npm install -g "$package_name"
            ;;
        "yarn")
            yarn global add "$package_name"
            ;;
        *)
            hook_log "$LOG_LEVEL_ERROR" "ToolCapabilityService" "Unsupported install method: $install_method"
            return 1
            ;;
    esac

    local install_result=$?
    if [[ $install_result -eq 0 ]]; then
        hook_log "$LOG_LEVEL_INFO" "ToolCapabilityService" "Successfully installed $tool_name"
        # Invalidate cache to force reassessment
        invalidate_capability_cache "$tool_name"
        return 0
    else
        hook_log "$LOG_LEVEL_ERROR" "ToolCapabilityService" "Failed to install $tool_name (exit code: $install_result)"
        return 1
    fi
}

# Invalidate capability cache for a tool
invalidate_capability_cache() {
    local tool_name="$1"
    local cache_file="$TOOL_CAPABILITY_CACHE_DIR/capability_${tool_name}.cache"
    local timestamp_file="$TOOL_CAPABILITY_CACHE_DIR/capability_${tool_name}.timestamp"

    rm -f "$cache_file" "$timestamp_file"
    hook_log "$LOG_LEVEL_DEBUG" "ToolCapabilityService" "Invalidated capability cache for $tool_name"
}

# Get comprehensive tool status report
get_tool_status_report() {
    local tools=("$@")

    echo "=== Tool Capability Status Report ==="
    echo "Generated: $(date)"
    echo

    for tool in "${tools[@]}"; do
        local capability_result
        capability_result=$(assess_tool_capability "$tool")
        local state reason detail
        IFS=':' read -r state reason detail <<< "$capability_result"

        local state_name
        case "$state" in
            $TOOL_STATE_HEALTHY) state_name="HEALTHY" ;;
            $TOOL_STATE_DEGRADED) state_name="DEGRADED" ;;
            $TOOL_STATE_UNAVAILABLE) state_name="UNAVAILABLE" ;;
            *) state_name="UNKNOWN" ;;
        esac

        echo "Tool: $tool"
        echo "  State: $state_name"
        echo "  Reason: $reason"
        echo "  Detail: $detail"

        # Show circuit breaker status if available
        if [[ "$CIRCUIT_BREAKER_AVAILABLE" = true ]]; then
            local cb_status
            cb_status=$(get_circuit_status "$tool" 2>/dev/null || echo "Circuit breaker status unavailable")
            echo "  Circuit Breaker: $cb_status"
        else
            echo "  Circuit Breaker: Not loaded"
        fi
        echo
    done
}

# Command-line interface for tool capability service
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    init_tool_capability_service

    case "${1:-}" in
        "assess")
            if [[ -n "${2:-}" ]]; then
                assess_tool_capability "$2" "${3:-}" "${4:-$2}"
            else
                echo "Usage: $0 assess <tool_name> [install_method] [package_name]"
                exit 1
            fi
            ;;
        "health")
            if [[ -n "${2:-}" ]]; then
                if is_tool_healthy "$2"; then
                    echo "Tool $2 is healthy"
                    exit 0
                else
                    echo "Tool $2 is not healthy"
                    exit 1
                fi
            else
                echo "Usage: $0 health <tool_name>"
                exit 1
            fi
            ;;
        "remediate")
            if [[ -n "${2:-}" ]]; then
                attempt_tool_remediation "$2" "${3:-}" "${4:-$2}"
            else
                echo "Usage: $0 remediate <tool_name> [install_method] [package_name]"
                exit 1
            fi
            ;;
        "report")
            shift
            get_tool_status_report "$@"
            ;;
        "cache-clear")
            if [[ -n "${2:-}" ]]; then
                invalidate_capability_cache "$2"
                echo "Cache cleared for $2"
            else
                echo "Usage: $0 cache-clear <tool_name>"
                exit 1
            fi
            ;;
        *)
            echo "Usage: $0 {assess|health|remediate|report|cache-clear} <tool_name> [args...]"
            echo "  assess - Assess tool capability and health"
            echo "  health - Check if tool is healthy (exit code 0/1)"
            echo "  remediate - Attempt to fix tool issues"
            echo "  report - Generate comprehensive status report for tools"
            echo "  cache-clear - Clear capability cache for a tool"
            exit 1
            ;;
    esac
fi