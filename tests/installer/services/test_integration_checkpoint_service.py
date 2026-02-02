"""Tests for IntegrationCheckpointService.

Tests verify:
- CheckpointData dataclass creation with all fields
- CheckpointResult dataclass with passed/failed states
- verify_checkpoint passes when all data matches
- verify_checkpoint fails when version mismatches
- verify_checkpoint fails when wheel_path mismatches
- verify_checkpoint fails when counts mismatch
- display_lines includes 'INTEGRATION CHECKPOINT' header
- display_lines shows checkmarks for passed checks
- display_lines shows X for failed checks
- mismatch details show expected vs actual values
"""

from pathlib import Path

import pytest

from crafter_ai.installer.services.integration_checkpoint_service import (
    CheckpointData,
    CheckpointResult,
    IntegrationCheckpointService,
)


class TestCheckpointData:
    """Tests for CheckpointData dataclass."""

    def test_checkpoint_data_has_all_required_fields(self) -> None:
        """CheckpointData should have all required fields."""
        data = CheckpointData(
            version="1.3.0-dev-20260201-001",
            wheel_path=Path("dist/nwave-1.3.0.dev20260201001-py3-none-any.whl"),
            agent_count=47,
            command_count=23,
            template_count=12,
        )

        assert data.version == "1.3.0-dev-20260201-001"
        assert data.wheel_path == Path(
            "dist/nwave-1.3.0.dev20260201001-py3-none-any.whl"
        )
        assert data.agent_count == 47
        assert data.command_count == 23
        assert data.template_count == 12

    def test_checkpoint_data_allows_none_wheel_path(self) -> None:
        """CheckpointData should allow None for wheel_path."""
        data = CheckpointData(
            version="1.3.0",
            wheel_path=None,
            agent_count=47,
            command_count=23,
            template_count=12,
        )

        assert data.wheel_path is None

    def test_checkpoint_data_is_immutable(self) -> None:
        """CheckpointData should be immutable (frozen)."""
        data = CheckpointData(
            version="1.3.0",
            wheel_path=None,
            agent_count=47,
            command_count=23,
            template_count=12,
        )

        with pytest.raises(AttributeError):
            data.version = "2.0.0"  # type: ignore[misc]


class TestCheckpointResult:
    """Tests for CheckpointResult dataclass."""

    def test_checkpoint_result_has_all_required_fields(self) -> None:
        """CheckpointResult should have all required fields."""
        result = CheckpointResult(
            passed=True,
            mismatches=[],
            version_match=True,
            wheel_path_match=True,
            counts_match=True,
            display_lines=["INTEGRATION CHECKPOINT", "version matches build [check]"],
        )

        assert result.passed is True
        assert result.mismatches == []
        assert result.version_match is True
        assert result.wheel_path_match is True
        assert result.counts_match is True
        assert len(result.display_lines) == 2

    def test_checkpoint_result_with_mismatches(self) -> None:
        """CheckpointResult should store mismatch details."""
        result = CheckpointResult(
            passed=False,
            mismatches=["Version mismatch: expected 1.3.0, found 1.2.0"],
            version_match=False,
            wheel_path_match=True,
            counts_match=True,
            display_lines=["INTEGRATION CHECKPOINT", "version matches build [x]"],
        )

        assert result.passed is False
        assert len(result.mismatches) == 1
        assert "Version mismatch" in result.mismatches[0]


class TestIntegrationCheckpointServiceVerifyCheckpoint:
    """Tests for verify_checkpoint method."""

    @pytest.fixture
    def service(self) -> IntegrationCheckpointService:
        """Create an IntegrationCheckpointService instance."""
        return IntegrationCheckpointService()

    @pytest.fixture
    def matching_expected_data(self) -> CheckpointData:
        """Create expected checkpoint data."""
        return CheckpointData(
            version="1.3.0-dev-20260201-001",
            wheel_path=Path("dist/nwave-1.3.0.dev20260201001-py3-none-any.whl"),
            agent_count=47,
            command_count=23,
            template_count=12,
        )

    @pytest.fixture
    def matching_actual_data(self) -> CheckpointData:
        """Create actual checkpoint data that matches expected."""
        return CheckpointData(
            version="1.3.0-dev-20260201-001",
            wheel_path=Path("dist/nwave-1.3.0.dev20260201001-py3-none-any.whl"),
            agent_count=47,
            command_count=23,
            template_count=12,
        )

    def test_verify_checkpoint_passes_when_all_data_matches(
        self,
        service: IntegrationCheckpointService,
        matching_expected_data: CheckpointData,
        matching_actual_data: CheckpointData,
    ) -> None:
        """verify_checkpoint should pass when all data matches."""
        result = service.verify_checkpoint(matching_expected_data, matching_actual_data)

        assert result.passed is True
        assert result.version_match is True
        assert result.wheel_path_match is True
        assert result.counts_match is True
        assert result.mismatches == []

    def test_verify_checkpoint_fails_when_version_mismatches(
        self,
        service: IntegrationCheckpointService,
        matching_expected_data: CheckpointData,
    ) -> None:
        """verify_checkpoint should fail when version mismatches."""
        mismatched_actual = CheckpointData(
            version="1.2.0",
            wheel_path=matching_expected_data.wheel_path,
            agent_count=matching_expected_data.agent_count,
            command_count=matching_expected_data.command_count,
            template_count=matching_expected_data.template_count,
        )

        result = service.verify_checkpoint(matching_expected_data, mismatched_actual)

        assert result.passed is False
        assert result.version_match is False
        assert any("version" in m.lower() or "Version" in m for m in result.mismatches)

    def test_verify_checkpoint_fails_when_wheel_path_mismatches(
        self,
        service: IntegrationCheckpointService,
        matching_expected_data: CheckpointData,
    ) -> None:
        """verify_checkpoint should fail when wheel_path mismatches."""
        mismatched_actual = CheckpointData(
            version=matching_expected_data.version,
            wheel_path=Path("dist/wrong-wheel.whl"),
            agent_count=matching_expected_data.agent_count,
            command_count=matching_expected_data.command_count,
            template_count=matching_expected_data.template_count,
        )

        result = service.verify_checkpoint(matching_expected_data, mismatched_actual)

        assert result.passed is False
        assert result.wheel_path_match is False
        assert any(
            "wheel" in m.lower() or "path" in m.lower() for m in result.mismatches
        )

    def test_verify_checkpoint_fails_when_agent_count_mismatches(
        self,
        service: IntegrationCheckpointService,
        matching_expected_data: CheckpointData,
    ) -> None:
        """verify_checkpoint should fail when agent_count mismatches."""
        mismatched_actual = CheckpointData(
            version=matching_expected_data.version,
            wheel_path=matching_expected_data.wheel_path,
            agent_count=50,  # Expected 47
            command_count=matching_expected_data.command_count,
            template_count=matching_expected_data.template_count,
        )

        result = service.verify_checkpoint(matching_expected_data, mismatched_actual)

        assert result.passed is False
        assert result.counts_match is False
        assert any("agent" in m.lower() for m in result.mismatches)

    def test_verify_checkpoint_fails_when_command_count_mismatches(
        self,
        service: IntegrationCheckpointService,
        matching_expected_data: CheckpointData,
    ) -> None:
        """verify_checkpoint should fail when command_count mismatches."""
        mismatched_actual = CheckpointData(
            version=matching_expected_data.version,
            wheel_path=matching_expected_data.wheel_path,
            agent_count=matching_expected_data.agent_count,
            command_count=30,  # Expected 23
            template_count=matching_expected_data.template_count,
        )

        result = service.verify_checkpoint(matching_expected_data, mismatched_actual)

        assert result.passed is False
        assert result.counts_match is False
        assert any("command" in m.lower() for m in result.mismatches)

    def test_verify_checkpoint_fails_when_template_count_mismatches(
        self,
        service: IntegrationCheckpointService,
        matching_expected_data: CheckpointData,
    ) -> None:
        """verify_checkpoint should fail when template_count mismatches."""
        mismatched_actual = CheckpointData(
            version=matching_expected_data.version,
            wheel_path=matching_expected_data.wheel_path,
            agent_count=matching_expected_data.agent_count,
            command_count=matching_expected_data.command_count,
            template_count=15,  # Expected 12
        )

        result = service.verify_checkpoint(matching_expected_data, mismatched_actual)

        assert result.passed is False
        assert result.counts_match is False
        assert any("template" in m.lower() for m in result.mismatches)

    def test_verify_checkpoint_multiple_mismatches_all_reported(
        self,
        service: IntegrationCheckpointService,
        matching_expected_data: CheckpointData,
    ) -> None:
        """verify_checkpoint should report all mismatches when multiple occur."""
        mismatched_actual = CheckpointData(
            version="1.2.0",
            wheel_path=Path("dist/wrong-wheel.whl"),
            agent_count=50,
            command_count=30,
            template_count=15,
        )

        result = service.verify_checkpoint(matching_expected_data, mismatched_actual)

        assert result.passed is False
        assert result.version_match is False
        assert result.wheel_path_match is False
        assert result.counts_match is False
        # Should have mismatches for version, wheel path, and each count
        assert len(result.mismatches) >= 3


class TestIntegrationCheckpointServiceDisplayLines:
    """Tests for display_lines in CheckpointResult."""

    @pytest.fixture
    def service(self) -> IntegrationCheckpointService:
        """Create an IntegrationCheckpointService instance."""
        return IntegrationCheckpointService()

    @pytest.fixture
    def matching_data(self) -> CheckpointData:
        """Create matching checkpoint data."""
        return CheckpointData(
            version="1.3.0-dev-20260201-001",
            wheel_path=Path("dist/nwave-1.3.0.dev20260201001-py3-none-any.whl"),
            agent_count=47,
            command_count=23,
            template_count=12,
        )

    def test_display_lines_includes_integration_checkpoint_header(
        self,
        service: IntegrationCheckpointService,
        matching_data: CheckpointData,
    ) -> None:
        """display_lines should include 'INTEGRATION CHECKPOINT' header."""
        result = service.verify_checkpoint(matching_data, matching_data)

        display_text = "\n".join(result.display_lines)
        assert "INTEGRATION CHECKPOINT" in display_text

    def test_display_lines_shows_checkmarks_for_passed_checks(
        self,
        service: IntegrationCheckpointService,
        matching_data: CheckpointData,
    ) -> None:
        """display_lines should show checkmarks for passed checks."""
        result = service.verify_checkpoint(matching_data, matching_data)

        display_text = "\n".join(result.display_lines)
        # Should contain checkmark character or [check] indicator
        assert "\u2713" in display_text or "check" in display_text.lower()

    def test_display_lines_shows_x_for_failed_checks(
        self,
        service: IntegrationCheckpointService,
        matching_data: CheckpointData,
    ) -> None:
        """display_lines should show X for failed checks."""
        mismatched = CheckpointData(
            version="1.2.0",
            wheel_path=matching_data.wheel_path,
            agent_count=matching_data.agent_count,
            command_count=matching_data.command_count,
            template_count=matching_data.template_count,
        )

        result = service.verify_checkpoint(matching_data, mismatched)

        display_text = "\n".join(result.display_lines)
        # Should contain X character or [x] indicator
        assert "\u2717" in display_text or "x" in display_text.lower()

    def test_display_lines_shows_version_matches_build_message(
        self,
        service: IntegrationCheckpointService,
        matching_data: CheckpointData,
    ) -> None:
        """display_lines should show 'version matches build' message."""
        result = service.verify_checkpoint(matching_data, matching_data)

        display_text = "\n".join(result.display_lines)
        assert "version" in display_text.lower()

    def test_display_lines_shows_wheel_path_verified_message(
        self,
        service: IntegrationCheckpointService,
        matching_data: CheckpointData,
    ) -> None:
        """display_lines should show 'wheel path verified' message."""
        result = service.verify_checkpoint(matching_data, matching_data)

        display_text = "\n".join(result.display_lines)
        assert "wheel" in display_text.lower() or "path" in display_text.lower()

    def test_display_lines_shows_artifact_counts_consistent_message(
        self,
        service: IntegrationCheckpointService,
        matching_data: CheckpointData,
    ) -> None:
        """display_lines should show 'artifact counts consistent' message."""
        result = service.verify_checkpoint(matching_data, matching_data)

        display_text = "\n".join(result.display_lines)
        assert "count" in display_text.lower() or "artifact" in display_text.lower()

    def test_display_lines_shows_expected_and_found_on_mismatch(
        self,
        service: IntegrationCheckpointService,
        matching_data: CheckpointData,
    ) -> None:
        """display_lines should show expected vs found values on mismatch."""
        mismatched = CheckpointData(
            version="1.2.0",
            wheel_path=matching_data.wheel_path,
            agent_count=matching_data.agent_count,
            command_count=matching_data.command_count,
            template_count=matching_data.template_count,
        )

        result = service.verify_checkpoint(matching_data, mismatched)

        display_text = "\n".join(result.display_lines)
        # Should show expected and found/actual values
        assert "expected" in display_text.lower() or "Expected" in display_text
        assert (
            "found" in display_text.lower()
            or "Found" in display_text
            or "actual" in display_text.lower()
        )


class TestIntegrationCheckpointServiceIntegration:
    """Integration tests for IntegrationCheckpointService."""

    def test_full_checkpoint_workflow_with_matching_data(self) -> None:
        """Test complete checkpoint workflow with matching data."""
        service = IntegrationCheckpointService()

        expected = CheckpointData(
            version="1.3.0-dev-20260201-001",
            wheel_path=Path("dist/nwave-1.3.0.dev20260201001-py3-none-any.whl"),
            agent_count=47,
            command_count=23,
            template_count=12,
        )

        actual = CheckpointData(
            version="1.3.0-dev-20260201-001",
            wheel_path=Path("dist/nwave-1.3.0.dev20260201001-py3-none-any.whl"),
            agent_count=47,
            command_count=23,
            template_count=12,
        )

        result = service.verify_checkpoint(expected, actual)

        assert result.passed is True
        assert result.version_match is True
        assert result.wheel_path_match is True
        assert result.counts_match is True
        assert len(result.display_lines) > 0
        assert "INTEGRATION CHECKPOINT" in "\n".join(result.display_lines)

    def test_full_checkpoint_workflow_with_mismatched_data(self) -> None:
        """Test complete checkpoint workflow with mismatched data."""
        service = IntegrationCheckpointService()

        expected = CheckpointData(
            version="1.3.0-dev-20260201-001",
            wheel_path=Path("dist/nwave-1.3.0.dev20260201001-py3-none-any.whl"),
            agent_count=47,
            command_count=23,
            template_count=12,
        )

        actual = CheckpointData(
            version="1.2.0",
            wheel_path=Path("dist/nwave-1.2.0-py3-none-any.whl"),
            agent_count=45,
            command_count=20,
            template_count=10,
        )

        result = service.verify_checkpoint(expected, actual)

        assert result.passed is False
        assert result.version_match is False
        assert result.wheel_path_match is False
        assert result.counts_match is False
        assert len(result.mismatches) >= 3
        assert len(result.display_lines) > 0
