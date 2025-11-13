# Changelog - Version 2.1.0

## 🎉 Release Highlights

Version 2.1.0 fixes critical Docker authentication issues and introduces Home Assistant integration mode for advanced deployment scenarios.

---

## 🐛 Bug Fixes

### Fixed: Docker Spotify Authentication Failure

**Issue**: Running SpotifyToWLED in Docker resulted in authentication error:
```
ERROR - ✗ Spotify authentication failed: [Errno 98] Address already in use
```

**Root Cause**: 
- SpotifyOAuth's default behavior attempts to start a local HTTP server for OAuth callback
- This conflicts with Flask app already running on port 5000
- In Docker/headless environments, the browser-based auth flow is not suitable

**Solution Implemented**:
1. Added `/callback` route in Flask application to handle OAuth redirects
2. Modified SpotifyOAuth initialization with `open_browser=False` parameter
3. Implemented persistent token caching in `/config/.spotify_cache`
4. Created web-based authentication flow with UI button
5. Added API endpoints for OAuth URL generation and callback handling

**Impact**: 
- ✅ Spotify authentication now works in Docker containers
- ✅ Tokens persist across container restarts (no re-authentication needed)
- ✅ User-friendly authentication via web interface
- ✅ Fully compatible with headless/server environments

---

## ✨ New Features

### Home Assistant Integration Mode

Added dual-mode support for Home Assistant addon:

#### Standalone Mode (Default)
- Runs complete SpotifyToWLED application within Home Assistant
- Self-contained with no external dependencies
- Original behavior preserved for existing users
- Best for single Home Assistant instances

#### Integration Mode (New)
- Lightweight HTTP proxy to external Docker server
- Share one SpotifyToWLED instance across multiple Home Assistant installations
- Significantly reduced resource usage in Home Assistant
- Centralized configuration and management
- Perfect for multi-instance or Portainer deployments

**Configuration Example**:
```yaml
# Standalone Mode
mode: "standalone"
spotify_client_id: "your_client_id"
spotify_client_secret: "your_secret"
wled_ips:
  - "192.168.1.100"

# Integration Mode
mode: "integration"
server_url: "http://192.168.1.50:5000"
```

**Benefits**:
- 🔋 Reduced CPU/memory usage in Home Assistant
- 🔄 Easy updates through centralized Docker management
- 🏢 Enterprise-friendly for multiple HA instances
- 🎯 Better separation of concerns

---

## 🔧 Technical Changes

### Application Core

**`app/utils/spotify_manager.py`**:
- Added `cache_path` parameter to constructor
- Implemented `get_auth_url()` method for OAuth flow initiation
- Implemented `handle_callback()` method for OAuth code exchange
- Set `open_browser=False` in SpotifyOAuth initialization
- Automatic cache path resolution using config directory

**`app/routes/web.py`**:
- Added `/callback` route for Spotify OAuth redirect handling
- Added `/api/spotify/auth-url` endpoint for authorization URL generation
- Error handling for OAuth failures
- Flash messages for user feedback

**`app/core/sync_engine.py`**:
- Added `get_spotify_auth_url()` method
- Added `handle_spotify_callback()` method
- Integration with SpotifyManager OAuth methods

**`app/templates/index.html`**:
- Added "Authenticate with Spotify" button
- Conditional display based on authentication status
- User-friendly messaging for auth status

**`app/static/js/app.js`**:
- Added `authenticateSpotify()` function
- Handles auth URL fetching and redirection
- Error display for auth failures

### Home Assistant Addon

**`homeassistant/spotifytowled/config.json`**:
- Added `mode` configuration option (standalone/integration)
- Added `server_url` for integration mode
- Made Spotify credentials optional (not needed in integration mode)
- Version bumped to 2.1.0
- Updated schema for new options

**`homeassistant/spotifytowled/run.sh`**:
- Mode detection and branching logic
- Standalone mode: runs full application (original behavior)
- Integration mode: creates HTTP proxy using Flask
- Proxy implementation forwards all requests to external server
- Automatic installation of `requests` library for proxy

### Documentation

**`README.md`**:
- Added v2.1 feature highlights
- Updated setup instructions with authentication steps
- Added Spotify redirect URI configuration

**`DOCKER.md`**:
- Added "Initial Setup and Spotify Authentication" section
- Step-by-step authentication guide
- Token caching explanation

**`HOMEASSISTANT.md`**:
- Complete rewrite with dual-mode documentation
- Pros/cons comparison of each mode
- Separate installation guides for both modes
- Integration mode setup instructions

**`homeassistant/spotifytowled/README.md`**:
- Dual-mode feature documentation
- Configuration examples for both modes
- Troubleshooting for integration mode

---

## 🔒 Security

### CodeQL Analysis: ✅ PASSED
- **Python**: 0 vulnerabilities found
- **JavaScript**: 0 vulnerabilities found

### Security Improvements:
- OAuth tokens stored in persistent volume (not in code)
- Redirect URI validation through Spotify Developer Console
- No credentials stored in container layers
- Secure token caching mechanism

---

## 📦 Migration Guide

### From v2.0 to v2.1

**Docker Users**:
1. Pull latest image: `docker pull ghcr.io/raphaelbleier/spotifytowled:latest`
2. Stop container: `docker stop spotifytowled`
3. Remove container: `docker rm spotifytowled`
4. Recreate with same volumes (preserves config)
5. Access web UI and click "Authenticate with Spotify"
6. Your config and WLED devices are preserved

**Home Assistant Users (Standalone)**:
1. Update addon from Home Assistant
2. Configuration automatically migrates (adds `mode: standalone`)
3. No manual changes needed
4. Restart addon

**Home Assistant Users (Migrating to Integration)**:
1. Deploy Docker server separately (see DOCKER.md)
2. Configure Docker server via web UI
3. Update HA addon config:
   ```yaml
   mode: "integration"
   server_url: "http://your-docker-server:5000"
   ```
4. Restart addon
5. Remove Spotify credentials from HA config (now in Docker server)

### Backward Compatibility
- ✅ All v2.0 configurations work without changes
- ✅ Default behavior unchanged (standalone mode)
- ✅ No breaking changes to API or configuration structure

---

## 🐞 Known Issues

None identified in this release.

---

## 👥 Contributors

- **raphaelbleier** - Maintainer
- GitHub Copilot - Code assistance

---

## 📅 Release Date

November 13, 2024

---

## 🔗 Links

- **Repository**: https://github.com/raphaelbleier/SpotifyToWled
- **Docker Hub**: ghcr.io/raphaelbleier/spotifytowled
- **Issues**: https://github.com/raphaelbleier/SpotifyToWled/issues
- **Documentation**: See README.md, DOCKER.md, and HOMEASSISTANT.md

---

## 🙏 Acknowledgments

Thanks to all users who reported the Docker authentication issue and provided feedback!
