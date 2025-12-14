"""Tests for AutoContent class in navdex_core."""
import pytest

import navdex_core


class TestAutoContent:
    """Tests for AutoContent class."""
    
    def test_auto_content_init_with_file(self, temp_dir):
        """Test AutoContent initialization with file."""
        auto_file = temp_dir / ".navdex-auto"
        content = """# This is a navdex-auto file
# .TAGS: python testing automation
# .DESC: Test project for automated testing
"""
        auto_file.write_text(content)
        
        ac = navdex_core.AutoContent(str(auto_file))
        assert ac.path == str(auto_file)
        assert len(ac) > 0
    
    def test_auto_content_init_no_file(self):
        """Test AutoContent initialization with None path."""
        ac = navdex_core.AutoContent(None)
        assert ac.path is None
        assert len(ac) == 0
    
    def test_tags_parsing(self, temp_dir):
        """Test tags() method parses tags correctly."""
        auto_file = temp_dir / ".navdex-auto"
        content = """# Some comment
# .TAGS: python testing automation ci-cd
# Another line
"""
        auto_file.write_text(content)
        
        ac = navdex_core.AutoContent(str(auto_file))
        tags = ac.tags()
        
        assert isinstance(tags, list)
        assert len(tags) == 4
        assert "python" in tags
        assert "testing" in tags
        assert "automation" in tags
        assert "ci-cd" in tags
    
    def test_tags_empty(self, temp_dir):
        """Test tags() with no .TAGS line."""
        auto_file = temp_dir / ".navdex-auto"
        content = """# Some comment
# Another line
"""
        auto_file.write_text(content)
        
        ac = navdex_core.AutoContent(str(auto_file))
        tags = ac.tags()
        
        assert isinstance(tags, list)
        assert len(tags) == 0
    
    def test_desc_parsing(self, temp_dir):
        """Test desc() method parses description correctly."""
        auto_file = temp_dir / ".navdex-auto"
        content = """# Some comment
# .DESC: This is a test project for automation
# Another line
"""
        auto_file.write_text(content)
        
        ac = navdex_core.AutoContent(str(auto_file))
        desc = ac.desc()
        
        assert isinstance(desc, str)
        # desc() preserves the space after the colon
        assert desc == " This is a test project for automation"
    
    def test_desc_with_trailing_whitespace(self, temp_dir):
        """Test desc() strips trailing whitespace."""
        auto_file = temp_dir / ".navdex-auto"
        content = """# .DESC: This is a description with trailing space   
"""
        auto_file.write_text(content)
        
        ac = navdex_core.AutoContent(str(auto_file))
        desc = ac.desc()
        
        # desc() preserves the space after colon but strips trailing space
        assert desc == " This is a description with trailing space"
        assert not desc.endswith("  ")  # Multiple trailing spaces should be stripped
    
    def test_desc_empty(self, temp_dir):
        """Test desc() with no .DESC line."""
        auto_file = temp_dir / ".navdex-auto"
        content = """# Some comment
# Another line
"""
        auto_file.write_text(content)
        
        ac = navdex_core.AutoContent(str(auto_file))
        desc = ac.desc()
        
        assert isinstance(desc, str)
        assert desc == ""
    
    def test_tags_and_desc_together(self, temp_dir):
        """Test parsing both .TAGS and .DESC."""
        auto_file = temp_dir / ".navdex-auto"
        content = """# Project auto file
# .TAGS: web backend api
# .DESC: Backend API service for web application
# Other comments
"""
        auto_file.write_text(content)
        
        ac = navdex_core.AutoContent(str(auto_file))
        
        tags = ac.tags()
        assert len(tags) == 3
        assert "web" in tags
        assert "backend" in tags
        assert "api" in tags
        
        desc = ac.desc()
        # desc() preserves the space after the colon
        assert desc == " Backend API service for web application"
    
    def test_tags_multiple_spaces(self, temp_dir):
        """Test tags parsing with multiple spaces between tags."""
        auto_file = temp_dir / ".navdex-auto"
        content = """# .TAGS: tag1   tag2    tag3
"""
        auto_file.write_text(content)
        
        ac = navdex_core.AutoContent(str(auto_file))
        tags = ac.tags()
        
        # split() should handle multiple spaces
        assert len(tags) == 3
        assert "tag1" in tags
        assert "tag2" in tags
        assert "tag3" in tags
    
    def test_multiple_tags_lines(self, temp_dir):
        """Test that only first .TAGS line is parsed."""
        auto_file = temp_dir / ".navdex-auto"
        content = """# .TAGS: first second
# .TAGS: third fourth
"""
        auto_file.write_text(content)
        
        ac = navdex_core.AutoContent(str(auto_file))
        tags = ac.tags()
        
        # Should only parse first .TAGS line
        assert len(tags) == 2
        assert "first" in tags
        assert "second" in tags
        assert "third" not in tags
    
    def test_multiple_desc_lines(self, temp_dir):
        """Test that only first .DESC line is parsed."""
        auto_file = temp_dir / ".navdex-auto"
        content = """# .DESC: First description
# .DESC: Second description
"""
        auto_file.write_text(content)
        
        ac = navdex_core.AutoContent(str(auto_file))
        desc = ac.desc()
        
        # Should only parse first .DESC line (with leading space preserved)
        assert desc == " First description"
