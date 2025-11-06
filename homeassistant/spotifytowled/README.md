# SpotifyToWLED Home Assistant Add-on

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

Sync your Spotify album colors with WLED devices directly from Home Assistant!

## About

SpotifyToWLED is a Home Assistant add-on that synchronizes the colors from your currently playing Spotify album covers with your WLED LED devices. Experience an immersive, dynamic lighting experience that matches your music.

## Features

- 🎨 **Multiple Color Extraction Modes**: Vibrant, Dominant, or Average color selection
- 💡 **Multi-Device Support**: Control multiple WLED devices simultaneously
- 🔄 **Real-time Sync**: Automatic color updates when tracks change
- 📊 **Color History**: Track the last 10 color palettes
- 🌐 **Web Interface**: Beautiful Bootstrap 5 UI accessible from Home Assistant
- ⚡ **Performance Optimized**: API caching and smart track detection
- 🔒 **Secure**: No security vulnerabilities (CodeQL verified)

## Installation

1. **Add Repository**: Add this repository to your Home Assistant:
   - Navigate to **Supervisor** → **Add-on Store** → **⋮** (three dots menu) → **Repositories**
   - Add: `https://github.com/raphaelbleier/SpotifyToWled`

2. **Install Add-on**: 
   - Find "SpotifyToWLED" in the add-on store
   - Click **Install**

3. **Configure**:
   - Get your Spotify credentials from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Add your WLED device IP addresses
   - Save configuration

4. **Start**: Click **Start** and check the logs

## Configuration

```yaml
spotify_client_id: "your_spotify_client_id"
spotify_client_secret: "your_spotify_client_secret"
wled_ips:
  - "192.168.1.100"
  - "192.168.1.101"
refresh_interval: 30
cache_duration: 5
color_extraction_method: "vibrant"
```

### Option: `spotify_client_id`

Your Spotify application Client ID. Get it from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).

### Option: `spotify_client_secret`

Your Spotify application Client Secret.

### Option: `wled_ips`

List of WLED device IP addresses on your network.

### Option: `refresh_interval`

How often to check for track changes (in seconds). Default: 30

### Option: `cache_duration`

How long to cache API responses (in seconds). Default: 5

### Option: `color_extraction_method`

Color extraction method: `vibrant`, `dominant`, or `average`. Default: `vibrant`

## Web Interface

Access the web interface through:
- Home Assistant Ingress (click "Open Web UI")
- Direct URL: `http://homeassistant.local:5000`

## Support

For issues, feature requests, or questions:
- GitHub Issues: https://github.com/raphaelbleier/SpotifyToWled/issues
- Documentation: See README.md in the repository

## Changelog

### 2.0.0
- Initial Home Assistant add-on release
- Complete overhaul with modern architecture
- Bootstrap 5 web interface
- Multi-device support
- Color history tracking
- Performance optimizations

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
