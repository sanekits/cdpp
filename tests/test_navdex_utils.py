"""Tests for utility functions in navdex_core."""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Import the module under test
import navdex_core


class TestNormalizePath:
    """Tests for normalize_path function."""
    
    def test_normalize_path_unix(self):
        """Test that on Unix systems, paths are returned unchanged."""
        # Since we're testing on a Unix system, winpaths should be False
        if not navdex_core.winpaths:
            assert navdex_core.normalize_path('/usr/bin') == '/usr/bin'
            assert navdex_core.normalize_path('/home/user/docs') == '/home/user/docs'
    
    def test_normalize_path_with_spaces(self):
        """Test that paths with spaces are handled correctly."""
        if not navdex_core.winpaths:
            assert navdex_core.normalize_path('/home/user/my docs') == '/home/user/my docs'


class TestAbbreviatePath:
    """Tests for abbreviate_path function."""
    
    def test_abbreviate_home_path(self, mock_home):
        """Test abbreviation of paths under HOME."""
        # Set the home_path in navdex_core
        original_home = navdex_core.home_path
        navdex_core.home_path = str(mock_home)
        
        try:
            result = navdex_core.abbreviate_path(f"{mock_home}/documents", "/tmp")
            assert result == "~/documents"
        finally:
            navdex_core.home_path = original_home
    
    def test_abbreviate_index_relative(self):
        """Test abbreviation of paths relative to index path."""
        ix_path = "/home/user/projects"
        dest_path = "/home/user/projects/myproject"
        result = navdex_core.abbreviate_path(dest_path, ix_path)
        assert result == "myproject"
    
    def test_abbreviate_absolute_path(self):
        """Test that absolute paths outside home/index are kept absolute."""
        result = navdex_core.abbreviate_path("/usr/local/bin", "/home/user")
        assert result == "/usr/local/bin"
    
    def test_abbreviate_relative_path(self, mock_home, monkeypatch):
        """Test abbreviation of relative paths."""
        monkeypatch.setenv('PWD', str(mock_home))
        original_home = navdex_core.home_path
        navdex_core.home_path = str(mock_home)
        
        try:
            result = navdex_core.abbreviate_path("documents", "/tmp")
            assert result == "~/documents"
        finally:
            navdex_core.home_path = original_home


class TestDirContains:
    """Tests for dirContains function."""
    
    def test_dir_contains_true(self, test_dir_structure):
        """Test that parent directory contains child."""
        parent = str(test_dir_structure)
        child = str(test_dir_structure / "projects" / "myproject")
        assert navdex_core.dirContains(parent, child) is True
    
    def test_dir_contains_false(self, test_dir_structure):
        """Test that unrelated directories return False."""
        dir1 = str(test_dir_structure / "projects")
        dir2 = str(test_dir_structure / "work")
        assert navdex_core.dirContains(dir1, dir2) is False
    
    def test_dir_contains_same_dir(self, test_dir_structure):
        """Test that a directory contains itself (by realpath check)."""
        d = str(test_dir_structure)
        # dirContains checks if realpath(unk).startswith(realpath(parent))
        # Same dir will have unk start with parent, so it returns True
        assert navdex_core.dirContains(d, d) is True


class TestIsChildDir:
    """Tests for isChildDir function."""
    
    def test_is_child_dir_true(self):
        """Test positive case for child directory."""
        parent = "/home/user"
        child = "/home/user/documents"
        assert navdex_core.isChildDir(parent, child) is True
    
    def test_is_child_dir_false_sibling(self):
        """Test that sibling directories return False."""
        parent = "/home/user/docs"
        sibling = "/home/user/pics"
        assert navdex_core.isChildDir(parent, sibling) is False
    
    def test_is_child_dir_false_parent(self):
        """Test that parent of candidate returns False."""
        parent = "/home/user/docs"
        ancestor = "/home/user"
        assert navdex_core.isChildDir(parent, ancestor) is False
    
    def test_is_child_dir_same(self):
        """Test that same directory returns False."""
        d = "/home/user"
        assert navdex_core.isChildDir(d, d) is False


class TestOwnerCheck:
    """Tests for ownerCheck function."""
    
    def test_owner_check_only_mine_false(self, temp_dir):
        """Test that ownerCheck returns True when only_mine is False."""
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")
        
        result = navdex_core.ownerCheck(str(temp_dir), "test.txt", only_mine=False)
        assert result is True
    
    def test_owner_check_only_mine_true(self, temp_dir, monkeypatch):
        """Test ownerCheck when only_mine is True."""
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")
        
        # Set USER environment variable
        monkeypatch.setenv('USER', os.environ.get('USER', 'testuser'))
        
        # This should return True since we own the file we just created
        result = navdex_core.ownerCheck(str(temp_dir), "test.txt", only_mine=True)
        assert result is True


class TestIsFileInDir:
    """Tests for isFileInDir function."""
    
    def test_is_file_in_dir_true(self, temp_dir):
        """Test that existing file in directory returns True."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")
        
        result = navdex_core.isFileInDir(str(temp_dir), "test.txt")
        assert result is True
    
    def test_is_file_in_dir_false(self, temp_dir):
        """Test that non-existing file returns False."""
        result = navdex_core.isFileInDir(str(temp_dir), "nonexistent.txt")
        assert result is False
    
    def test_is_file_in_dir_subdir(self, temp_dir):
        """Test detection of subdirectory."""
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        
        result = navdex_core.isFileInDir(str(temp_dir), "subdir")
        assert result is True


class TestSetFileSysRoot:
    """Tests for set_file_sys_root function."""
    
    def test_set_file_sys_root(self):
        """Test that set_file_sys_root returns previous value and sets new value."""
        original = navdex_core.file_sys_root
        try:
            prev = navdex_core.set_file_sys_root("/new/root")
            assert prev == original
            assert navdex_core.file_sys_root == "/new/root"
        finally:
            navdex_core.file_sys_root = original


class TestPathWrappers:
    """Tests for wrapper functions around os.path functions."""
    
    def test_isdir(self, test_dir_structure):
        """Test isdir wrapper."""
        assert navdex_core.isdir(str(test_dir_structure)) is True
        assert navdex_core.isdir(str(test_dir_structure / "nonexistent")) is False
    
    def test_exists(self, test_dir_structure):
        """Test exists wrapper."""
        assert navdex_core.exists(str(test_dir_structure)) is True
        assert navdex_core.exists(str(test_dir_structure / "nonexistent")) is False
    
    def test_dirname(self):
        """Test dirname wrapper."""
        result = navdex_core.dirname("/home/user/docs/file.txt")
        assert result == "/home/user/docs"
    
    def test_isfile(self, temp_dir):
        """Test isfile wrapper."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")
        
        assert navdex_core.isfile(str(test_file)) is True
        assert navdex_core.isfile(str(temp_dir)) is False
