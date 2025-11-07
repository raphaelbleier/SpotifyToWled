ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM $BUILD_FROM

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install Python and dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    gcc \
    python3-dev \
    musl-dev \
    jpeg-dev \
    zlib-dev \
    jq

# Set working directory
WORKDIR /app

# Copy application
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY run.py .

# Create directories
RUN mkdir -p /config /data

# Copy run script
COPY homeassistant/spotifytowled/run.sh /
RUN chmod a+x /run.sh

# Labels
LABEL \
    io.hass.name="SpotifyToWLED" \
    io.hass.description="Sync Spotify album colors with WLED devices" \
    io.hass.type="addon" \
    maintainer="Raphael Bleier <raphaelbleier@users.noreply.github.com>"

CMD [ "/run.sh" ]
