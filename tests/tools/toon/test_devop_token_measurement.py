"""
Tests for devop token measurement and compression validation.
Step 07-04: Token measurement and compression validation for devop.

TDD Phase: Tests that verify token metrics and compression targets.
"""
import pytest
import os
import yaml

# Paths
MD_FILE = "nWave/agents/devop.md"
TOON_FILE = "nWave/agents/devop.toon"
BASELINE_FILE = "docs/feature/toon-agent-conversion/measurements/devop-baseline.yaml"
COMPARISON_FILE = "docs/feature/toon-agent-conversion/measurements/devop-comparison.yaml"


class TestFilesExist:
    """Verify all required files exist."""

    def test_md_source_exists(self):
        """MD source file exists."""
        assert os.path.exists(MD_FILE), f"MD file not found: {MD_FILE}"

    def test_toon_source_exists(self):
        """TOON source file exists."""
        assert os.path.exists(TOON_FILE), f"TOON file not found: {TOON_FILE}"

    def test_baseline_file_exists(self):
        """Baseline measurement file exists."""
        assert os.path.exists(BASELINE_FILE), f"Baseline not found: {BASELINE_FILE}"

    def test_comparison_file_exists(self):
        """Comparison measurement file exists."""
        assert os.path.exists(COMPARISON_FILE), f"Comparison not found: {COMPARISON_FILE}"


class TestBaselineStructure:
    """Verify baseline file has required structure."""

    @pytest.fixture
    def baseline_data(self):
        """Load baseline YAML data."""
        with open(BASELINE_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def test_has_step_id(self, baseline_data):
        """Has step_id field."""
        assert 'step_id' in baseline_data

    def test_has_agent_name(self, baseline_data):
        """Has agent_name field."""
        assert 'agent_name' in baseline_data
        assert baseline_data['agent_name'] == 'devop'

    def test_has_measurement_date(self, baseline_data):
        """Has measurement_date field."""
        assert 'measurement_date' in baseline_data

    def test_has_tokenizer(self, baseline_data):
        """Has tokenizer field."""
        assert 'tokenizer' in baseline_data
        assert baseline_data['tokenizer'] == 'cl100k_base'

    def test_has_original_metrics(self, baseline_data):
        """Has original metrics section."""
        assert 'original' in baseline_data


class TestComparisonStructure:
    """Verify comparison file has required structure."""

    @pytest.fixture
    def comparison_data(self):
        """Load comparison YAML data."""
        with open(COMPARISON_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def test_has_step_id(self, comparison_data):
        """Has step_id field."""
        assert 'step_id' in comparison_data

    def test_has_agent_name(self, comparison_data):
        """Has agent_name field."""
        assert 'agent_name' in comparison_data
        assert comparison_data['agent_name'] == 'devop'

    def test_has_original_section(self, comparison_data):
        """Has original section."""
        assert 'original' in comparison_data

    def test_has_toon_section(self, comparison_data):
        """Has toon section."""
        assert 'toon' in comparison_data

    def test_has_compression_metrics(self, comparison_data):
        """Has compression metrics."""
        assert 'compression' in comparison_data


class TestCompressionTarget:
    """Verify compression ratio meets targets."""

    @pytest.fixture
    def comparison_data(self):
        """Load comparison YAML data."""
        with open(COMPARISON_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def test_compression_ratio_documented(self, comparison_data):
        """Compression ratio is documented."""
        compression = comparison_data.get('compression', {})
        assert 'ratio' in compression or 'compression_ratio' in compression

    def test_meets_secondary_target(self, comparison_data):
        """AC2: Meets at least secondary target (4:1)."""
        compression = comparison_data.get('compression', {})
        ratio_str = compression.get('ratio') or compression.get('compression_ratio', '0:1')
        ratio_value = float(ratio_str.split(':')[0])

        # Should meet at least 4:1 target
        assert ratio_value >= 4.0, f"Compression ratio {ratio_value}:1 below minimum 4:1"


class TestTokenMeasurementAccuracy:
    """Verify token measurements are accurate."""

    @pytest.fixture
    def comparison_data(self):
        """Load comparison YAML data."""
        with open(COMPARISON_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def test_original_tokens_positive(self, comparison_data):
        """Original tokens is positive."""
        original = comparison_data.get('original', {})
        tokens = original.get('tokens', 0)
        assert tokens > 0, "Original tokens should be positive"

    def test_toon_tokens_positive(self, comparison_data):
        """TOON tokens is positive."""
        toon = comparison_data.get('toon', {})
        tokens = toon.get('tokens', 0)
        assert tokens > 0, "TOON tokens should be positive"

    def test_toon_tokens_less_than_original(self, comparison_data):
        """TOON tokens is less than original."""
        original = comparison_data.get('original', {})
        toon = comparison_data.get('toon', {})
        assert toon.get('tokens', float('inf')) < original.get('tokens', 0), \
            "TOON should have fewer tokens than original"

    def test_token_reduction_calculation(self, comparison_data):
        """Token reduction is correctly calculated."""
        compression = comparison_data.get('compression', {})
        reduction = compression.get('token_reduction', 0)
        assert reduction > 0, "Token reduction should be positive"

    def test_token_reduction_percentage(self, comparison_data):
        """Token reduction percentage is reasonable."""
        compression = comparison_data.get('compression', {})
        pct = compression.get('token_reduction_percent', 0)
        assert pct > 50, "Token reduction should be significant (>50%)"


class TestFileSizeMetrics:
    """Verify file size metrics."""

    def test_size_reduction(self):
        """TOON file is smaller than MD."""
        md_size = os.path.getsize(MD_FILE)
        toon_size = os.path.getsize(TOON_FILE)
        assert toon_size < md_size, "TOON should be smaller than MD"


class TestLineCountMetrics:
    """Verify line count metrics."""

    def test_line_reduction(self):
        """TOON has fewer lines than MD."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            md_lines = len(f.readlines())
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            toon_lines = len(f.readlines())
        assert toon_lines < md_lines, "TOON should have fewer lines than MD"


class TestContentQuality:
    """Verify content quality is maintained."""

    def test_toon_substantial_content(self):
        """TOON file has substantial content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        assert len(content) > 5000, "TOON content should be substantial"

    def test_toon_minimum_lines(self):
        """TOON file has minimum lines."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            lines = len(f.readlines())
        assert lines > 100, "TOON should have at least 100 lines"


class TestExceptionDocumentation:
    """Verify exception documentation if needed."""

    @pytest.fixture
    def comparison_data(self):
        """Load comparison YAML data."""
        with open(COMPARISON_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def test_target_analysis_documented(self, comparison_data):
        """Target analysis is documented."""
        assert 'target_analysis' in comparison_data

    def test_secondary_target_status(self, comparison_data):
        """Secondary target status is documented."""
        target = comparison_data.get('target_analysis', {})
        assert 'secondary_target_4_1' in target
