"""
Spotify API manager with improved error handling
"""
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging
from typing import Optional, Dict, Tuple
from time import time

logger = logging.getLogger(__name__)


class SpotifyManager:
    """Manage Spotify API interactions with caching"""
    
    def __init__(self, client_id: str, client_secret: str, 
                 redirect_uri: str, scope: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self._sp = None
        self._last_track_id = None
        self._track_cache = {}
        self._cache_duration = 5
    
    def authenticate(self) -> bool:
        """
        Authenticate with Spotify
        
        Returns:
            True if successful, False otherwise
        """
        try:
            auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scope
            )
            self._sp = spotipy.Spotify(auth_manager=auth_manager)
            
            # Test the connection
            self._sp.current_user()
            logger.info("✓ Successfully authenticated with Spotify")
            return True
            
        except Exception as e:
            logger.error(f"✗ Spotify authentication failed: {e}")
            self._sp = None
            return False
    
    def get_current_track(self) -> Optional[Dict]:
        """
        Get currently playing track
        
        Returns:
            Track info dict or None if nothing is playing
        """
        if not self._sp:
            logger.warning("Not authenticated with Spotify")
            return None
        
        try:
            current_track = self._sp.current_user_playing_track()
            
            if not current_track or not current_track.get("item"):
                logger.debug("No track currently playing")
                return None
            
            if not current_track.get("is_playing"):
                logger.debug("Track is paused")
                return None
            
            return current_track
            
        except Exception as e:
            logger.error(f"Error fetching current track: {e}")
            return None
    
    def get_album_image_url(self, track_info: Dict) -> Optional[str]:
        """
        Extract album cover URL from track info
        
        Returns:
            Image URL or None if not available
        """
        try:
            album_images = track_info["item"]["album"].get("images", [])
            if album_images:
                # Return largest image (first one)
                return album_images[0]["url"]
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Error extracting album image: {e}")
        return None
    
    def get_track_info(self, track_info: Dict) -> Dict[str, str]:
        """
        Extract useful track information
        
        Returns:
            Dictionary with track name, artist, album
        """
        try:
            item = track_info.get("item", {})
            return {
                "name": item.get("name", "Unknown"),
                "artist": ", ".join(artist["name"] for artist in item.get("artists", [])),
                "album": item.get("album", {}).get("name", "Unknown"),
                "id": item.get("id", "")
            }
        except Exception as e:
            logger.error(f"Error extracting track info: {e}")
            return {
                "name": "Unknown",
                "artist": "Unknown",
                "album": "Unknown",
                "id": ""
            }
    
    def is_track_changed(self, track_info: Optional[Dict]) -> bool:
        """
        Check if the track has changed since last check
        
        Returns:
            True if track changed, False otherwise
        """
        if not track_info:
            return False
        
        try:
            current_track_id = track_info["item"]["id"]
            if current_track_id != self._last_track_id:
                self._last_track_id = current_track_id
                return True
        except (KeyError, TypeError):
            pass
        
        return False
    
    @property
    def is_authenticated(self) -> bool:
        """Check if authenticated"""
        return self._sp is not None
