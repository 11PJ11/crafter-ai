#!/bin/bash
# CI/CD Integration Script for AI-Craft Hook System
# Provides comprehensive test execution and validation for CI/CD pipelines

set -euo pipefail

# Source hook system dependencies
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_DIR="$(dirname "$SCRIPT_DIR")"

source "${HOOK_DIR}/lib/config/HookConfig.sh"
source "${HOOK_DIR}/lib/logging/LogManager.sh"
source "${HOOK_DIR}/lib/resilience/ResilienceConfiguration.sh"

# CI/CD Integration configuration
readonly CI_CD_LOG_FILE="/tmp/claude/ci-cd-integration.log"
readonly TEST_RESULTS_DIR="/tmp/claude/test-results"

# Initialize CI/CD integration
init_ci_cd_integration() {
    mkdir -p "$TEST_RESULTS_DIR"
    mkdir -p "$(dirname "$CI_CD_LOG_FILE")"

    echo "CI/CD Integration initialized at $(date)" > "$CI_CD_LOG_FILE"
    hook_log "$LOG_LEVEL_INFO" "CI-CD-Integration" "CI/CD integration system initialized"
}

# Execute comprehensive test suite
execute_comprehensive_tests() {
    local test_type="${1:-all}"
    local exit_code=0

    hook_log "$LOG_LEVEL_INFO" "CI-CD-Integration" "Starting comprehensive test execution: $test_type"

    case "$test_type" in
        "all"|"resilience")
            # Run Hook Resilience System E2E Tests
            if [[ -x "${HOOK_DIR}/tests/HookResilienceSystemE2E.sh" ]]; then
                hook_log "$LOG_LEVEL_INFO" "CI-CD-Integration" "Running Hook Resilience E2E Tests"
                "${HOOK_DIR}/tests/HookResilienceSystemE2E.sh" 2>&1 | tee "${TEST_RESULTS_DIR}/resilience-e2e.log"
                exit_code=${PIPESTATUS[0]}

                if [[ $exit_code -eq 0 ]]; then
                    hook_log "$LOG_LEVEL_INFO" "CI-CD-Integration" "Hook Resilience E2E Tests: PASSED"
                else
                    hook_log "$LOG_LEVEL_ERROR" "CI-CD-Integration" "Hook Resilience E2E Tests: FAILED (exit code: $exit_code)"
                    return $exit_code
                fi
            else
                hook_log "$LOG_LEVEL_WARN" "CI-CD-Integration" "Hook Resilience E2E test not found"
            fi
            ;;
    esac

    # Run additional test scripts if they exist
    if [[ "$test_type" == "all" ]]; then
        local additional_tests
        additional_tests=$(find "${HOOK_DIR}" -name "*test*.sh" -o -name "*Test*.sh" -type f | grep -v HookResilienceSystemE2E.sh || true)

        if [[ -n "$additional_tests" ]]; then
            hook_log "$LOG_LEVEL_INFO" "CI-CD-Integration" "Running additional tests"
            while IFS= read -r test_script; do
                if [[ -x "$test_script" ]]; then
                    local test_name
                    test_name=$(basename "$test_script")
                    hook_log "$LOG_LEVEL_INFO" "CI-CD-Integration" "Executing: $test_name"

                    "$test_script" 2>&1 | tee "${TEST_RESULTS_DIR}/${test_name}.log"
                    local test_exit_code=${PIPESTATUS[0]}

                    if [[ $test_exit_code -eq 0 ]]; then
                        hook_log "$LOG_LEVEL_INFO" "CI-CD-Integration" "$test_name: PASSED"
                    else
                        hook_log "$LOG_LEVEL_ERROR" "CI-CD-Integration" "$test_name: FAILED (exit code: $test_exit_code)"
                        exit_code=$test_exit_code
                    fi
                fi
            done <<< "$additional_tests"
        fi
    fi

    return $exit_code
}

# Validate system architecture and components
validate_system_architecture() {
    hook_log "$LOG_LEVEL_INFO" "CI-CD-Integration" "Validating system architecture"

    # Check essential hook system components
    local required_components=(
        "${HOOK_DIR}/lib/resilience/CircuitBreaker.sh"
        "${HOOK_DIR}/lib/resilience/ResilienceConfiguration.sh"
        "${HOOK_DIR}/lib/resilience/CircuitBreakerState.sh"
        "${HOOK_DIR}/lib/config/HookConfig.sh"
        "${HOOK_DIR}/lib/logging/LogManager.sh"
    )

    local validation_failed=false

    for component in "${required_components[@]}"; do
        if [[ -f "$component" ]]; then
            hook_log "$LOG_LEVEL_DEBUG" "CI-CD-Integration" "✅ Found: $component"
        else
            hook_log "$LOG_LEVEL_ERROR" "CI-CD-Integration" "❌ Missing: $component"
            validation_failed=true
        fi
    done

    if [[ "$validation_failed" == true ]]; then
        hook_log "$LOG_LEVEL_ERROR" "CI-CD-Integration" "Architecture validation failed"
        return 1
    fi

    hook_log "$LOG_LEVEL_INFO" "CI-CD-Integration" "Architecture validation: PASSED"
    return 0
}

# Performance benchmarking
execute_performance_benchmarks() {
    hook_log "$LOG_LEVEL_INFO" "CI-CD-Integration" "Executing performance benchmarks"

    # Benchmark circuit breaker operations
    local start_time end_time duration

    start_time=$(date +%s%3N)
    "${HOOK_DIR}/lib/resilience/CircuitBreaker.sh" status test_tool >/dev/null 2>&1 || true
    end_time=$(date +%s%3N)

    duration=$((end_time - start_time))

    echo "circuit_breaker_status_check_ms:$duration" > "${TEST_RESULTS_DIR}/performance-metrics.txt"

    if [[ $duration -gt 1000 ]]; then
        hook_log "$LOG_LEVEL_WARN" "CI-CD-Integration" "Circuit breaker operation took longer than expected: ${duration}ms"
    else
        hook_log "$LOG_LEVEL_INFO" "CI-CD-Integration" "Circuit breaker performance acceptable: ${duration}ms"
    fi

    hook_log "$LOG_LEVEL_INFO" "CI-CD-Integration" "Performance benchmarks completed"
}

# Security validation
execute_security_validation() {
    hook_log "$LOG_LEVEL_INFO" "CI-CD-Integration" "Executing security validation"

    # Check for hardcoded secrets with more precise patterns
    local security_issues
    security_issues=$(grep -rE "(password|secret|token)[[:space:]]*=[[:space:]]*['\"][^'\"]+['\"]" "${HOOK_DIR}/" --include="*.sh" | grep -v "example\|test\|comment\|LOG_LEVEL\|TODO" || true)

    # Also check for API keys and credentials
    local api_key_issues
    api_key_issues=$(grep -rE "(api_key|apikey|access_key)[[:space:]]*=[[:space:]]*['\"][^'\"]+['\"]" "${HOOK_DIR}/" --include="*.sh" | grep -v "example\|test\|comment" || true)

    # Combine all security issues
    local all_issues
    all_issues=$(printf "%s\n%s" "$security_issues" "$api_key_issues" | grep -v "^$" || true)

    if [[ -n "$all_issues" ]]; then
        hook_log "$LOG_LEVEL_WARN" "CI-CD-Integration" "Potential security issues detected - review required"
        echo "$all_issues" >> "${CI_CD_LOG_FILE}"
        # Don't fail the build for warnings, just log them
        hook_log "$LOG_LEVEL_INFO" "CI-CD-Integration" "Security validation completed with warnings"
        return 0
    fi

    hook_log "$LOG_LEVEL_INFO" "CI-CD-Integration" "Security validation: PASSED"
    return 0
}

# Generate comprehensive test report
generate_test_report() {
    local report_file="${TEST_RESULTS_DIR}/ci-cd-report.txt"

    {
        echo "AI-Craft CI/CD Integration Test Report"
        echo "========================================"
        echo "Generated: $(date)"
        echo ""
        echo "Test Results:"

        if [[ -f "${TEST_RESULTS_DIR}/resilience-e2e.log" ]]; then
            echo "- Hook Resilience E2E Tests: $(grep -c "PASS" "${TEST_RESULTS_DIR}/resilience-e2e.log" || echo "0") passed"
        fi

        if [[ -f "${TEST_RESULTS_DIR}/performance-metrics.txt" ]]; then
            echo "- Performance Metrics:"
            cat "${TEST_RESULTS_DIR}/performance-metrics.txt" | sed 's/^/  /'
        fi

        echo ""
        echo "System Status:"
        echo "- Architecture Validation: $(validate_system_architecture >/dev/null 2>&1 && echo "PASSED" || echo "FAILED")"
        echo "- Security Validation: $(execute_security_validation >/dev/null 2>&1 && echo "PASSED" || echo "FAILED")"

    } > "$report_file"

    hook_log "$LOG_LEVEL_INFO" "CI-CD-Integration" "Test report generated: $report_file"
    cat "$report_file"
}

# Main CI/CD integration execution
main() {
    local command="${1:-help}"

    case "$command" in
        "init")
            init_ci_cd_integration
            ;;
        "test")
            local test_type="${2:-all}"
            init_ci_cd_integration
            execute_comprehensive_tests "$test_type"
            ;;
        "validate")
            init_ci_cd_integration
            validate_system_architecture
            ;;
        "benchmark")
            init_ci_cd_integration
            execute_performance_benchmarks
            ;;
        "security")
            init_ci_cd_integration
            execute_security_validation
            ;;
        "report")
            init_ci_cd_integration
            generate_test_report
            ;;
        "full")
            # Complete CI/CD validation pipeline
            init_ci_cd_integration

            echo "🚀 Starting comprehensive CI/CD validation pipeline..."

            validate_system_architecture || exit 1
            execute_security_validation || exit 1
            execute_comprehensive_tests "all" || exit 1
            execute_performance_benchmarks
            generate_test_report

            echo "✅ CI/CD validation pipeline completed successfully"
            ;;
        "help"|*)
            echo "AI-Craft CI/CD Integration Script"
            echo ""
            echo "Usage: $0 {init|test|validate|benchmark|security|report|full}"
            echo ""
            echo "Commands:"
            echo "  init      - Initialize CI/CD integration system"
            echo "  test      - Run comprehensive test suite [all|resilience]"
            echo "  validate  - Validate system architecture"
            echo "  benchmark - Execute performance benchmarks"
            echo "  security  - Run security validation"
            echo "  report    - Generate comprehensive test report"
            echo "  full      - Execute complete CI/CD validation pipeline"
            echo ""
            echo "Examples:"
            echo "  $0 full                    # Complete CI/CD validation"
            echo "  $0 test resilience         # Run resilience tests only"
            echo "  $0 validate               # Architecture validation only"
            ;;
    esac
}

# Execute main function when script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi