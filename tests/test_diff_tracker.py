import pytest
from unittest import mock
from diff_tracker import get_commit_diff, get_affected_lines, analyze_impact_score

# Fixtures

@pytest.fixture
def mock_git_repo_path():
    return "/path/to/repo"

@pytest.fixture
def mock_commit_data():
    return {
        "files": [
            {"path": "main.py", "changes": [{"line": 10, "type": "add"}, {"line": 15, "type": "modify"}]},
            {"path": "utils.py", "changes": [{"line": 20, "type": "delete"}]}
        ]
    }

@pytest.fixture
def mock_severity_context():
    return {"critical_files": ["main.py"], "weights": {"add": 1, "modify": 2, "delete": 3}}

@pytest.fixture
def subprocess_mock():
    with mock.patch('subprocess.run') as mock_run:
        mock_run.return_value = mock.MagicMock(returncode=0, stdout=b"diff output", stderr=b"")
        yield mock_run

# Tests for get_commit_diff

@pytest.mark.usefixtures("subprocess_mock")
class TestGetCommitDiff:
    
    def test_get_commit_diff_success(self, mock_git_repo_path, subprocess_mock, mock_commit_data):
        with mock.patch('diff_tracker.get_commit_data', return_value=mock_commit_data):
            result = get_commit_diff(mock_git_repo_path, "abc123", "def456")
            assert result is not None
            assert "files" in result
            assert subprocess_mock.called

    def test_get_commit_diff_invalid_repo(self, mock_git_repo_path):
        with mock.patch('diff_tracker.os.path.isdir', return_value=False):
            with pytest.raises(FileNotFoundError):
                get_commit_diff("/nonexistent/path", "abc123", "def456")

    def test_get_commit_diff_git_fail(self, mock_git_repo_path, subprocess_mock):
        subprocess_mock.return_value.returncode = 1
        subprocess_mock.return_value.stderr = b"git error"
        
        with pytest.raises(RuntimeError) as exc_info:
            get_commit_diff(mock_git_repo_path, "abc123", "def456")
        
        assert "git error" in str(exc_info.value)

# Tests for get_affected_lines

@pytest.mark.usefixtures("mock_commit_data")
class TestGetAffectedLines:

    def test_get_affected_lines_success(self, mock_commit_data):
        lines = get_affected_lines(mock_commit_data)
        assert len(lines) > 0
        assert all(isinstance(line, dict) for line in lines)

    def test_get_affected_lines_empty_diff(self):
        empty_data = {"files": []}
        lines = get_affected_lines(empty_data)
        assert lines == []

    def test_get_affected_lines_invalid_format(self):
        invalid_data = "not a dict"
        with pytest.raises(TypeError):
            get_affected_lines(invalid_data)

# Tests for analyze_impact_score

@pytest.mark.usefixtures("mock_severity_context")
class TestAnalyzeImpactScore:

    def test_analyze_impact_score_calculated(self, mock_severity_context):
        test_lines = [{"file": "main.py", "type": "add"}]
        score = analyze_impact_score(test_lines, mock_severity_context)
        assert isinstance(score, int)
        assert score >= 0

    def test_analyze_impact_score_empty_lines(self, mock_severity_context):
        score = analyze_impact_score([], mock_severity_context)
        assert score == 0

    def test_analyze_impact_score_missing_file_critical(self, mock_severity_context):
        test_lines = [{"file": "utils.py", "type": "modify"}]
        score = analyze_impact_score(test_lines, mock_severity_context)
        # Should be low as utils.py is not critical
        assert score < 2

    def test_analyze_impact_score_missing_critical_weight(self, mock_severity_context):
        # Simulate a scenario where context has missing weight keys gracefully
        test_lines = [{"file": "main.py", "type": "modify"}]
        modified_context = mock_severity_context.copy()
        modified_context["weights"] = {}
        # Depending on implementation, might return 0 or raise, testing robustness
        score = analyze_impact_score(test_lines, modified_context)
        assert score >= 0