#!/usr/bin/env python3
"""
SpotifyToWLED - Sync Spotify album colors with WLED devices
Version 2.0.0
"""
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import main

if __name__ == '__main__':
    main()
