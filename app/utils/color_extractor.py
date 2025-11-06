"""
Color extraction utilities with caching
"""
import requests
import logging
from io import BytesIO
from colorthief import ColorThief
from typing import Tuple
from functools import lru_cache
from time import time

logger = logging.getLogger(__name__)


class ColorExtractor:
    """Extract colors from album covers with caching"""
    
    def __init__(self, cache_duration: int = 5):
        self.cache_duration = cache_duration
        self._cache = {}
    
    def _is_cache_valid(self, url: str) -> bool:
        """Check if cached color is still valid"""
        if url not in self._cache:
            return False
        cached_time = self._cache[url]['time']
        return (time() - cached_time) < self.cache_duration
    
    def get_color(self, image_url: str, method: str = 'vibrant') -> Tuple[int, int, int]:
        """
        Extract color from album cover image
        
        Args:
            image_url: URL of the album cover
            method: Extraction method ('vibrant', 'dominant', 'average')
        
        Returns:
            RGB tuple (r, g, b)
        """
        # Check cache first
        if self._is_cache_valid(image_url):
            logger.debug(f"Using cached color for {image_url}")
            return self._cache[image_url]['color']
        
        try:
            # Download image
            response = requests.get(image_url, timeout=5)
            response.raise_for_status()
            
            # Extract color
            if method == 'vibrant':
                color = self._get_vibrant_color(response.content)
            elif method == 'dominant':
                color = self._get_dominant_color(response.content)
            elif method == 'average':
                color = self._get_average_color(response.content)
            else:
                color = self._get_vibrant_color(response.content)
            
            # Cache the result
            self._cache[image_url] = {
                'color': color,
                'time': time()
            }
            
            logger.info(f"Extracted color: RGB{color} using method '{method}'")
            return color
            
        except requests.RequestException as e:
            logger.error(f"Failed to download image: {e}")
            return (0, 0, 0)
        except Exception as e:
            logger.error(f"Error extracting color: {e}")
            return (0, 0, 0)
    
    def _get_vibrant_color(self, image_bytes: bytes) -> Tuple[int, int, int]:
        """
        Get the most vibrant (saturated) color from palette
        Similar to spicetify-dynamic-theme
        """
        img_bytes = BytesIO(image_bytes)
        color_thief = ColorThief(img_bytes)
        
        # Get palette
        palette = color_thief.get_palette(color_count=6, quality=1)
        
        if not palette:
            return color_thief.get_color(quality=1)
        
        # Find most saturated color
        best_color = None
        best_saturation = -1
        
        for rgb in palette:
            saturation = self._calculate_saturation(*rgb)
            # Avoid very dark or very light colors
            brightness = sum(rgb) / 3
            if brightness < 30 or brightness > 225:
                continue
            
            if saturation > best_saturation:
                best_saturation = saturation
                best_color = rgb
        
        # Fallback to dominant if no good color found
        if best_color is None:
            best_color = color_thief.get_color(quality=1)
        
        return best_color
    
    def _get_dominant_color(self, image_bytes: bytes) -> Tuple[int, int, int]:
        """Get the dominant color from image"""
        img_bytes = BytesIO(image_bytes)
        color_thief = ColorThief(img_bytes)
        return color_thief.get_color(quality=1)
    
    def _get_average_color(self, image_bytes: bytes) -> Tuple[int, int, int]:
        """Get average color from image palette"""
        img_bytes = BytesIO(image_bytes)
        color_thief = ColorThief(img_bytes)
        palette = color_thief.get_palette(color_count=5, quality=1)
        
        # Calculate average
        avg_r = sum(c[0] for c in palette) // len(palette)
        avg_g = sum(c[1] for c in palette) // len(palette)
        avg_b = sum(c[2] for c in palette) // len(palette)
        
        return (avg_r, avg_g, avg_b)
    
    @staticmethod
    def _calculate_saturation(r: int, g: int, b: int) -> float:
        """Calculate color saturation (0-1)"""
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        if max_c == 0:
            return 0
        return (max_c - min_c) / max_c
    
    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> str:
        """Convert RGB to hex color string"""
        return "#{:02X}{:02X}{:02X}".format(r, g, b)
    
    def clear_cache(self):
        """Clear the color cache"""
        self._cache.clear()
        logger.info("Color cache cleared")
