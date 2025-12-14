# Tests for cdpp/navdex

This directory contains pytest-based tests for the Python logic in the cdpp project, specifically targeting the navdex navigation system.

## Test Structure

- `conftest.py` - Pytest configuration and shared fixtures
- `test_navdex_utils.py` - Tests for utility functions in navdex_core
- `test_index_content.py` - Tests for the IndexContent class (index file management)
- `test_auto_content.py` - Tests for the AutoContent class (.navdex-auto file parsing)
- `test_index_management.py` - Tests for index management functions (findIndex, loadIndex, etc.)
- `test_pattern_resolution.py` - Tests for pattern matching and directory resolution
- `test_setutils.py` - Tests for the IndexedSet class
- `test_termios_proxy.py` - Tests for terminal I/O proxy functions

## Running Tests

### Install Requirements

```bash
pip install -r tests/requirements.txt
```

### Run All Tests

```bash
cd /path/to/cdpp
python3 -m pytest tests/
```

### Run Specific Test File

```bash
python3 -m pytest tests/test_index_content.py
```

### Run with Verbose Output

```bash
python3 -m pytest tests/ -v
```

### Run with Coverage Report

```bash
python3 -m pytest tests/ --cov=bin --cov-report=term-missing
```

### Run Specific Test Class or Method

```bash
python3 -m pytest tests/test_index_content.py::TestIndexContent
python3 -m pytest tests/test_index_content.py::TestIndexContent::test_index_content_init
```

## Test Coverage

Current test coverage (as of initial implementation):

- **Overall**: 67%
- **navdex_core.py**: 63%
- **setutils.py**: 79%
- **termios_proxy.py**: 50%

### Coverage Areas

**Well-covered areas:**
- Index file parsing and management
- Directory path utilities
- IndexContent operations (add, delete, match patterns)
- AutoContent tag and description parsing
- IndexedSet operations
- Basic path manipulation functions

**Areas with lower coverage:**
- Interactive user interface code (prompt functions)
- Command-line argument parsing (main block)
- Error handling edge cases
- Terminal I/O operations
- Some recursive edge cases in index searching

## Notes on Testing Approach

1. **No Code Modifications**: These tests were written without modifying the existing navdex_core code, as per project requirements.

2. **Test Isolation**: Tests use pytest fixtures to create isolated temporary directories and mock environment variables.

3. **Edge Cases**: Some edge cases in the original code (like recursion when no index exists anywhere) were identified but not fixed, with tests documenting the actual behavior.

4. **Platform-Specific Code**: Tests handle both Unix (termios) and Windows (msvcrt) code paths where applicable.

5. **Interactive Features**: Tests for interactive features (user prompts, keyboard input) use mocking and test in non-interactive modes (calc mode, printonly mode) where possible.

## Future Improvements

When the code is restructured for better testability, consider:

- Breaking up large functions into smaller, testable units
- Adding dependency injection for file system operations
- Separating UI code from business logic
- Adding more comprehensive error handling
- Improving test coverage of edge cases and error paths
