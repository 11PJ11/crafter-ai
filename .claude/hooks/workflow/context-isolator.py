#!/usr/bin/env python3
"""
Craft-AI Context Isolator Hook
Provides clean context isolation for CAI agents only
Preserves other framework contexts unchanged
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional


def is_cai_context(prompt: str) -> bool:
    """Check if this prompt involves CAI agents or workflows"""
    cai_indicators = [
        "cai/atdd",
        "acceptance-designer",
        "test-first-developer",
        "solution-architect",
        "business-analyst",
        "user-experience-designer",
        "technical-stakeholder",
        "security-expert",
        "legal-compliance-advisor",
        "technology-selector",
        "architecture-diagram-manager",
        "quality-gates",
        "commit-readiness-coordinator",
        "mutation-testing-coordinator",
        "comprehensive-refactoring-specialist",
        "atdd-orchestrator",
        "hypothesis-validator",
        "experiment-designer",
        "learning-synthesizer",
    ]

    prompt_lower = prompt.lower()
    return any(indicator in prompt_lower for indicator in cai_indicators)


def load_agent_specification(agent_name: str) -> Optional[str]:
    """Load CAI agent specification"""
    # Check multiple possible locations
    possible_paths = [
        Path.home() / ".claude" / "agents" / "cai" / f"{agent_name}.md",
        Path(".claude") / "agents" / "cai" / f"{agent_name}.md",
        Path(".claude") / "agents" / "cai" / "test-design" / f"{agent_name}.md",
        Path(".claude") / "agents" / "cai" / "development" / f"{agent_name}.md",
        Path(".claude") / "agents" / "cai" / "coordination" / f"{agent_name}.md",
    ]

    for path in possible_paths:
        if path.exists():
            try:
                return path.read_text(encoding="utf-8")
            except Exception:
                continue

    return None


def get_agent_name_from_prompt(prompt: str) -> Optional[str]:
    """Extract agent name from prompt"""
    cai_agents = [
        "acceptance-designer",
        "test-first-developer",
        "solution-architect",
        "business-analyst",
        "user-experience-designer",
        "technical-stakeholder",
        "security-expert",
        "legal-compliance-advisor",
        "technology-selector",
        "architecture-diagram-manager",
    ]

    prompt_lower = prompt.lower()
    for agent in cai_agents:
        if agent in prompt_lower:
            return agent

    return None


def load_pipeline_state() -> Dict:
    """Load current pipeline state"""
    state_file = Path("state/craft-ai/pipeline-state.json")
    if state_file.exists():
        try:
            return json.loads(state_file.read_text())
        except Exception:
            pass

    return {"stage": "DISCUSS", "agent": "business-analyst", "status": "pending"}


def get_stage_context(stage: str) -> Dict:
    """Get context information for current stage"""
    stage_contexts = {
        "DISCUSS": {
            "input_files": ["requirements.md", "stakeholder-analysis.md"],
            "output_files": ["requirements.md", "business-constraints.md"],
            "focus": "requirements gathering and validation",
        },
        "ARCHITECT": {
            "input_files": ["requirements.md", "business-constraints.md"],
            "output_files": ["architecture.md", "technology-decisions.md"],
            "focus": "system design and architecture",
        },
        "DISTILL": {
            "input_files": ["requirements.md", "architecture.md"],
            "output_files": ["acceptance-tests.md", "test-scenarios.md"],
            "focus": "acceptance test design",
        },
        "DEVELOP": {
            "input_files": ["acceptance-tests.md", "architecture.md"],
            "output_files": ["implementation-status.md", "development-log.md"],
            "focus": "outside-in TDD implementation",
        },
        "DEMO": {
            "input_files": ["implementation-status.md", "quality-report.md"],
            "output_files": ["demo-report.md", "completion-status.md"],
            "focus": "feature validation and completion",
        },
    }

    return stage_contexts.get(stage, {})


def inject_cai_context(prompt: str) -> str:
    """Inject CAI-specific context into prompt"""
    # Get agent name from prompt
    agent_name = get_agent_name_from_prompt(prompt)
    if not agent_name:
        return prompt

    # Load agent specification
    agent_spec = load_agent_specification(agent_name)
    if not agent_spec:
        return prompt

    # Load pipeline state
    pipeline_state = load_pipeline_state()
    stage = pipeline_state.get("stage", "DISCUSS")
    stage_context = get_stage_context(stage)

    # Build enhanced context
    context = f"""
# 🔄 CAI AGENT CONTEXT RESET - Starting Fresh Session

## 📋 Your Identity and Specification
{agent_spec}

## 🎯 Current ATDD Stage: {stage}
**Stage Focus**: {stage_context.get('focus', 'General development')}

## 📁 File-Based Communication Protocol
### INPUT FILES (Read from these):
{chr(10).join(f"- docs/craft-ai/{f}" for f in stage_context.get('input_files', []))}

### OUTPUT FILES (Write to these):
{chr(10).join(f"- docs/craft-ai/{f}" for f in stage_context.get('output_files', []))}

## 🚫 MANDATORY CONSTRAINTS REMINDER
1. **Clean Context**: You are starting with fresh context - ignore any previous conversation
2. **File Discipline**: Read ONLY from your designated input files, write ONLY to output files
3. **Specification Adherence**: Follow ALL mandatory constraints in your specification above
4. **Production Services**: Use GetRequiredService pattern, never call CLI or infrastructure directly
5. **Business Language**: Use domain terminology, not technical implementation details
6. **Ask for Clarification**: When requirements are unclear or ambiguous, ask specific questions

## 🔍 Quality Gates Checklist
Before completing your task, verify:
- [ ] All mandatory constraints followed
- [ ] Business language used (not technical jargon)
- [ ] Production services called via dependency injection
- [ ] Output written to correct files only
- [ ] Architecture patterns respected

---

## 📝 Original User Request
{prompt}

**Remember**: You are {agent_name} starting fresh. Follow your specification above strictly.
"""

    return context


def main():
    """Main hook execution"""
    # Read prompt from stdin or command line
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = sys.stdin.read().strip()

    # Only process CAI contexts
    if not is_cai_context(prompt):
        print(prompt)  # Pass through unchanged
        return

    # Inject CAI context
    enhanced_prompt = inject_cai_context(prompt)
    print(enhanced_prompt)


if __name__ == "__main__":
    main()
