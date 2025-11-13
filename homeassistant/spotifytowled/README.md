# SpotifyToWLED Home Assistant Add-on

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

Sync your Spotify album colors with WLED devices directly from Home Assistant!

## About

SpotifyToWLED is a Home Assistant add-on that synchronizes the colors from your currently playing Spotify album covers with your WLED LED devices. Experience an immersive, dynamic lighting experience that matches your music.

This addon supports two modes:
- **Standalone Mode**: Runs the full SpotifyToWLED application within Home Assistant
- **Integration Mode**: Connects to an external Docker server running SpotifyToWLED (recommended for multi-instance setups)

## Features

- 🎨 **Multiple Color Extraction Modes**: Vibrant, Dominant, or Average color selection
- 💡 **Multi-Device Support**: Control multiple WLED devices simultaneously
- 🔄 **Real-time Sync**: Automatic color updates when tracks change
- 📊 **Color History**: Track the last 10 color palettes
- 🌐 **Web Interface**: Beautiful Bootstrap 5 UI accessible from Home Assistant
- ⚡ **Performance Optimized**: API caching and smart track detection
- 🔒 **Secure**: No security vulnerabilities (CodeQL verified)
- 🔗 **Integration Mode**: Connect to external Docker server for centralized management

## Installation

1. **Add Repository**: Add this repository to your Home Assistant:
   - Navigate to **Supervisor** → **Add-on Store** → **⋮** (three dots menu) → **Repositories**
   - Add: `https://github.com/raphaelbleier/SpotifyToWled`

2. **Install Add-on**: 
   - Find "SpotifyToWLED" in the add-on store
   - Click **Install**

3. **Configure** (see configuration sections below based on your chosen mode)

4. **Start**: Click **Start** and check the logs

## Configuration

### Mode 1: Standalone (Run everything in Home Assistant)

Use this mode if you want to run SpotifyToWLED entirely within Home Assistant.

```yaml
mode: "standalone"
spotify_client_id: "your_spotify_client_id"
spotify_client_secret: "your_spotify_client_secret"
wled_ips:
  - "192.168.1.100"
  - "192.168.1.101"
refresh_interval: 30
cache_duration: 5
color_extraction_method: "vibrant"
```

### Mode 2: Integration (Connect to External Docker Server)

Use this mode if you already have SpotifyToWLED running in Docker elsewhere and want to access it through Home Assistant.

```yaml
mode: "integration"
server_url: "http://192.168.1.50:5000"
```

**Benefits of Integration Mode:**
- Lighter resource usage in Home Assistant
- Share one SpotifyToWLED instance across multiple Home Assistant instances
- Easier to manage updates centrally
- Better for advanced Docker/Portainer setups

### Configuration Options

#### Required Settings (Standalone Mode)

| Setting | Description | Example |
|---------|-------------|---------|
| `mode` | Operating mode | `standalone` or `integration` |
| `spotify_client_id` | Your Spotify Client ID | `abc123...` |
| `spotify_client_secret` | Your Spotify Client Secret | `xyz789...` |
| `wled_ips` | List of WLED device IPs | `["192.168.1.100"]` |

#### Required Settings (Integration Mode)

| Setting | Description | Example |
|---------|-------------|---------|
| `mode` | Operating mode | `integration` |
| `server_url` | URL of your Docker server | `http://192.168.1.50:5000` |

#### Optional Settings (Standalone Mode Only)

| Setting | Default | Description |
|---------|---------|-------------|
| `refresh_interval` | `30` | Check for track changes every N seconds |
| `cache_duration` | `5` | Cache API responses for N seconds |
| `color_extraction_method` | `vibrant` | Color mode: `vibrant`, `dominant`, or `average` |

## Getting Spotify Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click **Create an App**
4. Fill in:
   - **App name**: SpotifyToWLED
   - **App description**: Sync album colors with WLED
   - Accept terms and click **Create**
5. You'll see your **Client ID** and **Client Secret**
6. Click **Edit Settings**
7. Add Redirect URI: `http://homeassistant.local:5000/callback` (or your HA IP)
8. Click **Save**

## Web Interface

Access the web interface through:
- **Standalone Mode**: Home Assistant Ingress (click "Open Web UI")
- **Integration Mode**: Proxied through the addon to your external server
- **Direct URL**: `http://homeassistant.local:5000`

## Using with Home Assistant Automations

### Example: Start/Stop with Presence

```yaml
automation:
  - alias: "Start SpotifyToWLED when home"
    trigger:
      - platform: state
        entity_id: person.your_name
        to: "home"
    action:
      - service: hassio.addon_start
        data:
          addon: local_spotifytowled
          
  - alias: "Stop SpotifyToWLED when away"
    trigger:
      - platform: state
        entity_id: person.your_name
        to: "not_home"
    action:
      - service: hassio.addon_stop
        data:
          addon: local_spotifytowled
```

## Troubleshooting

### Integration Mode Issues

1. **Can't connect to external server**
   - Verify server URL is correct and accessible from Home Assistant
   - Check firewall rules
   - Ensure the Docker server is running: `docker ps | grep spotifytowled`
   - Test connectivity: `curl http://your-server:5000/health`

2. **502 Bad Gateway**
   - Server is not responding
   - Check Docker server logs: `docker logs spotifytowled`

### Standalone Mode Issues

See the main troubleshooting section in the [full documentation](https://github.com/raphaelbleier/SpotifyToWled)

## Support

For issues, feature requests, or questions:
- GitHub Issues: https://github.com/raphaelbleier/SpotifyToWled/issues
- Documentation: See README.md in the repository

## Changelog

### 2.1.0
- Added Integration mode for connecting to external Docker servers
- Improved proxy support for multi-instance setups
- Enhanced configuration flexibility

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
