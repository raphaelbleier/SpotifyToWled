#!/usr/bin/with-contenv bashio
# ==============================================================================
# Start SpotifyToWLED
# ==============================================================================

# Get mode from configuration
MODE=$(bashio::config 'mode')
bashio::log.info "Running in ${MODE} mode"

if [ "$MODE" = "integration" ]; then
    # Integration mode - create proxy to external Docker server
    bashio::log.info "Starting in Integration mode - connecting to external server"
    
    SERVER_URL=$(bashio::config 'server_url')
    
    if [ -z "$SERVER_URL" ]; then
        bashio::log.error "Server URL is required in integration mode!"
        exit 1
    fi
    
    bashio::log.info "External server: ${SERVER_URL}"
    
    # Create a simple proxy using Python Flask
    cat > /app/proxy.py << 'EOFPROXY'
import os
import requests
from flask import Flask, request, jsonify, redirect, Response
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
SERVER_URL = os.environ.get('SERVER_URL', '').rstrip('/')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    """Proxy all requests to the external server"""
    url = f"{SERVER_URL}/{path}"
    
    # Forward query parameters
    if request.query_string:
        url = f"{url}?{request.query_string.decode('utf-8')}"
    
    logger.info(f"Proxying {request.method} {url}")
    
    try:
        # Prepare headers (exclude host)
        headers = {key: value for key, value in request.headers if key.lower() != 'host'}
        
        # Make request to external server
        resp = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=30
        )
        
        # Return response
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = [(name, value) for name, value in resp.raw.headers.items()
                          if name.lower() not in excluded_headers]
        
        return Response(resp.content, resp.status_code, response_headers)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Proxy error: {e}")
        return jsonify({'error': 'Unable to connect to external server', 'details': str(e)}), 502

if __name__ == '__main__':
    logger.info(f"Starting proxy to {SERVER_URL}")
    app.run(host='0.0.0.0', port=5000, debug=False)
EOFPROXY
    
    # Install requests if not available
    pip3 install --no-cache-dir requests 2>/dev/null || true
    
    # Set environment and start proxy
    export SERVER_URL="${SERVER_URL}"
    exec python3 /app/proxy.py
    
else
    # Standalone mode - run full application
    bashio::log.info "Starting in Standalone mode - running full application"
    
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
fi
