"""
Spotify API manager with improved error handling
"""
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging
import os
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class SpotifyManager:
    """Manage Spotify API interactions with caching"""
    
    def __init__(self, client_id: str, client_secret: str, 
                 redirect_uri: str, scope: str, cache_path: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.cache_path = cache_path or os.path.join(
            os.environ.get('CONFIG_PATH', '/config').rsplit('/', 1)[0],
            '.spotify_cache'
        )
        self._sp = None
        self._auth_manager = None
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
            self._auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scope,
                cache_path=self.cache_path,
                open_browser=False  # Don't try to open browser in Docker/headless
            )
            self._sp = spotipy.Spotify(auth_manager=self._auth_manager)
            
            # Test the connection
            self._sp.current_user()
            logger.info("✓ Successfully authenticated with Spotify")
            return True
            
        except Exception as e:
            logger.error(f"✗ Spotify authentication failed: {e}")
            self._sp = None
            return False
    
    def get_auth_url(self) -> Optional[str]:
        """
        Get the authorization URL for OAuth flow
        
        Returns:
            Authorization URL or None if auth manager not initialized
        """
        if not self._auth_manager:
            logger.error("Auth manager not initialized")
            return None
        
        return self._auth_manager.get_authorize_url()
    
    def handle_callback(self, code: str) -> bool:
        """
        Handle OAuth callback with authorization code
        
        Args:
            code: Authorization code from Spotify
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self._auth_manager:
                logger.error("Auth manager not initialized")
                return False
            
            # Get token using the code
            token_info = self._auth_manager.get_access_token(code, as_dict=True)
            
            if token_info:
                # Re-initialize Spotify client with the new token
                self._sp = spotipy.Spotify(auth_manager=self._auth_manager)
                logger.info("✓ Successfully authenticated with Spotify via callback")
                return True
            else:
                logger.error("Failed to get access token from code")
                return False
                
        except Exception as e:
            logger.error(f"Error handling OAuth callback: {e}")
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
        except (KeyError, TypeError) as e:
            logger.debug(f"Could not extract track ID for change detection: {e}")
        
        return False
    
    @property
    def is_authenticated(self) -> bool:
        """Check if authenticated"""
        return self._sp is not None
