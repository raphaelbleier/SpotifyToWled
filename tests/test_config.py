"""
Unit tests for configuration management
"""
import unittest
import tempfile
import os
from app.core.config import Config


class TestConfig(unittest.TestCase):
    
    def setUp(self):
        """Create a temporary config file for testing"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.config = Config(config_path=self.temp_file.name)
    
    def tearDown(self):
        """Clean up temporary files"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_default_config(self):
        """Test that default configuration is loaded"""
        self.assertIsNotNone(self.config.data)
        self.assertIn('SPOTIFY_CLIENT_ID', self.config.data)
        self.assertIn('WLED_IPS', self.config.data)
        self.assertIn('REFRESH_INTERVAL', self.config.data)
    
    def test_save_and_load(self):
        """Test saving and loading configuration"""
        test_data = {
            'SPOTIFY_CLIENT_ID': 'test_id',
            'SPOTIFY_CLIENT_SECRET': 'test_secret',
            'WLED_IPS': ['192.168.1.100'],
            'REFRESH_INTERVAL': 30
        }
        
        self.config.update(test_data)
        self.config.save()
        
        # Create a new config instance to test loading
        new_config = Config(config_path=self.temp_file.name)
        
        self.assertEqual(new_config.get('SPOTIFY_CLIENT_ID'), 'test_id')
        self.assertEqual(new_config.get('SPOTIFY_CLIENT_SECRET'), 'test_secret')
        self.assertEqual(new_config.get('WLED_IPS'), ['192.168.1.100'])
    
    def test_validation_success(self):
        """Test successful validation"""
        self.config.set('SPOTIFY_CLIENT_ID', 'test_id')
        self.config.set('SPOTIFY_CLIENT_SECRET', 'test_secret')
        self.config.set('WLED_IPS', ['192.168.1.100'])
        self.config.set('REFRESH_INTERVAL', 30)
        
        is_valid, errors = self.config.validate()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validation_missing_credentials(self):
        """Test validation with missing Spotify credentials"""
        self.config.set('SPOTIFY_CLIENT_ID', '')
        self.config.set('SPOTIFY_CLIENT_SECRET', '')
        self.config.set('WLED_IPS', ['192.168.1.100'])
        
        is_valid, errors = self.config.validate()
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_validation_missing_wled(self):
        """Test validation with no WLED devices"""
        self.config.set('SPOTIFY_CLIENT_ID', 'test_id')
        self.config.set('SPOTIFY_CLIENT_SECRET', 'test_secret')
        self.config.set('WLED_IPS', [])
        
        is_valid, errors = self.config.validate()
        self.assertFalse(is_valid)
        self.assertTrue(any('WLED' in err for err in errors))
    
    def test_get_set_methods(self):
        """Test get and set methods"""
        self.config.set('TEST_KEY', 'test_value')
        self.assertEqual(self.config.get('TEST_KEY'), 'test_value')
        self.assertIsNone(self.config.get('NONEXISTENT_KEY'))
        self.assertEqual(self.config.get('NONEXISTENT_KEY', 'default'), 'default')


if __name__ == '__main__':
    unittest.main()
