"""
WLED device controller with retry logic and health checks
"""
import requests
import logging
from typing import Dict, List, Optional
from time import sleep

logger = logging.getLogger(__name__)


class WLEDController:
    """Control WLED devices with improved error handling"""
    
    def __init__(self, max_retries: int = 3, retry_delay: int = 2):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._device_status = {}  # Track device health
    
    def set_color(self, ip: str, r: int, g: int, b: int) -> bool:
        """
        Set color on WLED device with retry logic
        
        Args:
            ip: WLED device IP address
            r, g, b: RGB color values (will be clamped to 0-255 for LED compatibility)
        
        Returns:
            True if successful, False otherwise
        """
        # Ensure RGB values are in valid LED range (0-255)
        r = max(0, min(255, int(r)))
        g = max(0, min(255, int(g)))
        b = max(0, min(255, int(b)))
        
        url = f"http://{ip}/json/state"
        payload = {
            "seg": [{
                "col": [[r, g, b]]
            }]
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(url, json=payload, timeout=5)
                
                if response.status_code == 200:
                    logger.info(f"✓ WLED @ {ip} -> RGB({r}, {g}, {b})")
                    self._device_status[ip] = {
                        'status': 'online',
                        'last_success': True
                    }
                    return True
                else:
                    logger.warning(f"WLED @ {ip} returned status {response.status_code}")
                    
            except requests.Timeout:
                logger.warning(f"Timeout connecting to WLED @ {ip} (attempt {attempt + 1}/{self.max_retries})")
            except requests.ConnectionError:
                logger.warning(f"Connection error to WLED @ {ip} (attempt {attempt + 1}/{self.max_retries})")
            except Exception as e:
                logger.error(f"Unexpected error with WLED @ {ip}: {e}")
            
            # Wait before retry (except on last attempt)
            if attempt < self.max_retries - 1:
                sleep(self.retry_delay)
        
        # All retries failed
        logger.error(f"✗ Failed to set color on WLED @ {ip} after {self.max_retries} attempts")
        self._device_status[ip] = {
            'status': 'offline',
            'last_success': False
        }
        return False
    
    def set_color_all(self, ips: List[str], r: int, g: int, b: int) -> Dict[str, bool]:
        """
        Set color on multiple WLED devices
        
        Returns:
            Dictionary mapping IP to success status
        """
        results = {}
        for ip in ips:
            results[ip] = self.set_color(ip, r, g, b)
        return results
    
    def set_brightness(self, ip: str, brightness: int) -> bool:
        """
        Set brightness on WLED device (0-255)
        
        Args:
            ip: WLED device IP address
            brightness: Brightness level (0-255)
        
        Returns:
            True if successful, False otherwise
        """
        url = f"http://{ip}/json/state"
        payload = {
            "bri": max(0, min(255, brightness))
        }
        
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                logger.info(f"✓ WLED @ {ip} brightness set to {brightness}")
                return True
            else:
                logger.warning(f"WLED @ {ip} brightness change failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error setting brightness on WLED @ {ip}: {e}")
            return False
    
    def set_effect(self, ip: str, effect_id: int) -> bool:
        """
        Set effect on WLED device
        
        Args:
            ip: WLED device IP address
            effect_id: Effect ID (0-based index)
        
        Returns:
            True if successful, False otherwise
        """
        url = f"http://{ip}/json/state"
        payload = {
            "seg": [{
                "fx": effect_id
            }]
        }
        
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                logger.info(f"✓ WLED @ {ip} effect set to {effect_id}")
                return True
            else:
                logger.warning(f"WLED @ {ip} effect change failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error setting effect on WLED @ {ip}: {e}")
            return False
    
    def get_info(self, ip: str) -> Optional[Dict]:
        """
        Get device information
        
        Returns:
            Device info dict or None if failed
        """
        try:
            response = requests.get(f"http://{ip}/json/info", timeout=3)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.debug(f"Could not get info from WLED @ {ip}: {e}")
        return None
    
    def health_check(self, ip: str) -> bool:
        """
        Check if WLED device is reachable
        
        Returns:
            True if device is online, False otherwise
        """
        try:
            response = requests.get(f"http://{ip}/json/info", timeout=2)
            is_online = response.status_code == 200
            self._device_status[ip] = {
                'status': 'online' if is_online else 'offline',
                'last_checked': True
            }
            return is_online
        except Exception:
            self._device_status[ip] = {
                'status': 'offline',
                'last_checked': True
            }
            return False
    
    def get_device_status(self, ip: str) -> Dict:
        """Get cached device status"""
        return self._device_status.get(ip, {'status': 'unknown', 'last_success': None})
    
    def get_all_device_status(self) -> Dict[str, Dict]:
        """Get status of all tracked devices"""
        return self._device_status.copy()
