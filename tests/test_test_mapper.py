import pytest
from unittest import mock
from test_mapper import (
    map_code_changes,
    get_tests_for_paths,
    validate_impact_report,
    generate_impact_summary
)

# Mock classes for external dependencies


class MockRepoClient:
    def get_diff(self, commit_id):
        return [{"file": "src/core/auth.py", "status": "modified"}]

    def find_tests(self, file_path):
        return ["tests/unit/test_auth.py", "tests/integration/test_auth_flow.py"]


class MockTestRegistryClient:
    def lookup_tests(self, paths):
        return {p: ["test_1", "test_2"] for p in paths}


# Fixtures


@pytest.fixture
def sample_changes():
    return [
        {"file": "src/utils.py", "status": "modified", "commit_id": "abc123"},
        {"file": "src/exceptions.py", "status": "added", "commit_id": "abc123"}
    ]


@pytest.fixture
def empty_changes():
    return []


@pytest.fixture
def valid_mapping():
    return {
        "src/utils.py": ["tests/unit/test_utils.py"],
        "src/exceptions.py": ["tests/unit/test_exceptions.py"]
    }


@pytest.fixture
def invalid_mapping_missing_file():
    return {
        "src/utils.py": []
    }


@pytest.fixture
def mock_repo_client():
    with mock.patch('test_mapper.RepoClient') as mock_client:
        client_instance = MockRepoClient()
        mock_client.return_value = client_instance
        yield mock_client


@pytest.fixture
def mock_registry_client():
    with mock.patch('test_mapper.TestRegistryClient') as mock_client:
        client_instance = MockTestRegistryClient()
        mock_client.return_value = client_instance
        yield mock_client


# Test Functions


class TestMapCodeChanges:
    def test_map_happy_path(self, sample_changes, mock_repo_client, mock_registry_client):
        result = map_code_changes(sample_changes)
        assert len(result) > 0
        assert all(isinstance(entry, dict) for entry in result)
        assert 'file' in result[0] or 'test' in result[0]

    def test_map_no_changes(self, empty_changes, mock_repo_client, mock_registry_client):
        result = map_code_changes(empty_changes)
        assert result == []

    def test_map_repo_error(self, sample_changes, mock_repo_client, mock_registry_client):
        mock_repo_client.return_value.get_diff.side_effect = Exception("Repo unavailable")
        with pytest.raises(Exception):
            map_code_changes(sample_changes)


class TestGetTestsForPaths:
    def test_get_tests_happy_path(self, mock_registry_client):
        paths = ["src/utils.py", "src/exceptions.py"]
        result = get_tests_for_paths(paths)
        assert "src/utils.py" in result
        assert "src/exceptions.py" in result

    def test_get_tests_no_tests_found(self, mock_registry_client):
        paths = ["src/unknown.py"]
        mock_registry_client.return_value.lookup_tests.return_value = {}
        result = get_tests_for_paths(paths)
        assert "src/unknown.py" not in result or result["src/unknown.py"] == []

    def test_get_tests_invalid_path_format(self):
        paths = [None, "src/utils.py"]
        with pytest.raises(ValueError):
            get_tests_for_paths(paths)


class TestValidateImpactReport:
    def test_validate_report_valid(self, valid_mapping):
        assert validate_impact_report(valid_mapping) is True

    def test_validate_report_missing_keys(self, invalid_mapping_missing_file):
        assert validate_impact_report(invalid_mapping_missing_file) is False

    def test_validate_report_none_input(self):
        assert validate_impact_report(None) is False


class TestGenerateImpactSummary:
    def test_summary_with_data(self, valid_mapping, mock_registry_client):
        result = generate_impact_summary(valid_mapping)
        assert "total_tests" in result
        assert "total_files" in result
        assert result["total_files"] == 2

    def test_summary_empty_mapping(self):
        result = generate_impact_summary({})
        assert result["total_files"] == 0
        assert result["total_tests"] == 0

    def test_summary_invalid_structure(self):
        result = generate_impact_summary("invalid_string")
        assert result == {"error": "Invalid mapping structure"}