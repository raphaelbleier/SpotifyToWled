"""
Main application entry point
"""
import logging
import os
from flask import Flask
from app.routes.web import register_routes
from app.core.config import config

# Get log path from environment or use default
log_path = os.environ.get('LOG_PATH', 'spotifytowled.log')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_path)
    ]
)

logger = logging.getLogger(__name__)


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure secret key with security warning
    secret_key = config.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    if secret_key == 'dev-secret-key-change-in-production':
        logger.warning("⚠️  Default secret key is being used! This is insecure for production. Please set SECRET_KEY in your configuration.")
    app.secret_key = secret_key
    
    # Register routes
    register_routes(app)
    
    logger.info("SpotifyToWLED v2.0.0 initialized")
    return app


def main():
    """Main entry point"""
    app = create_app()
    
    # Run the application
    # Port can be set via environment variable (for Docker/HA) or config
    port = int(os.environ.get('PORT', config.get('PORT', 5000)))
    debug = config.get('DEBUG', False)
    
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
    main()
