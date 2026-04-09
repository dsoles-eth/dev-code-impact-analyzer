import ast
import logging
import os
import typing
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Union

import networkx as nx


@dataclass
class CodeElement:
    """Represents a code element such as a function, class, or variable."""
    name: str
    type: str  # 'function', 'class', 'variable', 'import'
    line_no: int
    file_path: str
    children: List[str] = field(default_factory=list)


@dataclass
class ParsingResult:
    """Container for the result of parsing a source code file."""
    file_path: str
    ast_tree: ast.Module
    elements: List[CodeElement]
    imports: Set[str]
    errors: List[str] = field(default_factory=list)


class AstParser:
    """
    Parser for Python source code that extracts structural information
    and constructs dependency graphs for impact analysis.
    """

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def parse_source(self, source_code: str) -> ast.Module:
        """
        Parses a string containing Python source code into an AST.

        Args:
            source_code: The raw Python source code string to parse.

        Returns:
            ast.Module: The root node of the generated Abstract Syntax Tree.

        Raises:
            SyntaxError: If the source code contains syntax errors.
        """
        try:
            tree = ast.parse(source_code)
            return tree
        except SyntaxError as e:
            self._logger.error(f"Syntax error in source code: {e}")
            raise SyntaxError(f"Failed to parse source code at line {e.lineno}: {e.msg}")
        except Exception as e:
            self._logger.error(f"Unexpected error during parsing: {e}")
            raise RuntimeError(f"Failed to parse source code: {str(e)}")

    def parse_file(self, file_path: Union[str, Path]) -> ParsingResult:
        """
        Reads a file from the filesystem and parses its content into an AST.

        Args:
            file_path: The path to the Python source file.

        Returns:
            ParsingResult: An object containing the AST, extracted elements, and errors.
        """
        result = ParsingResult(
            file_path=str(file_path),
            ast_tree=ast.Module(),
            elements=[],
            imports=set()
        )
        
        path_obj = Path(file_path)

        try:
            if not path_obj.exists():
                result.errors.append(f"File not found: {path_obj}")
                return result
            
            with open(path_obj, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            result.ast_tree = self.parse_source(source_code)
            result.imports, result.elements = self._analyze_structure(result.ast_tree, str(path_obj))
            
        except IOError as e:
            result.errors.append(f"IOError reading file: {e}")
            self._logger.error(f"IOError reading file {path_obj}: {e}")
        except UnicodeDecodeError as e:
            result.errors.append(f"Encoding error: {e}")
            self._logger.error(f"Encoding error in {path_obj}: {e}")
        except Exception as e:
            result.errors.append(f"Unexpected error during file parsing: {e}")
            self._logger.error(f"Unexpected error in file parsing: {str(e)}")

        return result

    def _analyze_structure(self, tree: ast.Module, file_path: str) -> typing.Tuple[Set[str], List[CodeElement]]:
        """
        Internal method to traverse the AST and extract relevant structural information.

        Args:
            tree: The AST Module node.
            file_path: Absolute or relative path to the source file.

        Returns:
            Tuple containing a set of import names and a list of extracted CodeElements.
        """
        imports: Set[str] = set()
        elements: List[CodeElement] = []
        
        for node in ast.walk(tree):
            self._process_node