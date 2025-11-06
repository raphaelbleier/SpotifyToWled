# SpotifyToWLED v2.0

Bring your music to life! **SpotifyToWLED** syncs the color palette of your Spotify album covers with your WLED LEDs for a vibrant, immersive experience.

## ✨ What's New in v2.0

- 🏗️ **Restructured codebase** with proper modular architecture
- 🎨 **Modern web UI** with Bootstrap 5 and real-time updates
- ⚡ **Performance improvements** with caching and async operations
- 🔧 **Enhanced configuration** management with validation
- 📊 **Color history** tracking and visualization
- 🛡️ **Better error handling** with automatic retries
- 🔍 **Multiple color extraction modes** (vibrant, dominant, average)
- 💡 **Advanced WLED controls** (brightness, effects)
- 📡 **Health monitoring** for devices and API connections
- 📝 **Comprehensive logging** for debugging
- 🐳 **Docker support** with easy Portainer deployment
- 🏠 **Home Assistant add-on** for seamless smart home integration

---

## 🚀 Quick Start

Choose your deployment method:

### 🐳 Docker (Recommended for Portainer)

**Quick start:**
```bash
docker run -d \
  --name spotifytowled \
  -p 5000:5000 \
  -v $(pwd)/config:/config \
  -v $(pwd)/data:/data \
  --restart unless-stopped \
  ghcr.io/raphaelbleier/spotifytowled:latest
```

**Or with Docker Compose:**
```bash
docker-compose up -d
```

📖 **[Full Docker & Portainer Guide →](DOCKER.md)**

### 🏠 Home Assistant Add-on

1. Add repository: `https://github.com/raphaelbleier/SpotifyToWled`
2. Install **SpotifyToWLED** add-on
3. Configure and start
4. Open Web UI

📖 **[Full Home Assistant Guide →](HOMEASSISTANT.md)**

### 🐍 Python (Manual Installation)

**Prerequisites:**
- Python 3.8 or higher
- A **Spotify Developer App** (free): [Create one here](https://developer.spotify.com/dashboard)
- One or more **WLED devices** on your network

**Installation:**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/raphaelbleier/SpotifyToWled.git
   cd SpotifyToWled
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python run.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

5. **Configure the application**:
   - Enter your Spotify **Client ID** and **Client Secret**
   - Add your WLED device IP addresses
   - Adjust refresh interval if needed
   - Choose your preferred color extraction method

6. **Start syncing** and enjoy the light show! 🎶✨

---

## 🎯 Features

### Color Extraction Modes
- **Vibrant** (Recommended): Extracts the most saturated, vivid color from the album
- **Dominant**: Uses the most prevalent color in the album art
- **Average**: Calculates an average color from the palette

### WLED Integration
- Multiple device support
- Device health monitoring
- Brightness control
- Effect selection
- Automatic retry on connection failures

### Web Interface
- Real-time status updates
- Color history visualization
- Device management
- Configuration management
- Responsive design for mobile and desktop

---

## 📁 Project Structure

```
SpotifyToWled/
├── app/
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   └── sync_engine.py     # Main sync orchestrator
│   ├── utils/
│   │   ├── color_extractor.py # Color extraction with caching
│   │   ├── spotify_manager.py # Spotify API wrapper
│   │   └── wled_controller.py # WLED device controller
│   ├── routes/
│   │   └── web.py             # Web routes and API endpoints
│   ├── templates/
│   │   ├── base.html          # Base template
│   │   └── index.html         # Main dashboard
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css      # Custom styles
│   │   └── js/
│   │       └── app.js         # Client-side JavaScript
│   └── main.py                # Application factory
├── run.py                     # Application entry point
├── requirements.txt           # Python dependencies
└── config.json               # Configuration file (auto-generated)
```

---

## 🔧 Configuration

Configuration is stored in `config.json` (auto-generated on first run). You can also edit it directly:

```json
{
  "SPOTIFY_CLIENT_ID": "your_client_id",
  "SPOTIFY_CLIENT_SECRET": "your_client_secret",
  "SPOTIFY_REDIRECT_URI": "http://localhost:5000/callback",
  "SPOTIFY_SCOPE": "user-read-currently-playing",
  "WLED_IPS": ["192.168.1.100", "192.168.1.101"],
  "REFRESH_INTERVAL": 30,
  "CACHE_DURATION": 5,
  "MAX_RETRIES": 3,
  "RETRY_DELAY": 2
}
```

---

## 🚢 Deployment Options

### Docker & Portainer
Perfect for home servers and NAS devices. Includes health checks and automatic restarts.
- **[Docker Deployment Guide](DOCKER.md)** - Complete guide for Docker and Portainer
- Pre-built images available on GitHub Container Registry
- Simple volume mapping for configuration persistence

### Home Assistant
Native integration with Home Assistant supervisor.
- **[Home Assistant Guide](HOMEASSISTANT.md)** - Complete integration guide
- Official add-on available
- Ingress support for seamless UI access
- Automation examples included

### Manual Python
Traditional installation for development or custom setups.
- Full control over environment
- Easy debugging and development
- See Quick Start section above

---

## 🐛 Troubleshooting

### Spotify Authentication Issues
- Ensure your Client ID and Secret are correct
- Check that the redirect URI matches: `http://localhost:5000/callback`
- Make sure you've authorized the app in your browser

### WLED Connection Problems
- Verify WLED devices are on the same network
- Check IP addresses are correct
- Use the health check button to test connectivity
- Ensure WLED firmware is up to date

### Performance Issues
- Increase the refresh interval for slower networks
- Reduce the number of WLED devices
- Clear the color cache if needed

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🙏 Acknowledgments

- [WLED](https://github.com/Aircoookie/WLED) - Amazing LED control software
- [Spotipy](https://github.com/plamere/spotipy) - Spotify Web API wrapper
- [ColorThief](https://github.com/fengsp/color-thief-py) - Color extraction library

---

**Enjoy your synchronized light show! 🎵💡✨**
