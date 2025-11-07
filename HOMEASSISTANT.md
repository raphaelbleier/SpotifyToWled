# Home Assistant Integration Guide

This guide explains how to integrate SpotifyToWLED with Home Assistant.

## Installation Methods

### Method 1: Home Assistant Add-on (Recommended)

The easiest way to run SpotifyToWLED on Home Assistant is using the official add-on.

#### Step 1: Add Repository

1. Navigate to **Supervisor** → **Add-on Store**
2. Click the **⋮** (three dots) menu in the top right
3. Select **Repositories**
4. Add: `https://github.com/raphaelbleier/SpotifyToWled`
5. Click **Add** then **Close**

#### Step 2: Install Add-on

1. Refresh the Add-on Store page
2. Find **SpotifyToWLED** in the list
3. Click on it, then click **Install**
4. Wait for installation to complete (may take a few minutes)

#### Step 3: Configure

1. Go to the **Configuration** tab
2. Fill in your settings:

```yaml
spotify_client_id: "your_client_id_here"
spotify_client_secret: "your_client_secret_here"
wled_ips:
  - "192.168.1.100"
  - "192.168.1.101"
refresh_interval: 30
cache_duration: 5
color_extraction_method: "vibrant"
```

3. Click **Save**

#### Step 4: Start the Add-on

1. Go to the **Info** tab
2. Enable **Start on boot** (optional but recommended)
3. Enable **Watchdog** (optional but recommended)
4. Click **Start**
5. Check the **Log** tab for any errors

#### Step 5: Access Web Interface

- Click **Open Web UI** button
- Or access via Ingress in Home Assistant
- Configure Spotify credentials and WLED devices

### Method 2: Docker Container in Home Assistant

If you prefer to run as a standalone Docker container:

1. Install **Portainer** add-on from Home Assistant
2. Follow the [Docker Deployment Guide](DOCKER.md)
3. Access at `http://homeassistant.local:5000`

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
7. Add Redirect URI: `http://homeassistant.local:5000/callback`
8. Click **Save**

## Configuration Options

### Required Settings

| Setting | Description | Example |
|---------|-------------|---------|
| `spotify_client_id` | Your Spotify Client ID | `abc123...` |
| `spotify_client_secret` | Your Spotify Client Secret | `xyz789...` |
| `wled_ips` | List of WLED device IPs | `["192.168.1.100"]` |

### Optional Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `refresh_interval` | `30` | Check for track changes every N seconds |
| `cache_duration` | `5` | Cache API responses for N seconds |
| `color_extraction_method` | `vibrant` | Color mode: `vibrant`, `dominant`, or `average` |

## Using with Home Assistant Automations

### Example: Sync Only When Home

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

### Example: Sync Only During Evening

```yaml
automation:
  - alias: "Start music sync in evening"
    trigger:
      - platform: time
        at: "19:00:00"
    action:
      - service: hassio.addon_start
        data:
          addon: local_spotifytowled
          
  - alias: "Stop music sync at night"
    trigger:
      - platform: time
        at: "23:00:00"
    action:
      - service: hassio.addon_stop
        data:
          addon: local_spotifytowled
```

### Example: Notify When Sync Starts

```yaml
automation:
  - alias: "Notify when music sync starts"
    trigger:
      - platform: state
        entity_id: switch.spotifytowled
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "SpotifyToWLED"
          message: "Music color sync is now active! 🎵💡"
```

## Integration with WLED Entities

If you have WLED integrated in Home Assistant, you can create automations:

```yaml
automation:
  - alias: "Restore WLED brightness after sync"
    trigger:
      - platform: state
        entity_id: switch.spotifytowled
        to: "off"
    action:
      - service: light.turn_on
        target:
          entity_id: light.wled_strip
        data:
          brightness: 255
          rgb_color: [255, 255, 255]
```

## Troubleshooting

### Add-on Won't Start

1. **Check Logs**
   - Go to **Log** tab in the add-on
   - Look for error messages

2. **Verify Configuration**
   - Ensure Spotify credentials are correct
   - Check WLED IP addresses are reachable
   - Validate YAML syntax (use YAML validator)

3. **Check Network**
   - Ensure WLED devices are on same network
   - Ping WLED devices from Home Assistant terminal:
     ```bash
     ping 192.168.1.100
     ```

### Can't Access Web UI

1. **Check Add-on Status**
   - Ensure add-on is running
   - Look at the **Info** tab

2. **Try Direct URL**
   - Instead of Ingress, try: `http://homeassistant.local:5000`

3. **Check Port Conflict**
   - Port 5000 might be used by another service
   - Check Home Assistant logs

### Spotify Authentication Issues

1. **Redirect URI Mismatch**
   - In Spotify Dashboard, ensure redirect URI is exact:
   - `http://homeassistant.local:5000/callback`
   - Or use your Home Assistant IP: `http://192.168.1.x:5000/callback`

2. **Clear Cache**
   - Stop the add-on
   - Delete `.cache` files if present
   - Restart add-on

### WLED Devices Not Responding

1. **Test Connection**
   - Open WLED web interface directly
   - Ensure devices are powered on
   - Check network connectivity

2. **Use Health Check**
   - In SpotifyToWLED web UI, use the health check button
   - Verify device status

3. **Check WLED API**
   - Test manually:
     ```bash
     curl http://192.168.1.100/json/state
     ```

## Uninstalling

### Remove Add-on

1. Go to **Supervisor** → **Add-on Store**
2. Click on **SpotifyToWLED**
3. Click **Uninstall**
4. Optionally, remove the repository from Repositories list

### Clean Up

Configuration is stored in `/config` and `/data` directories within the add-on. These are automatically removed when you uninstall.

## Advanced: Custom Configuration

If you need to manually edit configuration:

1. Use the **File Editor** add-on
2. Navigate to add-on config directory
3. Edit `config.json` carefully
4. Restart the add-on

## Performance Tips

1. **Increase Refresh Interval**
   - If you have slow internet, increase to 45-60 seconds
   
2. **Reduce WLED Devices**
   - Start with 1-2 devices, add more gradually
   
3. **Use Vibrant Mode**
   - Provides best color extraction performance

## Security Considerations

1. **Keep Spotify Credentials Safe**
   - Don't share your Client ID/Secret
   - Use Home Assistant secrets if possible

2. **Network Security**
   - Consider running on isolated VLAN
   - Use firewall rules if needed

3. **Regular Updates**
   - Keep add-on updated for security patches

## Support and Community

- **Issues**: [GitHub Issues](https://github.com/raphaelbleier/SpotifyToWled/issues)
- **Documentation**: [README.md](README.md)
- **Home Assistant Forum**: Tag with `spotifytowled`

## Roadmap

Future Home Assistant integrations:
- [ ] Native Home Assistant entities (sensors, switches)
- [ ] Services for color control
- [ ] Integration with HA music player
- [ ] Dashboard cards
- [ ] Lovelace UI support

---

**Enjoy your smart home lighting experience! 🏠🎵💡**
