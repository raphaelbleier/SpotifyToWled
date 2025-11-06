"""
Unit tests for WLED controller
"""
import unittest
from unittest.mock import Mock, patch
from app.utils.wled_controller import WLEDController


class TestWLEDController(unittest.TestCase):
    
    def setUp(self):
        """Create a WLEDController instance"""
        self.controller = WLEDController(max_retries=2, retry_delay=0)
    
    def test_initialization(self):
        """Test controller initialization"""
        self.assertEqual(self.controller.max_retries, 2)
        self.assertEqual(self.controller.retry_delay, 0)
        self.assertIsInstance(self.controller._device_status, dict)
    
    @patch('app.utils.wled_controller.requests.post')
    def test_set_color_success(self, mock_post):
        """Test successful color setting"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.controller.set_color('192.168.1.100', 255, 128, 64)
        
        self.assertTrue(result)
        self.assertEqual(mock_post.call_count, 1)
    
    @patch('app.utils.wled_controller.requests.post')
    def test_set_color_failure(self, mock_post):
        """Test color setting with failure"""
        mock_post.side_effect = Exception("Connection error")
        
        result = self.controller.set_color('192.168.1.100', 255, 128, 64)
        
        self.assertFalse(result)
        # Should retry max_retries times
        self.assertEqual(mock_post.call_count, 2)
    
    @patch('app.utils.wled_controller.requests.post')
    def test_set_color_all(self, mock_post):
        """Test setting color on multiple devices"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        ips = ['192.168.1.100', '192.168.1.101']
        results = self.controller.set_color_all(ips, 255, 0, 0)
        
        self.assertEqual(len(results), 2)
        self.assertTrue(all(results.values()))
    
    @patch('app.utils.wled_controller.requests.get')
    def test_health_check_online(self, mock_get):
        """Test health check for online device"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.controller.health_check('192.168.1.100')
        
        self.assertTrue(result)
    
    @patch('app.utils.wled_controller.requests.get')
    def test_health_check_offline(self, mock_get):
        """Test health check for offline device"""
        mock_get.side_effect = Exception("Connection error")
        
        result = self.controller.health_check('192.168.1.100')
        
        self.assertFalse(result)
    
    def test_device_status_tracking(self):
        """Test device status is tracked"""
        ip = '192.168.1.100'
        
        # Initially unknown
        status = self.controller.get_device_status(ip)
        self.assertEqual(status['status'], 'unknown')


if __name__ == '__main__':
    unittest.main()
