#!/usr/bin/with-contenv bashio
# ==============================================================================
# Start SpotifyToWLED
# ==============================================================================

# Get configuration from Home Assistant
SPOTIFY_CLIENT_ID=$(bashio::config 'spotify_client_id')
SPOTIFY_CLIENT_SECRET=$(bashio::config 'spotify_client_secret')
WLED_IPS=$(bashio::config 'wled_ips')
REFRESH_INTERVAL=$(bashio::config 'refresh_interval')
CACHE_DURATION=$(bashio::config 'cache_duration')
COLOR_METHOD=$(bashio::config 'color_extraction_method')

# Create config directory
mkdir -p /config

# Create config.json from Home Assistant settings
cat > /config/config.json << EOF
{
  "SPOTIFY_CLIENT_ID": "${SPOTIFY_CLIENT_ID}",
  "SPOTIFY_CLIENT_SECRET": "${SPOTIFY_CLIENT_SECRET}",
  "SPOTIFY_REDIRECT_URI": "http://homeassistant.local:5000/callback",
  "SPOTIFY_SCOPE": "user-read-currently-playing",
  "WLED_IPS": ${WLED_IPS},
  "REFRESH_INTERVAL": ${REFRESH_INTERVAL},
  "CACHE_DURATION": ${CACHE_DURATION},
  "MAX_RETRIES": 3,
  "RETRY_DELAY": 2
}
EOF

bashio::log.info "Starting SpotifyToWLED..."
bashio::log.info "Spotify Client ID: ${SPOTIFY_CLIENT_ID:0:10}..."
bashio::log.info "WLED IPs: ${WLED_IPS}"
bashio::log.info "Refresh Interval: ${REFRESH_INTERVAL}s"
bashio::log.info "Color Method: ${COLOR_METHOD}"

# Set environment variables
export CONFIG_PATH=/config/config.json
export LOG_PATH=/data/spotifytowled.log

# Start the application
cd /app
exec python run.py
