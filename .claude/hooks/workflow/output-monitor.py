#!/usr/bin/env python3
"""
Craft-AI Output Monitor Hook
Monitors agent outputs for compliance and proper file usage
Only processes CAI agent outputs, preserves other framework outputs
"""

import sys
import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

def is_cai_workflow_active() -> bool:
    """Check if CAI workflow is currently active"""
    # Check environment variables
    if os.environ.get('CAI_WORKFLOW_ACTIVE') == 'true':
        return True

    # Check for CAI state file
    if Path('state/craft-ai/pipeline-state.json').exists():
        return True

    # Check for CAI agent in environment
    active_agent = os.environ.get('ACTIVE_AGENT', '')
    if any(agent in active_agent for agent in [
        'acceptance-designer', 'test-first-developer', 'solution-architect',
        'business-analyst', 'user-experience-designer'
    ]):
        return True

    return False

def load_pipeline_state() -> Dict:
    """Load current pipeline state"""
    state_file = Path('state/craft-ai/pipeline-state.json')
    if state_file.exists():
        try:
            return json.loads(state_file.read_text())
        except Exception:
            pass

    return {
        "stage": "DISCUSS",
        "agent": "business-analyst",
        "status": "pending"
    }

def get_allowed_output_files(stage: str) -> List[str]:
    """Get allowed output files for current stage"""
    stage_outputs = {
        "DISCUSS": [
            "requirements.md",
            "stakeholder-analysis.md",
            "business-constraints.md",
            "user-stories.md"
        ],
        "ARCHITECT": [
            "architecture.md",
            "technology-decisions.md",
            "architecture-diagrams.md",
            "component-design.md"
        ],
        "DISTILL": [
            "acceptance-tests.md",
            "test-scenarios.md",
            "validation-criteria.md",
            "test-data.md"
        ],
        "DEVELOP": [
            "implementation-status.md",
            "development-log.md",
            "quality-report.md",
            "refactoring-notes.md"
        ],
        "DEMO": [
            "demo-report.md",
            "completion-status.md",
            "lessons-learned.md",
            "handover-notes.md"
        ]
    }

    return stage_outputs.get(stage, ["requirements.md"])

def validate_output_file(file_path: str, stage: str) -> Tuple[bool, str]:
    """Validate if output file is allowed for current stage"""
    # Allow non-CAI files (preserve other frameworks)
    if 'craft-ai' not in file_path:
        return True, "Non-CAI file - allowed"

    # Check if file is in docs/craft-ai/ directory
    if not file_path.startswith('docs/craft-ai/'):
        return False, f"CAI files must be in docs/craft-ai/ directory, not: {file_path}"

    # Get filename
    filename = Path(file_path).name
    allowed_files = get_allowed_output_files(stage)

    if filename in allowed_files:
        return True, f"File allowed for {stage} stage"

    return False, f"File '{filename}' not allowed for {stage} stage. Allowed files: {', '.join(allowed_files)}"

def check_content_compliance(file_path: str, content: str) -> List[str]:
    """Check content for compliance with CAI standards"""
    violations = []

    # Only check CAI files
    if 'craft-ai' not in file_path:
        return violations

    # Check for forbidden patterns (CLI calls, infrastructure access)
    forbidden_patterns = [
        (r'execAsync\s*\(', "Direct CLI execution detected - use production services instead"),
        (r'Process\.Start\s*\(', "Direct process execution detected - use production services"),
        (r'CLI\s*\.', "Direct CLI access detected - use GetRequiredService pattern"),
        (r'exec\s*\(', "Direct exec call detected - use production services"),
        (r'system\s*\(', "Direct system call detected - use production services")
    ]

    for pattern, message in forbidden_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            violations.append(message)

    # Check for required patterns in test files
    if 'test' in file_path.lower() or 'acceptance' in file_path.lower():
        # Check for GetRequiredService pattern
        if 'GetRequiredService' not in content:
            violations.append("Missing GetRequiredService pattern in test implementation")

        # Check business language ratio
        business_terms = ['user', 'customer', 'order', 'business', 'domain', 'service', 'workflow']
        technical_terms = ['database', 'API', 'CLI', 'infrastructure', 'deployment', 'process']

        business_count = sum(content.lower().count(term) for term in business_terms)
        technical_count = sum(content.lower().count(term) for term in technical_terms)

        if technical_count > 0:
            ratio = business_count / (business_count + technical_count)
            if ratio < 0.7:
                violations.append(f"Business language ratio too low: {ratio:.1%} (minimum 70%)")

    return violations

def log_output_activity(file_path: str, stage: str, status: str, violations: List[str] = None):
    """Log output monitoring activity"""
    log_dir = Path('state/craft-ai')
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / 'output-monitor.log'

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = {
        'timestamp': timestamp,
        'file_path': file_path,
        'stage': stage,
        'status': status,
        'violations': violations or []
    }

    try:
        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] OUTPUT MONITOR: {status} - {file_path} (stage: {stage})\n")
            if violations:
                for violation in violations:
                    f.write(f"  - VIOLATION: {violation}\n")
    except Exception:
        pass

def update_compliance_metrics(file_path: str, violations: List[str]):
    """Update compliance metrics"""
    metrics_file = Path('state/craft-ai/compliance-metrics.json')

    # Load existing metrics
    metrics = {}
    if metrics_file.exists():
        try:
            metrics = json.loads(metrics_file.read_text())
        except Exception:
            pass

    # Initialize if needed
    if 'files' not in metrics:
        metrics['files'] = {}
    if 'summary' not in metrics:
        metrics['summary'] = {
            'total_files': 0,
            'compliant_files': 0,
            'total_violations': 0
        }

    # Update file metrics
    metrics['files'][file_path] = {
        'violations': len(violations),
        'violation_details': violations,
        'last_check': datetime.now().isoformat(),
        'compliant': len(violations) == 0
    }

    # Update summary
    metrics['summary']['total_files'] = len(metrics['files'])
    metrics['summary']['compliant_files'] = sum(
        1 for f in metrics['files'].values() if f['compliant']
    )
    metrics['summary']['total_violations'] = sum(
        f['violations'] for f in metrics['files'].values()
    )

    # Calculate compliance rate
    if metrics['summary']['total_files'] > 0:
        compliance_rate = metrics['summary']['compliant_files'] / metrics['summary']['total_files']
        metrics['summary']['compliance_rate'] = f"{compliance_rate:.1%}"

    # Save metrics
    try:
        metrics_file.write_text(json.dumps(metrics, indent=2))
    except Exception:
        pass

def main():
    """Main hook execution"""
    # Only process if CAI workflow is active
    if not is_cai_workflow_active():
        return

    # Get file information from environment or arguments
    file_path = os.environ.get('CLAUDE_WRITE_FILE', '')
    if not file_path and len(sys.argv) > 1:
        file_path = sys.argv[1]

    if not file_path:
        return

    # Load pipeline state
    pipeline_state = load_pipeline_state()
    stage = pipeline_state.get('stage', 'DISCUSS')

    # Validate output file
    is_valid, validation_message = validate_output_file(file_path, stage)

    if not is_valid:
        print(f"❌ CAI OUTPUT VALIDATION ERROR")
        print(f"File: {file_path}")
        print(f"Error: {validation_message}")
        log_output_activity(file_path, stage, "BLOCKED", [validation_message])
        sys.exit(1)

    # Read content if file exists for compliance checking
    violations = []
    if Path(file_path).exists():
        try:
            content = Path(file_path).read_text(encoding='utf-8')
            violations = check_content_compliance(file_path, content)
        except Exception:
            pass

    # Log results
    if violations:
        status = "VIOLATIONS_DETECTED"
        print(f"⚠️  CAI COMPLIANCE VIOLATIONS in {file_path}:")
        for violation in violations:
            print(f"  - {violation}")
        print("Please fix violations before proceeding.")
    else:
        status = "COMPLIANT"

    log_output_activity(file_path, stage, status, violations)
    update_compliance_metrics(file_path, violations)

    # Block if critical violations found
    critical_patterns = ["Direct CLI execution", "Direct process execution"]
    has_critical = any(any(pattern in v for pattern in critical_patterns) for v in violations)

    if has_critical:
        print("❌ CRITICAL VIOLATIONS DETECTED - Output blocked")
        sys.exit(1)

if __name__ == '__main__':
    main()