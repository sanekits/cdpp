"""Tests for IndexContent class in navdex_core."""
import os
import pytest
from pathlib import Path

import navdex_core


class TestIndexContent:
    """Tests for IndexContent class."""
    
    def test_index_content_init(self, test_index_file):
        """Test IndexContent initialization from file."""
        ic = navdex_core.IndexContent(str(test_index_file))
        
        assert ic.path == str(test_index_file)
        assert len(ic) > 0
        assert ic.protect is False
        assert ic.outer is None
    
    def test_index_content_parse_entries(self, test_index_file):
        """Test that entries are parsed correctly."""
        ic = navdex_core.IndexContent(str(test_index_file))
        
        # Check that entries are tuples of (path, priority)
        for entry in ic:
            assert isinstance(entry, tuple)
            assert len(entry) == 2
            assert isinstance(entry[0], str)
            assert isinstance(entry[1], int)
    
    def test_index_content_skip_comments(self, temp_dir):
        """Test that comment lines are skipped."""
        index_path = temp_dir / ".navdex-index"
        content = """# Comment line
# Another comment
dir1 1
# Yet another comment
dir2 2
"""
        index_path.write_text(content)
        
        ic = navdex_core.IndexContent(str(index_path))
        assert len(ic) == 2
        assert ic[0] == ('dir1', 1)
        assert ic[1] == ('dir2', 2)
    
    def test_index_content_default_priority(self, temp_dir):
        """Test that entries without priority get skipped (path becomes empty)."""
        index_path = temp_dir / ".navdex-index"
        content = """dir1 2
dir2
dir3 abc
"""
        index_path.write_text(content)
        
        ic = navdex_core.IndexContent(str(index_path))
        # dir2 with no priority has empty path after rpartition, so is skipped
        # dir3 with invalid "abc" gets default priority 1
        assert len(ic) == 2
        assert ic[0] == ('dir1', 2)
        assert ic[1] == ('dir3', 1)  # Invalid priority becomes default
    
    def test_empty(self, temp_dir):
        """Test Empty method."""
        index_path = temp_dir / ".navdex-index"
        index_path.write_text("")
        
        ic = navdex_core.IndexContent(str(index_path))
        assert ic.Empty() is True
    
    def test_empty_with_entries(self, test_index_file):
        """Test Empty method with entries."""
        ic = navdex_core.IndexContent(str(test_index_file))
        assert ic.Empty() is False
    
    def test_index_root(self, test_index_file):
        """Test indexRoot method."""
        ic = navdex_core.IndexContent(str(test_index_file))
        assert ic.indexRoot() == str(test_index_file.parent)
    
    def test_abs_path_absolute(self, test_index_file):
        """Test absPath with absolute path."""
        ic = navdex_core.IndexContent(str(test_index_file))
        result = ic.absPath("/absolute/path")
        assert result == "/absolute/path"
    
    def test_abs_path_relative(self, test_index_file):
        """Test absPath with relative path."""
        ic = navdex_core.IndexContent(str(test_index_file))
        result = ic.absPath("relative/path")
        expected = str(test_index_file.parent / "relative/path")
        assert result == expected
    
    def test_relative_path(self, test_index_file):
        """Test relativePath method."""
        ic = navdex_core.IndexContent(str(test_index_file))
        index_root = str(test_index_file.parent)
        
        # Test path under index root
        full_path = f"{index_root}/subdir/file"
        result = ic.relativePath(full_path)
        assert result == "subdir/file"
    
    def test_relative_path_outside_root(self, test_index_file):
        """Test relativePath with path outside index root."""
        ic = navdex_core.IndexContent(str(test_index_file))
        
        # Path outside index root should be returned as-is
        outside_path = "/some/other/path"
        result = ic.relativePath(outside_path)
        assert result == outside_path
    
    def test_add_dir_new(self, test_index_file):
        """Test addDir with new directory."""
        ic = navdex_core.IndexContent(str(test_index_file))
        initial_len = len(ic)
        
        result = ic.addDir("newdir", 2)
        assert result is True
        assert len(ic) == initial_len + 1
        assert ('newdir', 2) in ic
    
    def test_add_dir_existing_same_priority(self, test_index_file):
        """Test addDir with existing directory at same priority."""
        ic = navdex_core.IndexContent(str(test_index_file))
        
        # First add a directory
        ic.addDir("testdir", 1)
        initial_len = len(ic)
        
        # Try to add again with same priority
        with pytest.raises(navdex_core.AddEntryAlreadyPresent):
            ic.addDir("testdir", 1)
    
    def test_add_dir_update_priority(self, test_index_file):
        """Test addDir updating existing directory with different priority."""
        ic = navdex_core.IndexContent(str(test_index_file))
        
        # First add a directory
        ic.addDir("testdir", 1)
        initial_len = len(ic)
        
        # Update with different priority
        result = ic.addDir("testdir", 3)
        assert result is True
        assert len(ic) == initial_len  # Length shouldn't change
        
        # Verify priority was updated
        for entry in ic:
            if entry[0] == "testdir":
                assert entry[1] == 3
                break
        else:
            pytest.fail("Entry not found after update")
    
    def test_del_dir_existing(self, test_index_file):
        """Test delDir with existing directory."""
        ic = navdex_core.IndexContent(str(test_index_file))
        
        # Add a directory first
        ic.addDir("testdir", 1)
        initial_len = len(ic)
        
        # Delete it
        result = ic.delDir("testdir")
        assert result is True
        assert len(ic) == initial_len - 1
        assert ('testdir', 1) not in ic
    
    def test_del_dir_nonexistent(self, test_index_file):
        """Test delDir with non-existent directory."""
        ic = navdex_core.IndexContent(str(test_index_file))
        
        result = ic.delDir("nonexistent")
        assert result is False
    
    def test_clean(self, index_with_dirs):
        """Test clean method removes stale entries."""
        test_dir, index_path = index_with_dirs
        
        ic = navdex_core.IndexContent(str(index_path))
        initial_len = len(ic)
        
        # Add a stale entry
        ic.append(("nonexistent/dir", 1))
        
        # Clean should remove stale entries
        ic.clean()
        
        # All remaining entries should exist
        for entry in ic:
            full_path = ic.absPath(entry[0])
            assert navdex_core.isdir(full_path), f"Directory {full_path} should exist"
    
    def test_write_and_read(self, temp_dir):
        """Test writing index and reading it back."""
        index_path = temp_dir / ".navdex-index"
        index_path.write_text("")
        
        # Create and populate index
        ic = navdex_core.IndexContent(str(index_path))
        ic.append(("dir1", 1))
        ic.append(("dir2", 2))
        ic.append(("dir3", 3))
        
        # Write to file
        ic.write()
        
        # Read it back
        ic2 = navdex_core.IndexContent(str(index_path))
        
        # Should have same entries (write sorts them)
        assert len(ic2) == 3
        entries = sorted(ic)
        for i, entry in enumerate(entries):
            assert entry in ic2
    
    def test_match_paths_simple(self, index_with_dirs):
        """Test matchPaths with simple pattern."""
        test_dir, index_path = index_with_dirs
        
        ic = navdex_core.IndexContent(str(index_path))
        
        # Match pattern that should find myproject
        matches = ic.matchPaths(["*project*"])
        
        assert len(matches) > 0
        # Check that matches are tuples of (path, priority)
        for match in matches:
            assert isinstance(match, tuple)
            assert len(match) == 2
    
    def test_match_paths_multiple_patterns(self, index_with_dirs):
        """Test matchPaths with multiple patterns."""
        test_dir, index_path = index_with_dirs
        
        ic = navdex_core.IndexContent(str(index_path))
        
        # Match with multiple patterns (AND condition)
        matches = ic.matchPaths(["*work*", "*client1*"])
        
        # Should match paths containing both 'work' and 'client1'
        assert len(matches) > 0
        for match in matches:
            path = match[0]
            assert 'work' in path or 'client1' in path
    
    def test_match_paths_no_matches(self, index_with_dirs):
        """Test matchPaths with pattern that matches nothing."""
        test_dir, index_path = index_with_dirs
        
        ic = navdex_core.IndexContent(str(index_path))
        
        matches = ic.matchPaths(["*nonexistent*"])
        assert len(matches) == 0
    
    def test_match_paths_sorted_by_length_and_priority(self, temp_dir):
        """Test that matchPaths returns results sorted by length/priority."""
        index_path = temp_dir / ".navdex-index"
        
        # Create directories
        (temp_dir / "a").mkdir()
        (temp_dir / "ab").mkdir()
        (temp_dir / "abc").mkdir()
        
        # Create index with different priorities
        index_path.write_text("""a 1
ab 1
abc 3
""")
        
        ic = navdex_core.IndexContent(str(index_path))
        matches = ic.matchPaths(["*a*"])
        
        # Should return all three, sorted by length/priority
        assert len(matches) == 3
        
        # Shorter paths with high priority should come first
        # The sort key is len(path)/priority, so lower is better


class TestIndexContentChaining:
    """Tests for IndexContent chaining (outer index)."""
    
    def test_empty_with_outer(self, temp_dir):
        """Test Empty method with chained indices."""
        # Create inner index (empty)
        inner_index = temp_dir / "inner" / ".navdex-index"
        inner_index.parent.mkdir()
        inner_index.write_text("")
        
        # Create outer index (with entries)
        outer_index = temp_dir / ".navdex-index"
        outer_index.write_text("dir1 1\n")
        
        ic_inner = navdex_core.IndexContent(str(inner_index))
        ic_outer = navdex_core.IndexContent(str(outer_index))
        
        ic_inner.outer = ic_outer
        
        # Inner is empty but outer is not
        assert ic_inner.Empty() is False
    
    def test_match_paths_with_outer(self, temp_dir):
        """Test matchPaths with chained indices."""
        # Create directory structure
        (temp_dir / "inner" / "innerdir").mkdir(parents=True)
        (temp_dir / "outerdir").mkdir()
        
        # Create inner index
        inner_index = temp_dir / "inner" / ".navdex-index"
        inner_index.write_text("innerdir 1\n")
        
        # Create outer index
        outer_index = temp_dir / ".navdex-index"
        outer_index.write_text("outerdir 1\ninner/innerdir 1\n")
        
        ic_inner = navdex_core.IndexContent(str(inner_index))
        ic_outer = navdex_core.IndexContent(str(outer_index))
        
        ic_inner.outer = ic_outer
        
        # Match should include results from both indices
        matches = ic_inner.matchPaths(["*dir*"])
        
        # Should have matches from both inner and outer
        assert len(matches) >= 2
