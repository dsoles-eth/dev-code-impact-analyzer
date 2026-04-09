![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![GitHub Stars](https://img.shields.io/badge/Stars-500-yellow.svg)

# Dev Code Impact Analyzer

**A CLI tool that analyzes code changes to identify affected modules, dependencies, and relevant test suites for faster refactoring and safer deployments.**

`dev-code-impact-analyzer` is designed to minimize risk during backend refactoring and legacy code maintenance. By leveraging static analysis and version control integration, it automatically maps code modifications to their downstream effects, ensuring developers run the correct tests and update affected dependencies before deployment.

## Features

- 🕵️ **Static Analysis**: Parses source code using Python's `ast` module to extract structural information.
- 🕸️ **Dependency Graphing**: Constructs accurate call and dependency graphs between files and functions using `networkx`.
- 🔍 **Change Tracking**: Integrates with `gitpython` to identify specific lines and files affected between commits.
- 📉 **Impact Propagation**: Traverses the dependency graph to calculate downstream effects of any code modification.
- 🧪 **Test Mapping**: Automatically links code changes to relevant unit and integration tests.
- 📄 **Report Generation**: Outputs detailed findings in human-readable Markdown or machine-readable JSON formats.
- 🚀 **High Performance**: Utilizes a persistent cache layer to speed up repeated analysis checks within short timeframes.

## Installation

You can install the tool via PyPI:

```bash
pip install dev-code-impact-analyzer
```

For development purposes:

```bash
git clone https://github.com/your-organization/dev-code-impact-analyzer.git
cd dev-code-impact-analyzer
pip install -e .
```

## Quick Start

To analyze the impact of changes in your current repository:

```bash
$ dci analyze --repo ./my-legacy-app --commit HEAD~1 --output report.md

[+] Analysis Complete
[✓] 4 files modified
[✓] 12 modules affected
[✓] 5 test suites identified
[✓] Cache hit (3.2s)
```

**Sample Report Output:**

```markdown
# Impact Report: HEAD~1 -> HEAD

## Affected Files
- src/auth/login.py
- src/utils/helpers.py

## Affected Modules
- `auth_service`
- `data_validation`

## Suggested Test Suites
- `tests/auth/test_login.py`
- `tests/utils/test_helpers.py`
```

## Usage

The tool offers several commands to assist with different stages of the development workflow.

### Analyze Specific Commit

```bash
dci analyze --repo /path/to/repo --commit <commit-hash> --output-format json
```

### Check Impact of Staged Changes

```bash
dci check-staged --output report.md
```

### Generate Detailed Configuration

```bash
dci init-config
```
*Creates a `.dci_config.yaml` file with default settings for graph depth, ignored directories, and test paths.*

### Help & Documentation

```bash
dci --help
dci analyze --help
```

## Architecture