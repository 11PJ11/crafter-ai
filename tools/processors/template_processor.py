#!/usr/bin/env python3
"""
Template Processor for nWave Command Files

Processes Markdown command files to replace template variables with values
from the canonical schema. This ensures that command documentation always
reflects the actual schema structure without manual synchronization.

Template Variables:
  {{SCHEMA_TDD_PHASES}} - Complete list of TDD phases with descriptions
  {{TDD_PHASE_COUNT}} - Total number of TDD phases
  {{MANDATORY_PHASES}} - Mandatory phases with descriptions
  {{PHASE_EXECUTION_LOG}} - JSON schema for phase execution tracking
  {{SCHEMA_VERSION}} - Current schema version
  {{SCHEMA_UPDATED}} - Schema last updated date
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List


class TemplateProcessor:
    """Process template variables in Markdown files using canonical schema."""

    def __init__(self, schema_path: Path):
        """Initialize processor with canonical schema."""
        self.schema_path = Path(schema_path)
        self.schema = self._load_schema()
        self.template_variables = self._extract_variables()

    def _load_schema(self) -> Dict[str, Any]:
        """Load and validate canonical schema."""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {self.schema_path}")

        with open(self.schema_path, "r") as f:
            return json.load(f)

    def _extract_variables(self) -> Dict[str, str]:
        """Extract template variables from canonical schema."""
        variables = {}

        # Schema version
        variables["SCHEMA_VERSION"] = self.schema.get("version", "unknown")

        # TDD Phase count and list
        phase_log = self.schema.get("tdd_cycle", {}).get("phase_execution_log", [])
        variables["TDD_PHASE_COUNT"] = str(len(phase_log))

        # Build complete TDD phases list with descriptions
        phase_list = self._build_phase_list(phase_log)
        variables["SCHEMA_TDD_PHASES"] = phase_list

        # Mandatory phases with descriptions
        mandatory = self.schema.get("task_specification", {}).get(
            "mandatory_phases", []
        )
        variables["MANDATORY_PHASES"] = self._format_mandatory_phases(mandatory)

        # Phase execution log schema (for reference)
        variables["PHASE_EXECUTION_LOG"] = json.dumps(phase_log[0], indent=2)

        return variables

    def _build_phase_list(self, phase_log: List[Dict]) -> str:
        """Build formatted TDD phase list from schema."""
        lines = [
            "## TDD Phases (from canonical schema)",
            "",
            "The system uses the following TDD phases as defined in "
            "`nWave/templates/step-tdd-cycle-schema.json`:",
            "",
        ]

        for i, phase in enumerate(phase_log, 1):
            phase_name = phase.get("phase_name", "UNKNOWN")
            notes = phase.get("notes", "")

            if notes:
                lines.append(f"{i}. **{phase_name}** - {notes}")
            else:
                lines.append(f"{i}. **{phase_name}**")

        lines.extend(
            [
                "",
                f"**Total Phases:** {len(phase_log)}",
                f"**Schema Version:** {self.schema.get('version')}",
            ]
        )

        return "\n".join(lines)

    def _format_mandatory_phases(self, mandatory: List[str]) -> str:
        """Format mandatory phases list from schema."""
        lines = [
            "### Mandatory TDD Phases",
            "",
            "The following phases are mandatory for every step:",
            "",
        ]

        for i, phase_desc in enumerate(mandatory, 1):
            lines.append(f"{i}. {phase_desc}")

        return "\n".join(lines)

    def process_file(self, input_path: Path, output_path: Path = None) -> str:
        """
        Process template variables in a Markdown file.

        Args:
            input_path: Path to input Markdown file with template variables
            output_path: Path to write processed file (if None, returns string)

        Returns:
            Processed file content as string
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        with open(input_path, "r") as f:
            content = f.read()

        # Replace all template variables
        processed = content
        for var_name, var_value in self.template_variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            processed = processed.replace(placeholder, var_value)

        # Add metadata comment at top if processing
        if output_path:
            with open(output_path, "w") as f:
                f.write(processed)
            return processed

        return processed

    def extract_variables_dict(self) -> Dict[str, str]:
        """Return dictionary of all template variables for inspection."""
        return self.template_variables.copy()

    def validate_file(self, file_path: Path) -> tuple[bool, List[str]]:
        """
        Validate that file has no unprocessed template variables.

        Args:
            file_path: Path to file to validate

        Returns:
            (is_valid: bool, unprocessed_vars: List[str])
        """
        with open(file_path, "r") as f:
            content = f.read()

        # Find any remaining template variables
        pattern = r"\{\{[A-Z_]+\}\}"
        unprocessed = re.findall(pattern, content)

        return len(unprocessed) == 0, list(set(unprocessed))


def main():
    """CLI interface for template processor."""
    import argparse

    parser = argparse.ArgumentParser(description="Process nWave command templates")
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path(__file__).parent.parent.parent
        / "nWave/templates/step-tdd-cycle-schema.json",
        help="Path to canonical schema",
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Input Markdown file with template variables",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file (optional, prints to stdout if not provided)",
    )
    parser.add_argument(
        "--validate", type=Path, help="Validate file has no unprocessed variables"
    )
    parser.add_argument(
        "--dump-vars", action="store_true", help="Print all template variables and exit"
    )

    args = parser.parse_args()

    processor = TemplateProcessor(args.schema)

    if args.dump_vars:
        print("Template Variables:")
        for var_name, var_value in processor.extract_variables_dict().items():
            print(f"\n{var_name}:")
            print("-" * 60)
            print(var_value[:200] + ("..." if len(var_value) > 200 else ""))
        return

    if args.validate:
        is_valid, unprocessed = processor.validate_file(args.validate)
        if is_valid:
            print(f"✓ {args.validate} is valid (no unprocessed variables)")
        else:
            print(f"✗ {args.validate} has unprocessed variables:")
            for var in unprocessed:
                print(f"  - {var}")
        return

    # Process file
    processed = processor.process_file(args.input, args.output)

    if not args.output:
        print(processed)
    else:
        print(f"✓ Processed: {args.input} → {args.output}")


if __name__ == "__main__":
    main()
