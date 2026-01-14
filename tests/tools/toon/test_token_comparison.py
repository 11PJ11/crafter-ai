"""Tests for token comparison between original MD and TOON format

Step 02-04 acceptance criteria validation:
- Token reduction >= 50% for production viability
- Compression ratio documented
- Both original and TOON measurements present
- Comparison file has all required fields
"""

import json
from pathlib import Path

import pytest

# File paths
COMPARISON_PATH = Path("baseline/token-measurements/02-04-token-comparison.json")
BASELINE_PATH = Path("baseline/token-measurements/02-01-pre-conversion.json")
TOON_FILE = Path("nWave/agents/software-crafter.toon")


@pytest.fixture
def comparison_data():
    """Load token comparison data."""
    return json.loads(COMPARISON_PATH.read_text())


@pytest.fixture
def baseline_data():
    """Load baseline data."""
    return json.loads(BASELINE_PATH.read_text())


class TestComparisonFileExists:
    """Verify comparison file exists with valid structure."""

    def test_comparison_file_exists(self):
        assert COMPARISON_PATH.exists(), f"Comparison file not found: {COMPARISON_PATH}"

    def test_baseline_file_exists(self):
        assert BASELINE_PATH.exists(), f"Baseline file not found: {BASELINE_PATH}"

    def test_toon_file_exists(self):
        assert TOON_FILE.exists(), f"TOON file not found: {TOON_FILE}"


class TestComparisonStructure:
    """Verify comparison file has required fields."""

    def test_has_step_id(self, comparison_data):
        assert comparison_data["step_id"] == "02-04"

    def test_has_comparison_date(self, comparison_data):
        assert "comparison_date" in comparison_data
        assert "T" in comparison_data["comparison_date"]

    def test_has_tokenizer(self, comparison_data):
        assert comparison_data["tokenizer"] == "tiktoken/cl100k_base"

    def test_has_original_section(self, comparison_data):
        assert "original" in comparison_data
        original = comparison_data["original"]
        assert "file_path" in original
        assert "total_tokens" in original
        assert "file_size_bytes" in original
        assert "line_count" in original

    def test_has_toon_section(self, comparison_data):
        assert "toon" in comparison_data
        toon = comparison_data["toon"]
        assert "file_path" in toon
        assert "total_tokens" in toon
        assert "file_size_bytes" in toon
        assert "line_count" in toon

    def test_has_compression_metrics(self, comparison_data):
        assert "compression_metrics" in comparison_data
        metrics = comparison_data["compression_metrics"]
        assert "token_reduction" in metrics
        assert "token_reduction_percentage" in metrics
        assert "compression_ratio" in metrics


class TestTokenReductionTarget:
    """AC: Token reduction >= 50% for production viability."""

    def test_token_reduction_percentage_at_least_50(self, comparison_data):
        """Target: >= 50% token reduction."""
        pct = comparison_data["compression_metrics"]["token_reduction_percentage"]
        assert pct >= 50, f"Token reduction {pct}% is below 50% target"

    def test_target_achieved_flag(self, comparison_data):
        """Verify target_achieved flag is True."""
        assert comparison_data["target_achieved"] is True

    def test_compression_ratio_positive(self, comparison_data):
        """Compression ratio should be > 1."""
        ratio_str = comparison_data["compression_metrics"]["compression_ratio"]
        # Parse "6.21:1" format
        ratio = float(ratio_str.split(":")[0])
        assert ratio > 1, f"Compression ratio {ratio} should be > 1"


class TestTokenMeasurementAccuracy:
    """Verify token measurements are accurate."""

    def test_original_tokens_matches_baseline(self, comparison_data, baseline_data):
        """Original tokens should match baseline measurement."""
        assert comparison_data["original"]["total_tokens"] == baseline_data["total_tokens"]

    def test_toon_tokens_positive(self, comparison_data):
        """TOON file should have positive token count."""
        assert comparison_data["toon"]["total_tokens"] > 0

    def test_toon_tokens_less_than_original(self, comparison_data):
        """TOON should have fewer tokens than original."""
        original = comparison_data["original"]["total_tokens"]
        toon = comparison_data["toon"]["total_tokens"]
        assert toon < original, f"TOON ({toon}) should have fewer tokens than original ({original})"

    def test_token_reduction_calculation(self, comparison_data):
        """Verify token reduction calculation is correct."""
        original = comparison_data["original"]["total_tokens"]
        toon = comparison_data["toon"]["total_tokens"]
        expected_reduction = original - toon

        actual_reduction = comparison_data["compression_metrics"]["token_reduction"]
        assert actual_reduction == expected_reduction


class TestLineMeasurements:
    """Verify line count measurements."""

    def test_line_reduction_positive(self, comparison_data):
        """Line count should be reduced."""
        original_lines = comparison_data["original"]["line_count"]
        toon_lines = comparison_data["toon"]["line_count"]
        assert toon_lines < original_lines

    def test_line_reduction_calculation(self, comparison_data):
        """Verify line reduction calculation."""
        original = comparison_data["original"]["line_count"]
        toon = comparison_data["toon"]["line_count"]
        expected = original - toon

        actual = comparison_data["compression_metrics"]["line_reduction"]
        assert actual == expected


class TestSizeMeasurements:
    """Verify file size measurements."""

    def test_size_reduction_positive(self, comparison_data):
        """File size should be reduced."""
        original_size = comparison_data["original"]["file_size_bytes"]
        toon_size = comparison_data["toon"]["file_size_bytes"]
        assert toon_size < original_size

    def test_size_reduction_calculation(self, comparison_data):
        """Verify size reduction calculation."""
        original = comparison_data["original"]["file_size_bytes"]
        toon = comparison_data["toon"]["file_size_bytes"]
        expected = original - toon

        actual = comparison_data["compression_metrics"]["size_reduction_bytes"]
        assert actual == expected


class TestCompressionQuality:
    """Additional compression quality checks."""

    def test_compression_ratio_reasonable(self, comparison_data):
        """Compression ratio should be between 2:1 and 20:1."""
        ratio_str = comparison_data["compression_metrics"]["compression_ratio"]
        ratio = float(ratio_str.split(":")[0])
        assert 2 <= ratio <= 20, f"Compression ratio {ratio} outside expected range 2-20"

    def test_toon_still_substantial(self, comparison_data):
        """TOON file should still have substantial content (> 1000 tokens)."""
        toon_tokens = comparison_data["toon"]["total_tokens"]
        assert toon_tokens > 1000, f"TOON file too small: {toon_tokens} tokens"

    def test_toon_line_count_reasonable(self, comparison_data):
        """TOON file should have reasonable line count (> 100 lines)."""
        toon_lines = comparison_data["toon"]["line_count"]
        assert toon_lines > 100, f"TOON file too short: {toon_lines} lines"
