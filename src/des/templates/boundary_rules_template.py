"""
BOUNDARY_RULES template for DES-validated prompts.

This module defines the structure and content for the BOUNDARY_RULES section
that prevents agent scope creep by explicitly defining allowed and forbidden actions.
"""


class BoundaryRulesTemplate:
    """
    Template for BOUNDARY_RULES section in DES-validated prompts.

    The section includes:
    1. Section header (## BOUNDARY_RULES)
    2. ALLOWED subsection (permitted files and actions)
    3. FORBIDDEN subsection (prohibited actions and scope expansion)
    """

    def render(self) -> str:
        """
        Render the complete BOUNDARY_RULES section.

        Returns:
            str: Markdown-formatted section with header, ALLOWED, and FORBIDDEN subsections
        """
        return """## BOUNDARY_RULES

**ALLOWED**:
- Modify step file to record phase outcomes and state changes
- Modify task implementation files as specified in step scope
- Modify test files matching the feature being implemented

**FORBIDDEN**:
- Modify other step files or tasks outside current assignment
- Modify files not specified in step scope or allowed patterns
- Continue to next step after completion - return control immediately
"""
