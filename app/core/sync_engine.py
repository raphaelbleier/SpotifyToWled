"""
Main sync engine that orchestrates Spotify to WLED synchronization
"""
import threading
import logging
from time import sleep
from typing import Optional, Dict, Tuple

from app.core.config import config
from app.utils.spotify_manager import SpotifyManager
from app.utils.color_extractor import ColorExtractor
from app.utils.wled_controller import WLEDController

logger = logging.getLogger(__name__)


class SyncEngine:
    """
    Orchestrates the synchronization between Spotify and WLED devices
    """
    
    def __init__(self):
        self.spotify_manager: Optional[SpotifyManager] = None
        self.color_extractor = ColorExtractor(cache_duration=config.get("CACHE_DURATION", 5))
        self.wled_controller = WLEDController(
            max_retries=config.get("MAX_RETRIES", 3),
            retry_delay=config.get("RETRY_DELAY", 2)
        )
        
        self.is_running = False
        self.current_color: Tuple[int, int, int] = (0, 0, 0)
        self.current_album_image_url = ""
        self.current_track_info: Dict[str, str] = {}
        self.color_history: list = []  # Store last 10 colors
        self.max_history = 10
        
        self._thread: Optional[threading.Thread] = None
        self._color_extraction_method = 'vibrant'
    
    def initialize_spotify(self) -> bool:
        """Initialize Spotify manager with current config"""
        try:
            self.spotify_manager = SpotifyManager(
                client_id=config.get("SPOTIFY_CLIENT_ID"),
                client_secret=config.get("SPOTIFY_CLIENT_SECRET"),
                redirect_uri=config.get("SPOTIFY_REDIRECT_URI"),
                scope=config.get("SPOTIFY_SCOPE")
            )
            return self.spotify_manager.authenticate()
        except Exception as e:
            logger.error(f"Failed to initialize Spotify: {e}")
            return False
    
    def get_spotify_auth_url(self) -> Optional[str]:
        """
        Get Spotify authorization URL for OAuth flow
        
        Returns:
            Authorization URL or None
        """
        try:
            if not self.spotify_manager:
                # Initialize spotify manager if not already done
                self.spotify_manager = SpotifyManager(
                    client_id=config.get("SPOTIFY_CLIENT_ID"),
                    client_secret=config.get("SPOTIFY_CLIENT_SECRET"),
                    redirect_uri=config.get("SPOTIFY_REDIRECT_URI"),
                    scope=config.get("SPOTIFY_SCOPE")
                )
                # Initialize auth manager
                self.spotify_manager.authenticate()
            
            return self.spotify_manager.get_auth_url()
        except Exception as e:
            logger.error(f"Failed to get auth URL: {e}")
            return None
    
    def handle_spotify_callback(self, code: str) -> bool:
        """
        Handle Spotify OAuth callback
        
        Args:
            code: Authorization code from Spotify
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.spotify_manager:
                logger.error("Spotify manager not initialized")
                return False
            
            return self.spotify_manager.handle_callback(code)
        except Exception as e:
            logger.error(f"Failed to handle callback: {e}")
            return False
    
    def start(self) -> bool:
        """
        Start the sync loop in a background thread
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.is_running:
            logger.warning("Sync engine is already running")
            return False
        
        # Validate configuration
        is_valid, errors = config.validate()
        if not is_valid:
            logger.error(f"Invalid configuration: {', '.join(errors)}")
            return False
        
        # Initialize Spotify
        if not self.initialize_spotify():
            logger.error("Failed to initialize Spotify connection")
            return False
        
        self.is_running = True
        self._thread = threading.Thread(target=self._sync_loop, daemon=True)
        self._thread.start()
        logger.info("🎵 Sync engine started")
        return True
    
    def stop(self) -> None:
        """Stop the sync loop"""
        if self.is_running:
            self.is_running = False
            logger.info("🛑 Sync engine stopped")
    
    def set_color_extraction_method(self, method: str) -> bool:
        """
        Set the color extraction method
        
        Args:
            method: One of 'vibrant', 'dominant', 'average'
        
        Returns:
            True if valid method, False otherwise
        """
        valid_methods = ['vibrant', 'dominant', 'average']
        if method in valid_methods:
            self._color_extraction_method = method
            logger.info(f"Color extraction method set to: {method}")
            return True
        return False
    
    def _sync_loop(self) -> None:
        """Main synchronization loop"""
        logger.info("Starting sync loop...")
        
        while self.is_running:
            try:
                # Get current track
                track = self.spotify_manager.get_current_track()
                
                if not track:
                    logger.debug("No track playing, waiting...")
                    sleep(config.get("REFRESH_INTERVAL", 30))
                    continue
                
                # Check if track changed
                if self.spotify_manager.is_track_changed(track):
                    logger.info("🎵 New track detected")
                    
                    # Extract track info
                    self.current_track_info = self.spotify_manager.get_track_info(track)
                    logger.info(f"Now playing: {self.current_track_info['name']} "
                              f"by {self.current_track_info['artist']}")
                    
                    # Get album cover URL
                    image_url = self.spotify_manager.get_album_image_url(track)
                    if not image_url:
                        logger.warning("No album cover available")
                        sleep(config.get("REFRESH_INTERVAL", 30))
                        continue
                    
                    self.current_album_image_url = image_url
                    
                    # Extract color
                    color = self.color_extractor.get_color(
                        image_url, 
                        method=self._color_extraction_method
                    )
                    
                    if color != self.current_color:
                        self.current_color = color
                        
                        # Add to history
                        self._add_to_history(color, self.current_track_info)
                        
                        # Update WLED devices
                        wled_ips = config.get("WLED_IPS", [])
                        results = self.wled_controller.set_color_all(wled_ips, *color)
                        
                        # Log results
                        success_count = sum(1 for v in results.values() if v)
                        logger.info(f"✓ Updated {success_count}/{len(wled_ips)} WLED devices")
                
                # Wait before next iteration
                sleep(config.get("REFRESH_INTERVAL", 30))
                
            except Exception as e:
                logger.error(f"Error in sync loop: {e}", exc_info=True)
                sleep(config.get("REFRESH_INTERVAL", 30))
        
        logger.info("Sync loop ended")
    
    def _add_to_history(self, color: Tuple[int, int, int], track_info: Dict) -> None:
        """Add color to history"""
        self.color_history.insert(0, {
            'color': color,
            'track': track_info.get('name', 'Unknown'),
            'artist': track_info.get('artist', 'Unknown')
        })
        
        # Keep only last N entries
        if len(self.color_history) > self.max_history:
            self.color_history = self.color_history[:self.max_history]
    
    def get_status(self) -> Dict:
        """Get current status of sync engine"""
        return {
            'is_running': self.is_running,
            'current_color': self.current_color,
            'current_album_image_url': self.current_album_image_url,
            'current_track': self.current_track_info,
            'color_extraction_method': self._color_extraction_method,
            'color_history': self.color_history,
            'spotify_authenticated': self.spotify_manager.is_authenticated if self.spotify_manager else False
        }


# Global sync engine instance
sync_engine = SyncEngine()
