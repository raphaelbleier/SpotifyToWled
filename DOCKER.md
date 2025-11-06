# Docker Deployment Guide

This guide explains how to deploy SpotifyToWLED using Docker and Portainer.

## Quick Start with Docker

### Using Docker Run

```bash
docker run -d \
  --name spotifytowled \
  -p 5000:5000 \
  -v $(pwd)/config:/config \
  -v $(pwd)/data:/data \
  -e TZ=Europe/Berlin \
  --restart unless-stopped \
  ghcr.io/raphaelbleier/spotifytowled:latest
```

### Using Docker Compose

1. Create a `docker-compose.yml` file (or use the one in the repository)
2. Run:

```bash
docker-compose up -d
```

## Deploying on Portainer

### Method 1: Using Docker Compose (Recommended)

1. **Login to Portainer**
   - Navigate to your Portainer instance
   - Go to **Stacks** → **Add stack**

2. **Configure Stack**
   - **Name**: `spotifytowled`
   - **Build method**: `Repository` or `Upload`
   
3. **Option A: From Repository**
   - **Repository URL**: `https://github.com/raphaelbleier/SpotifyToWled`
   - **Repository reference**: `main`
   - **Compose path**: `docker-compose.yml`
   
4. **Option B: Paste Compose**
   - Copy the contents from `docker-compose.yml`
   - Paste into the web editor

5. **Environment Variables** (Optional)
   ```
   TZ=Europe/Berlin
   CONFIG_PATH=/config/config.json
   LOG_PATH=/data/spotifytowled.log
   ```

6. **Deploy**
   - Click **Deploy the stack**
   - Wait for the container to start

### Method 2: Using Container (Manual)

1. **Go to Containers**
   - Navigate to **Containers** → **Add container**

2. **Basic Settings**
   - **Name**: `spotifytowled`
   - **Image**: `ghcr.io/raphaelbleier/spotifytowled:latest`

3. **Network Ports**
   - Click **publish a new network port**
   - **host**: `5000`
   - **container**: `5000`

4. **Volumes**
   - Click **map additional volume**
   - Volume 1:
     - **container**: `/config`
     - **host**: `/path/to/config` (or create a volume)
   - Volume 2:
     - **container**: `/data`
     - **host**: `/path/to/data` (or create a volume)

5. **Environment Variables**
   - Click **add environment variable**
   - `TZ`: `Europe/Berlin`
   - `CONFIG_PATH`: `/config/config.json`
   - `LOG_PATH`: `/data/spotifytowled.log`

6. **Restart Policy**
   - Select **Unless stopped**

7. **Deploy**
   - Click **Deploy the container**

## Accessing the Application

After deployment, access the web interface at:
- **URL**: `http://your-server-ip:5000`
- Or through Portainer's container console

## Initial Configuration

1. **Open the web interface**
2. **Enter Spotify Credentials**
   - Get them from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
3. **Add WLED Devices**
   - Enter your WLED device IP addresses
4. **Save Configuration**
5. **Start Sync**

## Directory Structure

```
./config/          # Configuration files (persistent)
└── config.json    # Application configuration

./data/            # Application data (persistent)
└── spotifytowled.log  # Application logs
```

## Volumes Explained

| Volume | Purpose | Required |
|--------|---------|----------|
| `/config` | Stores configuration (Spotify credentials, WLED IPs) | Yes |
| `/data` | Stores logs and runtime data | Recommended |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CONFIG_PATH` | `/config/config.json` | Path to configuration file |
| `LOG_PATH` | `/data/spotifytowled.log` | Path to log file |
| `PORT` | `5000` | Web interface port |
| `TZ` | `UTC` | Timezone for logs |

## Building Your Own Image

If you want to build the image yourself:

```bash
# Clone the repository
git clone https://github.com/raphaelbleier/SpotifyToWled.git
cd SpotifyToWled

# Build the image
docker build -t spotifytowled:custom .

# Run the custom image
docker run -d \
  --name spotifytowled \
  -p 5000:5000 \
  -v $(pwd)/config:/config \
  -v $(pwd)/data:/data \
  spotifytowled:custom
```

## Health Check

The container includes a built-in health check that runs every 30 seconds:

```bash
# Check container health status
docker inspect --format='{{.State.Health.Status}}' spotifytowled

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' spotifytowled
```

## Troubleshooting

### Container Won't Start

1. Check logs:
   ```bash
   docker logs spotifytowled
   ```

2. Verify volumes are accessible:
   ```bash
   docker inspect spotifytowled | grep -A 10 Mounts
   ```

### Can't Access Web Interface

1. Check if container is running:
   ```bash
   docker ps | grep spotifytowled
   ```

2. Verify port mapping:
   ```bash
   docker port spotifytowled
   ```

3. Check firewall rules on host

### Configuration Issues

1. Access container shell:
   ```bash
   docker exec -it spotifytowled sh
   ```

2. Check config file:
   ```bash
   cat /config/config.json
   ```

3. View logs in real-time:
   ```bash
   docker logs -f spotifytowled
   ```

## Updating the Container

### Using Portainer

1. Go to **Containers**
2. Select `spotifytowled`
3. Click **Recreate**
4. Enable **Pull latest image**
5. Click **Recreate**

### Using Docker Compose

```bash
docker-compose pull
docker-compose up -d
```

### Using Docker CLI

```bash
docker pull ghcr.io/raphaelbleier/spotifytowled:latest
docker stop spotifytowled
docker rm spotifytowled
# Run the docker run command again
```

## Backup Configuration

Always backup your configuration before updating:

```bash
# Backup config
docker cp spotifytowled:/config/config.json ./config.json.backup

# Restore if needed
docker cp ./config.json.backup spotifytowled:/config/config.json
```

## Advanced: Using with Reverse Proxy

If you're using a reverse proxy (nginx, Traefik, etc.), you can add labels:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.spotifytowled.rule=Host(`spotify.yourdomain.com`)"
  - "traefik.http.services.spotifytowled.loadbalancer.server.port=5000"
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/raphaelbleier/SpotifyToWled/issues
- Documentation: See README.md

---

**Happy syncing with Docker! 🐳🎵💡**
