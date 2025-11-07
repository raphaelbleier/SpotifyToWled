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

# Create config.json from Home Assistant settings using jq for safe JSON generation
jq -n \
  --arg client_id "$SPOTIFY_CLIENT_ID" \
  --arg client_secret "$SPOTIFY_CLIENT_SECRET" \
  --arg redirect_uri "http://homeassistant.local:5000/callback" \
  --arg scope "user-read-currently-playing" \
  --argjson wled_ips "$WLED_IPS" \
  --argjson refresh_interval "$REFRESH_INTERVAL" \
  --argjson cache_duration "$CACHE_DURATION" \
  '{
    SPOTIFY_CLIENT_ID: $client_id,
    SPOTIFY_CLIENT_SECRET: $client_secret,
    SPOTIFY_REDIRECT_URI: $redirect_uri,
    SPOTIFY_SCOPE: $scope,
    WLED_IPS: $wled_ips,
    REFRESH_INTERVAL: $refresh_interval,
    CACHE_DURATION: $cache_duration,
    MAX_RETRIES: 3,
    RETRY_DELAY: 2
  }' > /config/config.json

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
