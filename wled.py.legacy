import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from io import BytesIO
from PIL import Image
import threading
import json
import os

from flask import Flask, request, redirect, render_template_string

# NEW: We'll use colorthief to replicate spicetify-dynamic-theme style picking.
# pip install colorthief
from colorthief import ColorThief

app = Flask(__name__)

# ----------------------------
# CONFIG & GLOBAL STATE
# ----------------------------
# Default config in case config.json doesn't exist or is missing keys
config = {
    "SPOTIFY_CLIENT_ID": "YOUR_SPOTIFY_CLIENT_ID",
    "SPOTIFY_CLIENT_SECRET": "YOUR_SPOTIFY_CLIENT_SECRET",
    "SPOTIFY_REDIRECT_URI": "http://localhost:8888/callback",
    "SPOTIFY_SCOPE": "user-read-currently-playing",
    "WLED_IPS": ["192.168.68.100"],
    "REFRESH_INTERVAL": 30,
    # We do NOT persist 'IS_RUNNING' in the file; it's an in-memory toggle only.
    "IS_RUNNING": False
}

# Track the current color extracted from the album cover
# Use a tuple (r, g, b). Initialize to black.
current_color = (0, 0, 0)

# Store the last album image URL for reference (optional)
current_album_image_url = ""


# ----------------------------
# CONFIG PERSISTENCE
# ----------------------------
def load_config():
    """Load config from config.json if it exists; update the global config dict."""
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r") as f:
                file_config = json.load(f)
            # Update global config with values from file_config
            for key, value in file_config.items():
                config[key] = value
            print("[INFO] Loaded config from config.json")
        except Exception as e:
            print("[WARNING] Could not load config.json:", e)
    else:
        print("[INFO] config.json not found. Using default in-memory config.")


def save_config():
    """
    Save the config (minus IS_RUNNING) to config.json.
    Overwrites any existing file.
    """
    data_to_save = {
        "SPOTIFY_CLIENT_ID": config["SPOTIFY_CLIENT_ID"],
        "SPOTIFY_CLIENT_SECRET": config["SPOTIFY_CLIENT_SECRET"],
        "SPOTIFY_REDIRECT_URI": config["SPOTIFY_REDIRECT_URI"],
        "SPOTIFY_SCOPE": config["SPOTIFY_SCOPE"],
        "WLED_IPS": config["WLED_IPS"],
        "REFRESH_INTERVAL": config["REFRESH_INTERVAL"]
    }
    try:
        with open("config.json", "w") as f:
            json.dump(data_to_save, f, indent=2)
        print("[INFO] Saved config to config.json")
    except Exception as e:
        print("[ERROR] Could not save config.json:", e)


# Load config on startup
load_config()


# ----------------------------
# HELPER FUNCTIONS
# ----------------------------
def rgb_saturation(r, g, b):
    """
    Approximate saturation (0..1) in HSV-like fashion.
    We'll pick the color with the highest saturation from the palette
    to mimic "vibrant" color picking.
    """
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    if max_c == 0:
        return 0
    return (max_c - min_c) / max_c

def get_spicetify_like_color_from_image_url(image_url):
    """
    1. Download the album cover.
    2. Use ColorThief to extract a palette (like spicetify-dynamic-theme).
    3. Pick the color with the highest saturation (i.e., "vibrant").
       If everything is dull, pick the dominant color as fallback.

    Feel free to skip near-black or near-white if desired.
    """
    response = requests.get(image_url, timeout=5)
    response.raise_for_status()

    # Load into memory
    img_bytes = BytesIO(response.content)
    color_thief = ColorThief(img_bytes)

    # Try to get a palette of up to 5 colors
    palette = color_thief.get_palette(color_count=5, quality=1)

    if not palette:
        # Fallback: just get the dominant color if palette fails
        return color_thief.get_color(quality=1)

    # We'll pick the color from the palette with the highest saturation:
    # palette is a list of (r, g, b).
    best_color = None
    best_sat = -1

    for (r, g, b) in palette:
        sat = rgb_saturation(r, g, b)
        if sat > best_sat:
            best_sat = sat
            best_color = (r, g, b)

    # If everything was zero saturation (all grayscale?), fallback to dominant
    if best_sat == 0:
        return color_thief.get_color(quality=1)

    return best_color


def set_wled_color(ip_address, r, g, b):
    """
    Set the color on a WLED device (given by ip_address) via its JSON API.
    """
    url = f"http://{ip_address}/json/state"
    payload = {
        "seg": [
            {
                "col": [[r, g, b]]
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            print(f"[OK] WLED @ {ip_address} -> color set to ({r}, {g}, {b}).")
        else:
            print(f"[Error] WLED @ {ip_address} HTTP status code: {response.status_code}")
    except Exception as e:
        print(f"[Error] Could not reach WLED @ {ip_address}: {e}")


def rgb_to_hex(r, g, b):
    """Convert (R, G, B) to #RRGGBB hex format for display in HTML."""
    return "#{:02X}{:02X}{:02X}".format(r, g, b)


# ----------------------------
# SPOTIFY -> WLED MAIN LOOP
# ----------------------------
def spotify_loop():
    """
    Runs in a separate thread. Continuously fetches the
    currently playing track from Spotify, extracts a color
    using a method similar to spicetify-dynamic-theme (vibrant),
    and updates WLED.
    """
    global current_color, current_album_image_url

    # Re-authenticate with Spotify each time we start the loop
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=config["SPOTIFY_CLIENT_ID"],
            client_secret=config["SPOTIFY_CLIENT_SECRET"],
            redirect_uri=config["SPOTIFY_REDIRECT_URI"],
            scope=config["SPOTIFY_SCOPE"]
        )
    )

    print("[INFO] Starting Spotify -> WLED loop...")
    while config["IS_RUNNING"]:
        try:
            current_track = sp.current_user_playing_track()

            if not current_track or not current_track.get("item"):
                print("[INFO] No song is currently playing on Spotify.")
            else:
                if current_track.get("is_playing"):
                    album_images = current_track["item"]["album"].get("images", [])
                    if album_images:
                        image_url = album_images[0]["url"]  # typically largest
                        current_album_image_url = image_url
                        print(f"[INFO] Album cover URL: {image_url}")

                        # Like spicetify-dynamic-theme: pick a "vibrant" color
                        r, g, b = get_spicetify_like_color_from_image_url(image_url)
                        current_color = (r, g, b)
                        print(f"[INFO] Extracted dynamic color: R={r}, G={g}, B={b}")

                        # Send color to each WLED
                        for wled_ip in config["WLED_IPS"]:
                            set_wled_color(wled_ip, r, g, b)
                    else:
                        print("[INFO] No album cover found for the current track.")
                else:
                    print("[INFO] Spotify track is paused (or not playing).")

            time.sleep(config["REFRESH_INTERVAL"])
        except Exception as e:
            print("[Error in Spotify Loop]", e)
            time.sleep(config["REFRESH_INTERVAL"])

    print("[INFO] Spotify -> WLED loop stopped.")


# We'll keep track of the thread object so we can start/stop it.
spotify_thread = None


# ----------------------------
# FLASK ROUTES
# ----------------------------
@app.route("/")
def index():
    """
    Show the current config values:
    - Spotify Client ID/Secret
    - Refresh interval
    - WLED IPs (add/remove)
    - Start/Stop control
    - Current color + album image
    """
    html_template = """
    <html>
    <head>
        <title>Spotify -> WLED Config</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .color-box {
                width: 100px;
                height: 100px;
                border: 2px solid #666;
                display: inline-block;
                vertical-align: middle;
            }
            .section {
                margin-bottom: 20px;
                padding: 10px;
                border: 1px solid #ccc;
            }
        </style>
    </head>
    <body>
        <h1>Spotify -> WLED Configuration</h1>

        <div class="section">
            <h2>Current Status</h2>
            <p>Loop is: <strong>{{ 'Running' if IS_RUNNING else 'Stopped' }}</strong></p>
            {% if IS_RUNNING %}
                <a href="/stop">[Stop]</a>
            {% else %}
                <a href="/start">[Start]</a>
            {% endif %}
        </div>

        <div class="section">
            <h2>Spotify Settings</h2>
            <form action="/update_config" method="post">
                <label>Spotify Client ID:</label><br>
                <input type="text" name="client_id" value="{{ SPOTIFY_CLIENT_ID }}"><br><br>

                <label>Spotify Client Secret:</label><br>
                <input type="text" name="client_secret" value="{{ SPOTIFY_CLIENT_SECRET }}"><br><br>

                <label>Refresh Interval (seconds):</label><br>
                <input type="number" name="refresh_interval" value="{{ REFRESH_INTERVAL }}"><br><br>

                <button type="submit">Update Config</button>
            </form>
        </div>

        <div class="section">
            <h2>WLED Devices</h2>
            <ul>
                {% for ip in WLED_IPS %}
                <li>
                    {{ ip }}
                    <a href="/remove_wled?ip={{ ip }}">[Remove]</a>
                </li>
                {% endfor %}
            </ul>
            <form action="/add_wled" method="post">
                <label>Add WLED IP:</label><br>
                <input type="text" name="new_wled_ip" placeholder="192.168.x.x">
                <button type="submit">Add</button>
            </form>
        </div>

        <div class="section">
            <h2>Current Color</h2>
            <p>RGB: ({{ current_color[0] }}, {{ current_color[1] }}, {{ current_color[2] }})</p>
            <div class="color-box" style="background-color: {{ current_color_hex }};"></div>
        </div>

        {% if current_album_image_url %}
        <div class="section">
            <h2>Current Album Cover</h2>
            <img src="{{ current_album_image_url }}" alt="Album Cover" width="300">
        </div>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(
        html_template,
        SPOTIFY_CLIENT_ID=config["SPOTIFY_CLIENT_ID"],
        SPOTIFY_CLIENT_SECRET=config["SPOTIFY_CLIENT_SECRET"],
        REFRESH_INTERVAL=config["REFRESH_INTERVAL"],
        IS_RUNNING=config["IS_RUNNING"],
        WLED_IPS=config["WLED_IPS"],
        current_color=current_color,
        current_color_hex=rgb_to_hex(*current_color),
        current_album_image_url=current_album_image_url
    )


@app.route("/update_config", methods=["POST"])
def update_config_route():
    """
    Handle updating the Spotify client ID, client secret,
    and refresh interval from the form. Then save to config.json.
    """
    config["SPOTIFY_CLIENT_ID"] = request.form.get("client_id", "").strip()
    config["SPOTIFY_CLIENT_SECRET"] = request.form.get("client_secret", "").strip()
    try:
        refresh_interval = int(request.form.get("refresh_interval", "30"))
        config["REFRESH_INTERVAL"] = max(refresh_interval, 1)  # at least 1 second
    except ValueError:
        pass

    # Save updates to config.json
    save_config()

    return redirect("/")


@app.route("/add_wled", methods=["POST"])
def add_wled():
    """
    Add a new WLED IP to the config list, then save.
    """
    new_ip = request.form.get("new_wled_ip", "").strip()
    if new_ip and new_ip not in config["WLED_IPS"]:
        config["WLED_IPS"].append(new_ip)

    save_config()
    return redirect("/")


@app.route("/remove_wled")
def remove_wled():
    """
    Remove a WLED IP from the config list, then save.
    """
    ip_to_remove = request.args.get("ip")
    if ip_to_remove in config["WLED_IPS"]:
        config["WLED_IPS"].remove(ip_to_remove)

    save_config()
    return redirect("/")


@app.route("/start")
def start():
    """
    Start the Spotify -> WLED loop in a background thread.
    """
    if not config["IS_RUNNING"]:
        config["IS_RUNNING"] = True
        global spotify_thread
        spotify_thread = threading.Thread(target=spotify_loop, daemon=True)
        spotify_thread.start()
    return redirect("/")


@app.route("/stop")
def stop():
    """
    Stop the Spotify -> WLED loop.
    """
    config["IS_RUNNING"] = False
    return redirect("/")


# ----------------------------
# RUN FLASK (ENTRY POINT)
# ----------------------------
if __name__ == "__main__":
    # By default, runs on http://127.0.0.1:5000
    app.run(debug=True, port=5000)
