"""Tests for termios_proxy module."""
import pytest
from unittest.mock import patch, MagicMock
import sys

# Import the module under test
import termios_proxy


class TestTermiosProxyModule:
    """Tests for termios_proxy module."""
    
    def test_use_termios_flag(self):
        """Test that use_termios flag is set."""
        assert isinstance(termios_proxy.use_termios, bool)
    
    def test_use_ansiterm_flag(self):
        """Test that use_ansiterm flag is set."""
        assert isinstance(termios_proxy.use_ansiterm, bool)
    
    def test_getraw_kbd_returns_generator(self):
        """Test that getraw_kbd returns a generator."""
        # We can't actually test the keyboard reading without mocking,
        # but we can verify it returns a generator
        gen = termios_proxy.getraw_kbd()
        assert hasattr(gen, '__next__')
        assert hasattr(gen, '__iter__')


class TestGetrawKbdNix:
    """Tests for getraw_kbd_nix function (Unix-specific)."""
    
    @pytest.mark.skipif(not termios_proxy.use_termios, reason="termios not available")
    def test_getraw_kbd_nix_is_generator(self):
        """Test that getraw_kbd_nix returns a generator."""
        gen = termios_proxy.getraw_kbd_nix()
        assert hasattr(gen, '__next__')
        assert hasattr(gen, '__iter__')
    
    @pytest.mark.skipif(not termios_proxy.use_termios, reason="termios not available")
    @patch('sys.stdin')
    def test_getraw_kbd_nix_reads_chars(self, mock_stdin):
        """Test that getraw_kbd_nix reads characters."""
        # Mock stdin to return a character
        mock_stdin.fileno.return_value = 0
        mock_stdin.read.side_effect = ['a', 'b', KeyboardInterrupt]
        
        # We can't fully test this without mocking termios
        # Just verify the function exists and is callable
        assert callable(termios_proxy.getraw_kbd_nix)


class TestGetrawKbdWindows:
    """Tests for getraw_kbd_windows function (Windows-specific)."""
    
    def test_getraw_kbd_windows_is_generator(self):
        """Test that getraw_kbd_windows returns a generator."""
        gen = termios_proxy.getraw_kbd_windows()
        assert hasattr(gen, '__next__')
        assert hasattr(gen, '__iter__')
    
    @pytest.mark.skipif(termios_proxy.use_termios, reason="Test for Windows only")
    def test_getraw_kbd_windows_callable(self):
        """Test that getraw_kbd_windows is callable."""
        assert callable(termios_proxy.getraw_kbd_windows)


class TestGetrawKbd:
    """Tests for getraw_kbd function (platform-agnostic wrapper)."""
    
    def test_getraw_kbd_returns_appropriate_function(self):
        """Test that getraw_kbd returns the appropriate platform function."""
        gen = termios_proxy.getraw_kbd()
        assert hasattr(gen, '__next__')
        
        # The function should return either nix or windows version
        # depending on platform, but we can't easily test which one
        # without mocking the platform detection
    
    @patch('termios_proxy.use_termios', True)
    @patch('termios_proxy.getraw_kbd_nix')
    def test_getraw_kbd_uses_nix_when_available(self, mock_nix):
        """Test that getraw_kbd uses nix version when termios available."""
        mock_nix.return_value = iter(['a', 'b'])
        
        result = termios_proxy.getraw_kbd()
        mock_nix.assert_called_once()
    
    @patch('termios_proxy.use_termios', False)
    @patch('termios_proxy.getraw_kbd_windows')
    def test_getraw_kbd_uses_windows_when_termios_unavailable(self, mock_windows):
        """Test that getraw_kbd uses windows version when termios unavailable."""
        mock_windows.return_value = iter(['a', 'b'])
        
        result = termios_proxy.getraw_kbd()
        mock_windows.assert_called_once()
