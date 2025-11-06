# Migration Guide from v1.0 to v2.0

## Overview
SpotifyToWled v2.0 is a complete rewrite with a modern architecture. This guide will help you migrate from the old monolithic `wled.py` to the new modular application.

## Key Changes

### Structure Changes
- **Old**: Single file `wled.py` (~413 lines)
- **New**: Modular structure with separate concerns
  - `app/core/` - Core business logic
  - `app/utils/` - Utility functions
  - `app/routes/` - Web routes and API
  - `app/templates/` - HTML templates
  - `app/static/` - CSS and JavaScript

### Configuration Changes
- **Old**: Configuration stored in memory, lost on restart
- **New**: Configuration persisted to `config.json` file
  - Automatic validation
  - Better error messages
  - Support for more options

### Running the Application
- **Old**: `python wled.py`
- **New**: `python run.py`

### New Configuration Options
The new version includes additional configuration options:

```json
{
  "CACHE_DURATION": 5,      // NEW: Cache API responses (seconds)
  "MAX_RETRIES": 3,         // NEW: Retry attempts for failed operations
  "RETRY_DELAY": 2          // NEW: Delay between retries (seconds)
}
```

## Migration Steps

### 1. Backup Your Old Configuration
If you had custom settings in the old version, note them down:
- Spotify Client ID
- Spotify Client Secret
- WLED IP addresses
- Refresh interval

### 2. Install New Dependencies
```bash
pip install -r requirements.txt
```

The new version requires `colorthief` which was missing before.

### 3. First Run
```bash
python run.py
```

On first run, the application will:
1. Create a default `config.json` file
2. Start the web server on `http://localhost:5000`
3. Show the configuration page

### 4. Configure via Web UI
1. Open your browser to `http://localhost:5000`
2. Enter your Spotify credentials
3. Add your WLED device IP addresses
4. Adjust settings as needed
5. Click "Save Configuration"

### 5. Start Syncing
Click the "Start Sync" button in the web interface.

## New Features in v2.0

### Color Extraction Modes
Choose how colors are extracted from album covers:
- **Vibrant** (Default): Most saturated, vivid colors
- **Dominant**: Most prevalent color
- **Average**: Average of palette colors

### Color History
Track the last 10 colors that were synced, with track information.

### Device Management
- Add/remove WLED devices easily
- Health check for each device
- Status tracking

### Advanced Controls
- Brightness control (coming soon)
- Effect selection (coming soon)
- Multiple color modes

## Troubleshooting

### Port Already in Use
If port 5000 is in use, you can change it in `config.json`:
```json
{
  "PORT": 5001
}
```

### Authentication Issues
1. Check your Spotify Client ID and Secret
2. Ensure redirect URI is: `http://localhost:5000/callback`
3. Clear the `.cache` file if it exists

### WLED Connection Problems
1. Use the health check button to test connectivity
2. Ensure WLED devices are on the same network
3. Check firewall settings

## Rollback to Old Version
If you need to use the old version, it's been preserved as `wled.py.legacy`:

```bash
python wled.py.legacy
```

Note: The old version will not receive updates or bug fixes.

## Getting Help
- Check the [README](README.md) for detailed documentation
- Review the logs in `spotifytowled.log`
- Report issues on GitHub

---

**Welcome to SpotifyToWled v2.0!** 🎵💡✨
