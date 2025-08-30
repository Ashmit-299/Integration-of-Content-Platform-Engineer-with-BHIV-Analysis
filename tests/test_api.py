# tests/test_api.py - API Integration Tests
import pytest
import tempfile
import json
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

import sys
sys.path.append('..')

from backend.server import app

class TestAPIEndpoints:
    """Test suite for FastAPI endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_script_file(self):
        """Create sample script file for upload testing"""
        content = "Sample lesson: Introduction to Python programming"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            return f.name
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "bhiv-gurukul-platform"
    
    def test_status_endpoint(self, client):
        """Test system status endpoint"""
        response = client.get("/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "platform" in data
        assert "bhiv_integration" in data
        assert "bucket_storage" in data
        assert "ai_logging" in data
        assert "endpoints" in data
        
        assert data["platform"] == "operational"
        assert data["bhiv_integration"] == "active"
    
    def test_bhiv_status_endpoint(self, client):
        """Test BHIV status endpoint"""
        response = client.get("/bhiv/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "bhiv_core" in data
        assert "bucket_files" in data
        assert "feedback_logs" in data
        assert "ai_client" in data
        
        assert data["bhiv_core"] == "operational"
        assert data["ai_client"] == "ready"
    
    @patch('bhiv_core.process_script_upload')
    def test_upload_endpoint_success(self, mock_process, client, sample_script_file):
        """Test successful file upload"""
        mock_process.return_value = {
            "id": "test123",
            "storyboard": "bucket/storyboards/test123.json",
            "video": "bucket/videos/test123.mp4"
        }
        
        with open(sample_script_file, 'rb') as f:
            response = client.post(
                "/upload",
                files={"file": ("test.txt", f, "text/plain")}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test123"
        assert "BHIV" in data["message"]
        
        # Verify BHIV core was called
        mock_process.assert_called_once()
    
    def test_upload_endpoint_invalid_file_type(self, client):
        """Test upload with invalid file type"""
        with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
            f.write(b"fake pdf content")
            f.seek(0)
            
            response = client.post(
                "/upload",
                files={"file": ("test.pdf", f, "application/pdf")}
            )
        
        assert response.status_code == 400
        assert "Only .txt or .md files accepted" in response.json()["detail"]
    
    @patch('bhiv_core.process_script_upload')
    def test_upload_endpoint_processing_error(self, mock_process, client, sample_script_file):
        """Test upload with processing error"""
        mock_process.side_effect = Exception("Processing failed")
        
        with open(sample_script_file, 'rb') as f:
            response = client.post(
                "/upload",
                files={"file": ("test.txt", f, "text/plain")}
            )
        
        assert response.status_code == 500
        assert "BHIV processing error" in response.json()["detail"]
    
    def test_stream_endpoint_video_not_found(self, client):
        """Test streaming non-existent video"""
        response = client.get("/stream/nonexistent_video")
        
        assert response.status_code == 404
        assert "Video not found" in response.json()["detail"]
    
    @patch('pathlib.Path.exists')
    def test_stream_endpoint_success(self, mock_exists, client):
        """Test successful video streaming"""
        # Mock that bucket video exists
        def exists_side_effect(self):
            return str(self).endswith("bucket/videos/test123.mp4")
        
        mock_exists.side_effect = exists_side_effect
        
        with patch('fastapi.responses.FileResponse') as mock_response:
            mock_response.return_value = Mock()
            
            response = client.get("/stream/test123")
            
            # FileResponse should be called
            mock_response.assert_called_once()
    
    @patch('bhiv_core.notify_on_rate')
    def test_rate_endpoint_success(self, mock_notify, client):
        """Test successful video rating"""
        mock_notify.return_value = {"analysis": "positive feedback"}
        
        response = client.post(
            "/rate/test123",
            data={"rating": 5, "comment": "Great video!"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Thanks for rating" in data["message"]
        assert "improvement_triggered" in data
        
        # Verify feedback processing was called
        mock_notify.assert_called_once_with("test123", 5, "Great video!")
    
    def test_rate_endpoint_invalid_rating(self, client):
        """Test rating with invalid rating value"""
        response = client.post(
            "/rate/test123",
            data={"rating": 6, "comment": "Invalid rating"}
        )
        
        assert response.status_code == 400
        assert "rating must be 1..5" in response.json()["detail"]
    
    @patch('bhiv_core.notify_on_rate')
    def test_rate_endpoint_processing_error(self, mock_notify, client):
        """Test rating with feedback processing error"""
        mock_notify.side_effect = Exception("Feedback processing failed")
        
        response = client.post(
            "/rate/test123",
            data={"rating": 3, "comment": "Average video"}
        )
        
        assert response.status_code == 200  # Should still return 200
        data = response.json()
        assert "Thanks for rating" in data["message"]
        assert "improvement_error" in data

@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for complete API workflows"""
    
    @pytest.fixture
    def client(self):
        """Create test client with temporary bucket"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('bhiv_bucket.BUCKET_ROOT', Path(temp_dir) / "test_bucket"):
                yield TestClient(app)
    
    def test_complete_workflow(self, client):
        """Test complete workflow: upload -> stream -> rate"""
        # This would test the entire pipeline
        # Currently mocked due to complexity of video generation
        pass
    
    def test_concurrent_uploads(self, client):
        """Test handling multiple concurrent uploads"""
        # Test concurrent request handling
        pass

@pytest.mark.performance
class TestAPIPerformance:
    """Performance tests for API endpoints"""
    
    def test_upload_performance(self):
        """Test upload endpoint performance under load"""
        # Performance testing would go here
        pass
    
    def test_concurrent_request_handling(self):
        """Test API handling concurrent requests"""
        # Concurrency testing would go here
        pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])