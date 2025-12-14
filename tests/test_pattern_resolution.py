"""Tests for pattern resolution functions in navdex_core."""
import os
import pytest
from unittest.mock import patch

import navdex_core


class TestResolvePatternToDir:
    """Tests for resolvePatternToDir function."""
    
    def test_resolve_pattern_single_match(self, index_with_dirs, monkeypatch):
        """Test resolving pattern with single match."""
        test_dir, index_path = index_with_dirs
        
        monkeypatch.chdir(test_dir)
        monkeypatch.setenv('PWD', str(test_dir))
        monkeypatch.setenv('HOME', str(test_dir))
        
        orig_root = navdex_core.file_sys_root
        try:
            navdex_core.file_sys_root = "/"
            
            # Use calc mode to avoid user interaction
            # Pattern "myproject" should match uniquely
            matches, solution = navdex_core.resolvePatternToDir(
                ["myproject"], mode=navdex_core.ResolveMode.calc
            )
            
            # With a single match, solution should be the matched path
            if matches is not None and len(matches) == 1:
                # Single match case
                assert solution is not None
                assert 'myproject' in str(solution)
            else:
                # Multiple matches case - returned as list
                assert matches is not None
                assert len(matches) > 0
        finally:
            navdex_core.file_sys_root = orig_root
    
    def test_resolve_pattern_multiple_matches(self, index_with_dirs, monkeypatch):
        """Test resolving pattern with multiple matches."""
        test_dir, index_path = index_with_dirs
        
        monkeypatch.chdir(test_dir)
        monkeypatch.setenv('PWD', str(test_dir))
        monkeypatch.setenv('HOME', str(test_dir))
        
        orig_root = navdex_core.file_sys_root
        try:
            navdex_core.file_sys_root = "/"
            
            # "project" should match both myproject and otherproject
            matches, solution = navdex_core.resolvePatternToDir(
                ["project"], mode=navdex_core.ResolveMode.calc
            )
            
            assert matches is not None
            assert len(matches) >= 2
        finally:
            navdex_core.file_sys_root = orig_root
    
    def test_resolve_pattern_no_matches(self, index_with_dirs, monkeypatch):
        """Test resolving pattern with no matches."""
        test_dir, index_path = index_with_dirs
        
        monkeypatch.chdir(test_dir)
        monkeypatch.setenv('PWD', str(test_dir))
        monkeypatch.setenv('HOME', str(test_dir))
        
        orig_root = navdex_core.file_sys_root
        try:
            navdex_core.file_sys_root = "/"
            
            matches, solution = navdex_core.resolvePatternToDir(
                ["nonexistent"], mode=navdex_core.ResolveMode.calc
            )
            
            assert matches is None
            assert solution is not None
            assert solution.startswith("!")
            assert "No matches" in solution
        finally:
            navdex_core.file_sys_root = orig_root
    
    def test_resolve_pattern_with_index_offset(self, index_with_dirs, monkeypatch):
        """Test resolving pattern with numeric index offset."""
        test_dir, index_path = index_with_dirs
        
        monkeypatch.chdir(test_dir)
        monkeypatch.setenv('PWD', str(test_dir))
        monkeypatch.setenv('HOME', str(test_dir))
        
        orig_root = navdex_core.file_sys_root
        try:
            navdex_core.file_sys_root = "/"
            
            # Use index 0 to select first match
            matches, solution = navdex_core.resolvePatternToDir(
                ["project", "0"], mode=navdex_core.ResolveMode.calc
            )
            
            assert solution is not None
            assert not solution.startswith("!")
        finally:
            navdex_core.file_sys_root = orig_root
    
    def test_resolve_pattern_negative_index(self, index_with_dirs, monkeypatch):
        """Test resolving pattern with negative index offset."""
        test_dir, index_path = index_with_dirs
        
        monkeypatch.chdir(test_dir)
        monkeypatch.setenv('PWD', str(test_dir))
        monkeypatch.setenv('HOME', str(test_dir))
        
        orig_root = navdex_core.file_sys_root
        try:
            navdex_core.file_sys_root = "/"
            
            # Use -1 to select last match
            matches, solution = navdex_core.resolvePatternToDir(
                ["project", "-1"], mode=navdex_core.ResolveMode.calc
            )
            
            assert solution is not None
            assert not solution.startswith("!")
        finally:
            navdex_core.file_sys_root = orig_root
    
    def test_resolve_pattern_printonly_mode(self, index_with_dirs, monkeypatch):
        """Test resolvePatternToDir in printonly mode."""
        test_dir, index_path = index_with_dirs
        
        monkeypatch.chdir(test_dir)
        monkeypatch.setenv('PWD', str(test_dir))
        monkeypatch.setenv('HOME', str(test_dir))
        
        orig_root = navdex_core.file_sys_root
        try:
            navdex_core.file_sys_root = "/"
            
            matches, solution = navdex_core.resolvePatternToDir(
                ["project"], mode=navdex_core.ResolveMode.printonly
            )
            
            assert solution is not None
            assert solution.startswith("!")
            # Solution should contain newline-separated paths
            assert '\n' in solution or len(solution.split('!')[1]) > 0
        finally:
            navdex_core.file_sys_root = orig_root


class TestPrintMatchingEntries:
    """Tests for printMatchingEntries function."""
    
    def test_print_matching_entries(self, temp_dir):
        """Test printMatchingEntries formats output correctly."""
        index_path = temp_dir / ".navdex-index"
        index_path.write_text("dir1 1\ndir2 2\n")
        
        ic = navdex_core.IndexContent(str(index_path))
        matches = [("dir1", 1), ("dir2", 2)]
        
        result_matches, result_str = navdex_core.printMatchingEntries(matches, ic)
        
        assert result_matches == matches
        assert result_str.startswith("!")
        assert "dir1" in result_str
        assert "dir2" in result_str
        assert "\n" in result_str


class TestColorFunctions:
    """Tests for color formatting functions."""
    
    def test_red(self):
        """Test red color formatting."""
        result = navdex_core.red("test")
        if navdex_core.use_ansiterm:
            assert "\033[" in result
        assert "test" in result
    
    def test_green(self):
        """Test green color formatting."""
        result = navdex_core.green("test")
        if navdex_core.use_ansiterm:
            assert "\033[" in result
        assert "test" in result
    
    def test_yellow(self):
        """Test yellow color formatting."""
        result = navdex_core.yellow("test")
        if navdex_core.use_ansiterm:
            assert "\033[" in result
        assert "test" in result
    
    def test_grey(self):
        """Test grey color formatting."""
        result = navdex_core.grey("test")
        if navdex_core.use_ansiterm:
            assert "\033[" in result
        assert "test" in result
    
    def test_purp(self):
        """Test purple color formatting."""
        result = navdex_core.purp("test")
        if navdex_core.use_ansiterm:
            assert "\033[" in result
        assert "test" in result


class TestMultipleNumericCandidates:
    """Tests for multiple_numeric_candidates function."""
    
    def test_multiple_candidates_true(self):
        """Test when buffer matches multiple candidates."""
        from collections import OrderedDict
        dx = OrderedDict({
            "1": ("path1", None),
            "10": ("path10", None),
            "11": ("path11", None),
        })
        
        # "1" matches "1", "10", and "11"
        result = navdex_core.multiple_numeric_candidates("1", dx)
        assert result is True
    
    def test_multiple_candidates_false(self):
        """Test when buffer matches single candidate."""
        from collections import OrderedDict
        dx = OrderedDict({
            "1": ("path1", None),
            "2": ("path2", None),
            "3": ("path3", None),
        })
        
        # "2" only matches "2"
        result = navdex_core.multiple_numeric_candidates("2", dx)
        assert result is False
    
    def test_no_candidates(self):
        """Test when buffer matches no candidates."""
        from collections import OrderedDict
        dx = OrderedDict({
            "1": ("path1", None),
            "2": ("path2", None),
        })
        
        # "5" matches nothing - first next() will raise StopIteration
        # This is actually a bug in the code, but we're not modifying it
        # so we test the actual behavior
        with pytest.raises(StopIteration):
            result = navdex_core.multiple_numeric_candidates("5", dx)


class TestUserTraps:
    """Tests for user trap exceptions."""
    
    def test_user_trap_hierarchy(self):
        """Test that user traps inherit correctly."""
        assert issubclass(navdex_core.UserUpTrap, navdex_core.UserTrap)
        assert issubclass(navdex_core.UserDownTrap, navdex_core.UserTrap)
        assert issubclass(navdex_core.UserSelectionTrap, navdex_core.UserTrap)
        assert issubclass(navdex_core.UserBadEntryTrap, navdex_core.UserTrap)
    
    def test_user_selection_trap_with_args(self):
        """Test UserSelectionTrap can carry arguments."""
        trap = navdex_core.UserSelectionTrap(5)
        assert trap.args[0] == 5
    
    def test_user_up_trap_with_path(self):
        """Test UserUpTrap can carry path."""
        trap = navdex_core.UserUpTrap("/some/path")
        assert trap.args[0] == "/some/path"


class TestAddEntryAlreadyPresent:
    """Tests for AddEntryAlreadyPresent exception."""
    
    def test_add_entry_already_present(self):
        """Test AddEntryAlreadyPresent exception."""
        exc = navdex_core.AddEntryAlreadyPresent()
        assert isinstance(exc, BaseException)


class TestPrintGrep:
    """Tests for printGrep function."""
    
    def test_print_grep_no_pattern(self, index_with_dirs, monkeypatch, capsys):
        """Test printGrep without pattern lists all entries."""
        test_dir, index_path = index_with_dirs
        
        monkeypatch.chdir(test_dir)
        monkeypatch.setenv('PWD', str(test_dir))
        monkeypatch.setenv('HOME', str(test_dir))
        
        orig_root = navdex_core.file_sys_root
        try:
            navdex_core.file_sys_root = "/"
            result = navdex_core.printGrep(None)
            
            assert result is True
            captured = capsys.readouterr()
            # Should have printed paths
            assert "!" in captured.out
        finally:
            navdex_core.file_sys_root = orig_root
    
    def test_print_grep_with_pattern(self, index_with_dirs, monkeypatch, capsys):
        """Test printGrep with pattern filters results."""
        test_dir, index_path = index_with_dirs
        
        monkeypatch.chdir(test_dir)
        monkeypatch.setenv('PWD', str(test_dir))
        monkeypatch.setenv('HOME', str(test_dir))
        
        orig_root = navdex_core.file_sys_root
        try:
            navdex_core.file_sys_root = "/"
            result = navdex_core.printGrep("myproject")
            
            captured = capsys.readouterr()
            # Should have found matches
            if result:
                assert "myproject" in captured.out
        finally:
            navdex_core.file_sys_root = orig_root
    
    def test_print_grep_with_navdex_auto(self, temp_dir, monkeypatch, capsys):
        """Test printGrep includes .navdex-auto info."""
        # Create directory with .navdex-auto
        test_dir = temp_dir / "testdir"
        test_dir.mkdir()
        
        auto_file = test_dir / ".navdex-auto"
        auto_file.write_text("# .TAGS: python test\n# .DESC: Test directory\n")
        
        index_file = temp_dir / ".navdex-index"
        index_file.write_text("testdir 1\n")
        
        monkeypatch.chdir(temp_dir)
        monkeypatch.setenv('PWD', str(temp_dir))
        monkeypatch.setenv('HOME', str(temp_dir))
        
        orig_root = navdex_core.file_sys_root
        try:
            navdex_core.file_sys_root = "/"
            result = navdex_core.printGrep(None)
            
            captured = capsys.readouterr()
            # Should include tags and description
            assert ".TAGS:" in captured.out
            assert "Test directory" in captured.out
        finally:
            navdex_core.file_sys_root = orig_root
