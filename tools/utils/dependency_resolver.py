"""
Dependency Resolver

Resolves and embeds dependencies for nWave agents and other components.
Handles {root} placeholder resolution, content embedding with proper formatting,
BUILD:INCLUDE markers, and BUILD:INJECT coexistence.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Set


class DependencyResolver:
    """Resolves and embeds dependencies for agent files."""

    def __init__(self, source_dir: Path, file_manager):
        self.source_dir = Path(source_dir)
        self.file_manager = file_manager

        # Define dependency type mappings
        self.dependency_mappings = {
            "tasks": "tasks",
            "templates": "templates",
            "checklists": "checklists",
            "data": "data",
            "utils": "utils",
            "workflows": "workflows",
            "agent-teams": "agent-teams",
            "embed_knowledge": "data",  # embed_knowledge files are under data/embed/
        }

        # Track circular references during BUILD:INCLUDE resolution
        self._include_stack: Set[str] = set()

    def parse_build_include_markers(self, content: str) -> List[Dict[str, str]]:
        """
        Parse BUILD:INCLUDE markers from content.

        Marker format: {{ BUILD:INCLUDE file_path }}

        Args:
            content: Content to parse

        Returns:
            list: List of dicts with 'marker' (full text) and 'path' (file path)
        """
        pattern = r"{{\s*BUILD:INCLUDE\s+([^\s}]+)\s*}}"
        matches = re.finditer(pattern, content)

        markers = []
        for match in matches:
            markers.append({"marker": match.group(0), "path": match.group(1)})

        return markers

    def resolve_build_include_markers(
        self, content: str, source_file: Optional[Path] = None
    ) -> str:
        """
        Resolve BUILD:INCLUDE markers by replacing with file content.

        Args:
            content: Content with BUILD:INCLUDE markers
            source_file: Path to source file (for relative path resolution)

        Returns:
            str: Content with markers replaced

        Raises:
            ValueError: If circular reference detected or file not found
        """
        markers = self.parse_build_include_markers(content)

        if not markers:
            return content

        result = content

        for marker_info in markers:
            marker_text = marker_info["marker"]
            file_path = marker_info["path"]

            # Resolve path (handle relative paths)
            resolved_path = self._resolve_include_path(file_path, source_file)

            if not resolved_path:
                raise ValueError(
                    f"BUILD:INCLUDE file not found: {file_path} "
                    f"(from {source_file or 'unknown'})"
                )

            # Check for circular references
            if str(resolved_path) in self._include_stack:
                raise ValueError(
                    f"Circular BUILD:INCLUDE reference detected: {file_path} "
                    f"(include stack: {' -> '.join(self._include_stack)})"
                )

            # Load included file content
            try:
                included_content = self.file_manager.read_file(resolved_path)
                if not included_content:
                    raise ValueError(f"Could not read BUILD:INCLUDE file: {file_path}")

                # Add to stack to track circular refs
                self._include_stack.add(str(resolved_path))

                # Recursively resolve nested BUILD:INCLUDE markers
                resolved_content = self.resolve_build_include_markers(
                    included_content, resolved_path
                )

                # Remove from stack
                self._include_stack.discard(str(resolved_path))

                # Format for embedding
                file_format = resolved_path.suffix.lstrip(".") or "txt"
                formatted_content = self.format_content_for_embedding(
                    resolved_content, file_format
                )

                # Replace marker with content
                result = result.replace(marker_text, formatted_content)

                logging.debug(
                    f"Resolved BUILD:INCLUDE marker: {file_path} -> {resolved_path} "
                    f"({len(formatted_content)} chars)"
                )

            except Exception as e:
                logging.error(
                    f"Error resolving BUILD:INCLUDE marker '{file_path}': {e}"
                )
                raise ValueError(
                    f"Failed to resolve BUILD:INCLUDE marker '{file_path}': {e}"
                )

        return result

    def _resolve_include_path(
        self, file_path: str, source_file: Optional[Path] = None
    ) -> Optional[Path]:
        """
        Resolve BUILD:INCLUDE file path with security checks.

        Args:
            file_path: Path from marker
            source_file: Source file path (for relative resolution)

        Returns:
            Path: Resolved absolute path or None if not found

        Raises:
            ValueError: If path traversal attack detected
        """
        try:
            # Parse the path
            target_path = Path(file_path)

            # Security check: prevent directory traversal attacks
            if ".." in target_path.parts:
                raise ValueError(
                    f"Path traversal attack detected in BUILD:INCLUDE: {file_path}"
                )

            # If absolute path, use as-is (but still inside project)
            if target_path.is_absolute():
                # Ensure it's within source_dir
                try:
                    target_path.relative_to(self.source_dir)
                except ValueError:
                    raise ValueError(f"BUILD:INCLUDE path outside project: {file_path}")
                resolved = target_path
            else:
                # Relative path: resolve from source file or source_dir
                if source_file and source_file.is_file():
                    resolved = source_file.parent / target_path
                else:
                    resolved = self.source_dir / target_path

                # Normalize and verify still within source_dir
                resolved = resolved.resolve()
                try:
                    resolved.relative_to(self.source_dir)
                except ValueError:
                    raise ValueError(
                        f"BUILD:INCLUDE path outside project: {file_path} "
                        f"(resolved to {resolved})"
                    )

            # Check file exists
            if not resolved.exists():
                logging.warning(f"BUILD:INCLUDE file not found: {resolved}")
                return None

            if not resolved.is_file():
                raise ValueError(f"BUILD:INCLUDE path is not a file: {resolved}")

            return resolved

        except ValueError:
            raise
        except Exception as e:
            logging.error(f"Error resolving BUILD:INCLUDE path '{file_path}': {e}")
            return None

    def resolve_dependency_path(
        self, dependency_type: str, dependency_name: str
    ) -> Optional[Path]:
        """
        Resolve the full path to a dependency file.

        Args:
            dependency_type: Type of dependency (tasks, templates, etc.)
            dependency_name: Name of the dependency file

        Returns:
            Path: Full path to dependency file or None if not found
        """
        # Map dependency type to directory
        if dependency_type not in self.dependency_mappings:
            logging.warning(f"Unknown dependency type: {dependency_type}")
            return None

        dir_name = self.dependency_mappings[dependency_type]
        dependency_dir = self.source_dir / dir_name

        # Try to find the file with various approaches
        candidates = [
            dependency_dir / dependency_name,  # Exact match
            dependency_dir / f"{dependency_name}.md",  # Add .md extension
            dependency_dir / f"{dependency_name}.yaml",  # Add .yaml extension
            dependency_dir / f"{dependency_name}.yml",  # Add .yml extension
        ]

        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                logging.debug(
                    f"Resolved dependency: {dependency_type}/{dependency_name} -> {candidate}"
                )
                return candidate

        # Search for partial matches
        if dependency_dir.exists():
            for file_path in dependency_dir.iterdir():
                if (
                    file_path.is_file()
                    and dependency_name.lower() in file_path.name.lower()
                ):
                    logging.debug(
                        f"Found partial match for dependency: {dependency_type}/{dependency_name} -> {file_path}"
                    )
                    return file_path

        logging.warning(
            f"Could not resolve dependency: {dependency_type}/{dependency_name}"
        )
        return None

    def resolve_dependency(
        self, dependency_type: str, dependency_name: str
    ) -> Optional[str]:
        """
        Resolve and load content of a dependency.

        Args:
            dependency_type: Type of dependency
            dependency_name: Name of the dependency file

        Returns:
            str: Dependency content or None if not found
        """
        dependency_path = self.resolve_dependency_path(dependency_type, dependency_name)
        if not dependency_path:
            return None

        content = self.file_manager.read_file(dependency_path)
        if not content:
            logging.error(f"Could not read dependency content: {dependency_path}")
            return None

        logging.debug(
            f"Loaded dependency: {dependency_type}/{dependency_name} ({len(content)} chars)"
        )
        return content

    def resolve_placeholders(
        self, config: Union[Dict[str, Any], List[Any], str]
    ) -> Union[Dict[str, Any], List[Any], str]:
        """
        Resolve {root} placeholders in configuration recursively.

        Args:
            config: Configuration data (dict, list, or string)

        Returns:
            Configuration with resolved placeholders
        """
        if isinstance(config, dict):
            resolved = {}
            for key, value in config.items():
                resolved[key] = self.resolve_placeholders(value)
            return resolved

        elif isinstance(config, list):
            return [self.resolve_placeholders(item) for item in config]

        elif isinstance(config, str):
            # Replace {root} with the source directory path
            if "{root}" in config:
                resolved = config.replace("{root}", str(self.source_dir))
                logging.debug(f"Resolved placeholder: {config} -> {resolved}")
                return resolved
            return config

        else:
            # Return non-string, non-dict, non-list values as-is
            return config

    def get_dependency_metadata(
        self, dependency_type: str, dependency_name: str
    ) -> Dict[str, Any]:
        """
        Get metadata about a dependency.

        Args:
            dependency_type: Type of dependency
            dependency_name: Name of the dependency file

        Returns:
            dict: Dependency metadata
        """
        dependency_path = self.resolve_dependency_path(dependency_type, dependency_name)
        if not dependency_path:
            return {
                "exists": False,
                "type": dependency_type,
                "name": dependency_name,
                "path": None,
                "size": 0,
                "format": "unknown",
            }

        try:
            stat = dependency_path.stat()
            return {
                "exists": True,
                "type": dependency_type,
                "name": dependency_name,
                "path": str(dependency_path),
                "size": stat.st_size,
                "format": dependency_path.suffix.lstrip(".") or "unknown",
                "modified": stat.st_mtime,
            }
        except Exception as e:
            logging.error(f"Error getting dependency metadata: {e}")
            return {
                "exists": False,
                "type": dependency_type,
                "name": dependency_name,
                "path": str(dependency_path) if dependency_path else None,
                "size": 0,
                "format": "unknown",
            }

    def validate_dependencies(
        self, dependencies: Dict[str, List[str]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Validate all dependencies in a configuration.

        Args:
            dependencies: Dependencies configuration

        Returns:
            dict: Validation results by dependency type
        """
        validation_results = {}

        for dep_type, dep_files in dependencies.items():
            type_results = []

            for dep_file in dep_files:
                metadata = self.get_dependency_metadata(dep_type, dep_file)
                type_results.append(metadata)

            validation_results[dep_type] = type_results

        return validation_results

    def get_missing_dependencies(
        self, dependencies: Dict[str, List[str]]
    ) -> List[Dict[str, str]]:
        """
        Get list of missing dependencies.

        Args:
            dependencies: Dependencies configuration

        Returns:
            list: List of missing dependencies
        """
        missing = []
        validation_results = self.validate_dependencies(dependencies)

        for dep_type, results in validation_results.items():
            for result in results:
                if not result["exists"]:
                    missing.append(
                        {
                            "type": dep_type,
                            "name": result["name"],
                            "expected_path": result["path"],
                        }
                    )

        return missing

    def format_content_for_embedding(self, content: str, file_format: str) -> str:
        """
        Format content appropriately for embedding in markdown.

        Args:
            content: Raw content
            file_format: File format (md, yaml, yml, txt, etc.)

        Returns:
            str: Formatted content for embedding
        """
        if not content:
            return ""

        # Determine how to format based on file extension
        if file_format.lower() in ["yaml", "yml"]:
            # Embed YAML as code block
            return f"```yaml\n{content.strip()}\n```"

        elif file_format.lower() in ["json"]:
            # Embed JSON as code block
            return f"```json\n{content.strip()}\n```"

        elif file_format.lower() in ["py", "python"]:
            # Embed Python as code block
            return f"```python\n{content.strip()}\n```"

        elif file_format.lower() in ["js", "javascript"]:
            # Embed JavaScript as code block
            return f"```javascript\n{content.strip()}\n```"

        elif file_format.lower() in ["sh", "bash"]:
            # Embed shell scripts as code block
            return f"```bash\n{content.strip()}\n```"

        elif file_format.lower() in ["md", "markdown"]:
            # Embed markdown directly (but clean up any conflicting headers)
            return self._clean_markdown_for_embedding(content)

        else:
            # For unknown formats, treat as plain text in code block
            return f"```\n{content.strip()}\n```"

    def _clean_markdown_for_embedding(self, markdown_content: str) -> str:
        """
        Clean markdown content for safe embedding.

        Args:
            markdown_content: Original markdown content

        Returns:
            str: Cleaned markdown content
        """
        # Remove any YAML front matter
        content = re.sub(r"^---\n.*?\n---\n", "", markdown_content, flags=re.DOTALL)

        # Ensure proper spacing
        content = content.strip()

        return content

    def resolve_all_dependencies(
        self, dependencies: Dict[str, List[str]]
    ) -> Dict[str, Dict[str, str]]:
        """
        Resolve all dependencies and return their content.

        Args:
            dependencies: Dependencies configuration

        Returns:
            dict: Resolved dependencies by type and name
        """
        resolved = {}

        for dep_type, dep_files in dependencies.items():
            resolved[dep_type] = {}

            for dep_file in dep_files:
                content = self.resolve_dependency(dep_type, dep_file)
                if content:
                    # Get file format for proper embedding
                    dep_path = self.resolve_dependency_path(dep_type, dep_file)
                    file_format = dep_path.suffix.lstrip(".") if dep_path else "txt"

                    # Format content for embedding
                    formatted_content = self.format_content_for_embedding(
                        content, file_format
                    )
                    resolved[dep_type][dep_file] = formatted_content
                else:
                    logging.warning(
                        f"Could not resolve dependency: {dep_type}/{dep_file}"
                    )

        return resolved

    def create_dependency_summary(self, dependencies: Dict[str, List[str]]) -> str:
        """
        Create a summary of dependencies for documentation.

        Args:
            dependencies: Dependencies configuration

        Returns:
            str: Dependency summary
        """
        validation_results = self.validate_dependencies(dependencies)
        missing = self.get_missing_dependencies(dependencies)

        summary_parts = ["## Dependency Summary\n"]

        # Count totals
        total_deps = sum(len(files) for files in dependencies.values())
        missing_count = len(missing)
        resolved_count = total_deps - missing_count

        summary_parts.extend(
            [
                f"- **Total Dependencies**: {total_deps}",
                f"- **Resolved**: {resolved_count}",
                f"- **Missing**: {missing_count}",
                "",
            ]
        )

        # List by type
        for dep_type, results in validation_results.items():
            if not results:
                continue

            summary_parts.append(f"### {dep_type.title()}")
            summary_parts.append("")

            for result in results:
                status = "✅" if result["exists"] else "❌"
                size_info = f" ({result['size']} bytes)" if result["exists"] else ""
                summary_parts.append(f"- {status} {result['name']}{size_info}")

            summary_parts.append("")

        return "\n".join(summary_parts)

    def verify_build_include_and_inject_coexistence(
        self, content: str
    ) -> Dict[str, Any]:
        """
        Verify that BUILD:INCLUDE and BUILD:INJECT mechanisms work together.

        Args:
            content: Content to check

        Returns:
            dict: Verification results with 'valid' bool and 'findings' list
        """
        findings = []

        # Parse both types of markers
        include_markers = self.parse_build_include_markers(content)
        inject_pattern = r"BUILD:INJECT\s+(\w+)\s+(\S+)"
        inject_matches = re.finditer(inject_pattern, content)
        inject_markers = [
            {"type": m.group(1), "target": m.group(2)} for m in inject_matches
        ]

        # Check for conflicts (same file referenced in both)
        include_files = {m["path"] for m in include_markers}
        inject_targets = {m["target"] for m in inject_markers}

        conflicts = include_files & inject_targets
        if conflicts:
            findings.append(
                {
                    "level": "warning",
                    "message": f"Files referenced in both BUILD:INCLUDE and BUILD:INJECT: {conflicts}",
                    "type": "coexistence_conflict",
                }
            )

        # Verify BUILD:INCLUDE files exist
        for marker in include_markers:
            resolved_path = self._resolve_include_path(marker["path"])
            if not resolved_path:
                findings.append(
                    {
                        "level": "error",
                        "message": f'BUILD:INCLUDE file not found: {marker["path"]}',
                        "type": "missing_include_file",
                    }
                )

        # Check for circular references in BUILD:INCLUDE chain
        for marker in include_markers:
            try:
                self._include_stack.clear()
                self.resolve_build_include_markers(
                    f"{{{{ BUILD:INCLUDE {marker['path']} }}}}"
                )
            except ValueError as e:
                findings.append(
                    {"level": "error", "message": str(e), "type": "circular_reference"}
                )

        return {
            "valid": len([f for f in findings if f["level"] == "error"]) == 0,
            "findings": findings,
            "include_markers_count": len(include_markers),
            "inject_markers_count": len(inject_markers),
            "conflicts": list(conflicts),
        }
