"""Pytest configuration and shared fixtures for navdex tests."""
import os
import sys
import tempfile
import shutil
import pytest
from pathlib import Path

# Add bin directory to path so we can import navdex_core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'bin'))


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def mock_home(temp_dir, monkeypatch):
    """Create a mock HOME directory."""
    home = temp_dir / "home"
    home.mkdir()
    monkeypatch.setenv('HOME', str(home))
    return home


@pytest.fixture
def test_index_file(temp_dir):
    """Create a test index file with sample entries."""
    index_path = temp_dir / ".navdex-index"
    content = """# Test index
dir1 1
dir2/subdir 2
dir3 1
projects/myproject 3
"""
    index_path.write_text(content)
    return index_path


@pytest.fixture
def test_dir_structure(temp_dir):
    """Create a test directory structure with multiple levels."""
    # Create directory structure
    dirs = [
        "projects/myproject",
        "projects/otherproject",
        "work/client1/site1",
        "work/client1/site2",
        "work/client2",
        "personal/docs",
        "personal/photos",
    ]
    
    for d in dirs:
        (temp_dir / d).mkdir(parents=True, exist_ok=True)
    
    return temp_dir


@pytest.fixture
def index_with_dirs(test_dir_structure):
    """Create an index file with actual existing directories."""
    index_path = test_dir_structure / ".navdex-index"
    content = """# Test index with real dirs
projects/myproject 3
projects/otherproject 1
work/client1/site1 2
work/client1/site2 1
work/client2 1
personal/docs 1
personal/photos 1
"""
    index_path.write_text(content)
    return test_dir_structure, index_path
