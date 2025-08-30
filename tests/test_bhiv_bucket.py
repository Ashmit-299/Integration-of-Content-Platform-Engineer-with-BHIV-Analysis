# tests/test_bhiv_bucket.py - Unit Tests for BHIV Bucket
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, Mock

import sys
sys.path.append('..')

from bhiv_bucket import (
    init_bucket, save_script, save_storyboard, 
    save_video, read_storyboard, BUCKET_ROOT
)

class TestBHIVBucket:
    """Test suite for BHIV Bucket storage abstraction"""
    
    @pytest.fixture
    def temp_bucket(self):
        """Create temporary bucket for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('bhiv_bucket.BUCKET_ROOT', Path(temp_dir) / "test_bucket"):
                yield Path(temp_dir) / "test_bucket"
    
    @pytest.fixture
    def sample_script_file(self):
        """Create sample script file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a sample lesson script for testing.")
            return f.name
    
    @pytest.fixture
    def sample_video_file(self):
        """Create sample video file"""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            f.write(b"fake video content")
            return f.name
    
    def test_init_bucket_creates_directories(self, temp_bucket):
        """Test bucket initialization creates all required directories"""
        init_bucket()
        
        expected_dirs = ["scripts", "storyboards", "videos", "logs", "ratings", "tmp"]
        
        for dir_name in expected_dirs:
            assert (temp_bucket / dir_name).exists()
            assert (temp_bucket / dir_name).is_dir()
    
    def test_save_script_success(self, temp_bucket, sample_script_file):
        """Test successful script saving"""
        result = save_script(sample_script_file, "test_script.txt")
        
        expected_path = temp_bucket / "scripts" / "test_script.txt"
        assert result == str(expected_path)
        assert expected_path.exists()
        
        # Verify content
        content = expected_path.read_text()
        assert "sample lesson script" in content
    
    def test_save_script_auto_name(self, temp_bucket, sample_script_file):
        """Test script saving with automatic naming"""
        result = save_script(sample_script_file)
        
        # Should use original filename
        original_name = Path(sample_script_file).name
        expected_path = temp_bucket / "scripts" / original_name
        
        assert result == str(expected_path)
        assert expected_path.exists()
    
    def test_save_storyboard_success(self, temp_bucket):
        """Test successful storyboard saving"""
        storyboard_data = {
            "title": "Test Lesson",
            "scenes": [
                {"scene_id": 1, "text": "Introduction", "duration_secs": 5},
                {"scene_id": 2, "text": "Main content", "duration_secs": 10}
            ]
        }
        
        result = save_storyboard(storyboard_data, "test_storyboard.json")
        
        expected_path = temp_bucket / "storyboards" / "test_storyboard.json"
        assert result == str(expected_path)
        assert expected_path.exists()
        
        # Verify content
        saved_data = json.loads(expected_path.read_text(encoding="utf-8"))
        assert saved_data["title"] == "Test Lesson"
        assert len(saved_data["scenes"]) == 2
    
    def test_save_video_success(self, temp_bucket, sample_video_file):
        """Test successful video saving"""
        result = save_video(sample_video_file, "test_video.mp4")
        
        expected_path = temp_bucket / "videos" / "test_video.mp4"
        assert result == str(expected_path)
        assert expected_path.exists()
        
        # Verify content
        assert expected_path.read_bytes() == b"fake video content"
    
    def test_save_video_auto_name(self, temp_bucket, sample_video_file):
        """Test video saving with automatic naming"""
        result = save_video(sample_video_file)
        
        original_name = Path(sample_video_file).name
        expected_path = temp_bucket / "videos" / original_name
        
        assert result == str(expected_path)
        assert expected_path.exists()
    
    def test_read_storyboard_success(self, temp_bucket):
        """Test successful storyboard reading"""
        # First save a storyboard
        storyboard_data = {
            "title": "Test Reading",
            "scenes": [{"scene_id": 1, "text": "Test scene"}]
        }
        
        storyboard_path = save_storyboard(storyboard_data, "read_test.json")
        
        # Now read it back
        read_data = read_storyboard(storyboard_path)
        
        assert read_data["title"] == "Test Reading"
        assert len(read_data["scenes"]) == 1
        assert read_data["scenes"][0]["text"] == "Test scene"
    
    def test_read_storyboard_file_not_found(self):
        """Test reading non-existent storyboard file"""
        with pytest.raises(FileNotFoundError):
            read_storyboard("nonexistent_file.json")
    
    def test_save_script_file_not_found(self, temp_bucket):
        """Test saving non-existent script file"""
        with pytest.raises(FileNotFoundError):
            save_script("nonexistent_script.txt", "output.txt")
    
    def test_bucket_operations_create_directories(self, temp_bucket):
        """Test that bucket operations create directories if they don't exist"""
        # Remove a directory
        scripts_dir = temp_bucket / "scripts"
        if scripts_dir.exists():
            scripts_dir.rmdir()
        
        # Create a temporary script file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test content")
            temp_script = f.name
        
        # Save script should recreate the directory
        save_script(temp_script, "test.txt")
        
        assert scripts_dir.exists()
        assert (scripts_dir / "test.txt").exists()
    
    def test_storyboard_unicode_handling(self, temp_bucket):
        """Test storyboard saving/reading with unicode content"""
        storyboard_data = {
            "title": "Test with émojis 🎬",
            "scenes": [
                {"text": "Content with unicode: café, naïve, résumé"}
            ]
        }
        
        # Save and read back
        path = save_storyboard(storyboard_data, "unicode_test.json")
        read_data = read_storyboard(path)
        
        assert read_data["title"] == "Test with émojis 🎬"
        assert "café" in read_data["scenes"][0]["text"]
    
    def test_bucket_root_environment_variable(self):
        """Test that BUCKET_ROOT respects environment variable"""
        with patch.dict('os.environ', {'BHIV_BUCKET_PATH': '/custom/bucket/path'}):
            # Re-import to get updated BUCKET_ROOT
            import importlib
            import bhiv_bucket
            importlib.reload(bhiv_bucket)
            
            assert str(bhiv_bucket.BUCKET_ROOT) == '/custom/bucket/path'

@pytest.mark.integration
class TestBHIVBucketIntegration:
    """Integration tests for BHIV Bucket with real file system"""
    
    def test_full_workflow(self):
        """Test complete workflow: script -> storyboard -> video"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('bhiv_bucket.BUCKET_ROOT', Path(temp_dir) / "integration_bucket"):
                # Initialize bucket
                init_bucket()
                
                # Create test script
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    f.write("Integration test script content")
                    script_file = f.name
                
                # Save script
                script_path = save_script(script_file, "integration_script.txt")
                assert Path(script_path).exists()
                
                # Create and save storyboard
                storyboard = {
                    "title": "Integration Test",
                    "scenes": [{"scene_id": 1, "text": "Test scene"}]
                }
                storyboard_path = save_storyboard(storyboard, "integration_storyboard.json")
                assert Path(storyboard_path).exists()
                
                # Verify we can read it back
                read_storyboard_data = read_storyboard(storyboard_path)
                assert read_storyboard_data["title"] == "Integration Test"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])