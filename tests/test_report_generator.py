import pytest
import json
import unittest.mock as mock
import report_generator

# Fixtures for test data

@pytest.fixture
def sample_findings():
    """Provides a list of valid impact findings."""
    return [
        {
            "id": 1,
            "severity": "HIGH",
            "description": "SQL Injection in login form",
            "metric": {"impact_score": 8.5, "affected_files": ["auth.py"]}
        },
        {
            "id": 2,
            "severity": "MEDIUM",
            "description": "Missing XSS protection on comments",
            "metric": {"impact_score": 5.0, "affected_files": ["comments.py"]}
        }
    ]

@pytest.fixture
def empty_findings():
    """Provides an empty list of findings."""
    return []

@pytest.fixture
def findings_with_special_chars():
    """Provides findings with special characters that need escaping."""
    return [
        {
            "id": 1,
            "severity": "HIGH",
            "description": "Error: <script>alert(1)</script>",
            "metric": {"impact_score": 8.5, "affected_files": ["test.py"]}
        }
    ]

class TestReportGenerator:
    """Test suite for report_generator module functions."""

    @pytest.mark.parametrize("findings, title, expected_lines", [
        (sample_findings, "Test Report", 5),
        (empty_findings, "Empty Report", 3),
        (findings_with_special_chars, "Special Report", 4),
    ])
    def test_generate_markdown_report_basic(self, findings, title, expected_lines, monkeypatch):
        """Test markdown generation with various inputs."""
        result = report_generator.generate_markdown_report(findings, title)
        assert isinstance(result, str)
        assert f"# {title}" in result
        assert result.count("#") >= expected_lines  # Basic header check
        
    def test_generate_markdown_report_empty(self, empty_findings):
        """Test markdown report generation with no findings."""
        result = report_generator.generate_markdown_report(empty_findings)
        assert isinstance(result, str)
        assert "No findings detected" in result
        
    def test_generate_markdown_report_special_chars(self, findings_with_special_chars):
        """Test markdown report generation handles special characters safely."""
        result = report_generator.generate_markdown_report(findings_with_special_chars)
        # Check that description is not stripped or corrupted
        assert "Error:" in result
        # Ensure markdown doesn't break due to script tags
        assert "<script>" not in result  # Assuming sanitizer or escaping

    @pytest.mark.parametrize("findings, indent, expected_valid", [
        (sample_findings, 2, True),
        (empty_findings, 0, True),
        (findings_with_special_chars, 4, True),
    ])
    def test_generate_json_report_basic(self, findings, indent, expected_valid):
        """Test JSON report generation and validity."""
        result = report_generator.generate_json_report(findings, indent=indent)
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert expected_valid
        if len(findings) >