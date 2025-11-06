"""
Unit tests for color extraction utilities
"""
import unittest
from app.utils.color_extractor import ColorExtractor


class TestColorExtractor(unittest.TestCase):
    
    def setUp(self):
        """Create a ColorExtractor instance"""
        self.extractor = ColorExtractor(cache_duration=5)
    
    def test_calculate_saturation(self):
        """Test saturation calculation"""
        # Pure red - high saturation
        sat = ColorExtractor._calculate_saturation(255, 0, 0)
        self.assertEqual(sat, 1.0)
        
        # Gray - no saturation
        sat = ColorExtractor._calculate_saturation(128, 128, 128)
        self.assertEqual(sat, 0.0)
        
        # Mixed color
        sat = ColorExtractor._calculate_saturation(200, 100, 50)
        self.assertGreater(sat, 0)
        self.assertLess(sat, 1)
    
    def test_rgb_to_hex(self):
        """Test RGB to hex conversion"""
        # Black
        hex_color = ColorExtractor.rgb_to_hex(0, 0, 0)
        self.assertEqual(hex_color, '#000000')
        
        # White
        hex_color = ColorExtractor.rgb_to_hex(255, 255, 255)
        self.assertEqual(hex_color, '#FFFFFF')
        
        # Red
        hex_color = ColorExtractor.rgb_to_hex(255, 0, 0)
        self.assertEqual(hex_color, '#FF0000')
        
        # Custom color
        hex_color = ColorExtractor.rgb_to_hex(123, 45, 67)
        self.assertEqual(hex_color, '#7B2D43')
    
    def test_cache_functionality(self):
        """Test that cache works"""
        # Clear cache first
        self.extractor.clear_cache()
        
        # Cache should be empty
        self.assertEqual(len(self.extractor._cache), 0)
        
        # After clearing, cache should be empty again
        self.extractor.clear_cache()
        self.assertEqual(len(self.extractor._cache), 0)
    
    def test_color_validation(self):
        """Test that extracted colors are valid RGB values"""
        # Test with saturation calculation
        r, g, b = 255, 128, 64
        sat = ColorExtractor._calculate_saturation(r, g, b)
        
        # Saturation should be between 0 and 1
        self.assertGreaterEqual(sat, 0)
        self.assertLessEqual(sat, 1)


if __name__ == '__main__':
    unittest.main()
