import pytest
from unittest.mock import patch, MagicMock, mock_open
import graph_builder
import os
import ast

# Fixtures

@pytest.fixture
def mock_file_content():
    """Returns mock file content for testing."""
    return """
import requests
from graph_builder import build_dependency_graph

def main():
    print('Hello World')
    pass
"""

@pytest.fixture
def mock_ast_tree(mock_file_content):
    """Returns a mock AST tree object."""
    mock_tree = MagicMock(spec=ast.Module)
    mock_tree.body = [
        MagicMock(spec=ast.Import),
        MagicMock(spec=ast.FunctionDef, name='main'),
    ]
    return mock_tree

@pytest.fixture
def mock_external_api_response():
    """Returns mock response for external dependency checks."""
    return {
        'status': 'success',
        'version': '1.0.0',
        'dependencies': ['requests', 'graph_builder']
    }

@pytest.fixture
def mock_path_join():
    """Mock os.path.join to prevent actual path manipulation."""
    with patch('os.path.join') as mock_join:
        mock_join.return_value = '/mocked/path'
        yield mock_join

# Test Cases for Dependency Graph Builder

class TestDependencyGraphBuilder:
    """Tests for build_dependency_graph function."""

    @patch('graph_builder.parse_file')
    @patch('graph_builder.os.path.exists')
    def test_build_graph_happy_path(self, mock_exists, mock_parse):
        """Test successful graph construction."""
        mock_exists.return_value = True
        mock_parse.return_value = {
            'imports': ['os', 'sys'],
            'functions': ['main', 'helper']
        }
        
        files = ['/path/to/main.py', '/path/to/util.py']
        result = graph_builder.build_dependency_graph(files)
        
        assert 'nodes' in result
        assert 'edges' in result
        assert len(result['nodes']) >= len(files)

    @patch('graph_builder.parse_file')
    @patch('graph_builder.os.path.exists')
    def test_build_graph_missing_file(self, mock_exists, mock_parse):
        """Test handling of non-existent files."""
        mock_exists.return_value = False
        mock_parse.return_value = {}
        
        files = ['/nonexistent/file.py']
        result = graph_builder.build_dependency_graph(files)
        
        assert 'warnings' in result
        assert len(result['warnings']) > 0

    @patch('graph_builder.os.path.exists')
    def test_build_graph_permission_error(self, mock_exists):
        """Test handling of permission denied errors."""
        mock_exists.side_effect = PermissionError("Access denied")
        
        files = ['/root/system/file.py']
        with pytest.raises(Exception):
            graph_builder.build_dependency_graph(files)

# Test Cases for Call Graph Builder

class TestCallGraphBuilder:
    """Tests for build_call_graph function."""

    @patch('graph_builder.parse_file_content')
    @patch('graph_builder.os.path.getmtime')
    def test_call_graph_extraction(self, mock_mtime, mock_content):
        """Test extraction of call relationships."""
        mock_mtime.return_value = 1000.0
        mock_content.return_value = {
            'calls': [{'target': 'helper', 'line': 10}],
            'defs': ['main']
        }
        
        file_path = '/test/file.py'
        result = graph_builder.build_call_graph(file_path)
        
        assert 'calls' in result
        assert 'defs' in result

    @patch('graph_builder.parse_file_content')
    @patch('os.path.isfile')
    def test_call_graph_empty_file(self, mock_isfile, mock_content):
        """Test handling of empty source files."""
        mock_isfile.return_value = True
        mock_content.return_value = {'calls': [], 'defs': []}
        
        file_path = '/test/empty.py'
        result = graph_builder.build_call_graph(file_path)
        
        assert len(result['calls']) == 0

    @patch('graph_builder.parse_file_content')
    @patch('os.path.isfile')
    def test_call_graph_syntax_error(self, mock_isfile, mock_content):
        """Test handling of files with syntax errors."""
        mock_isfile.return_value = True
        mock_content.side_effect = SyntaxError