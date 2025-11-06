ARG BUILD_FROM
FROM $BUILD_FROM

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install Python and dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    gcc \
    python3-dev \
    musl-dev

# Set working directory
WORKDIR /app

# Copy application
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY run.py .

# Copy run script
COPY homeassistant/spotifytowled/run.sh /
RUN chmod a+x /run.sh

# Labels
LABEL \
    io.hass.name="SpotifyToWLED" \
    io.hass.description="Sync Spotify album colors with WLED devices" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version="${BUILD_VERSION}" \
    maintainer="Raphael Bleier"

CMD [ "/run.sh" ]
