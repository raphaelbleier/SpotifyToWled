"""
Main application entry point
"""
import logging
from flask import Flask
from app.routes.web import register_routes
from app.core.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('spotifytowled.log')
    ]
)

logger = logging.getLogger(__name__)


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.secret_key = config.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Register routes
    register_routes(app)
    
    logger.info("SpotifyToWLED v2.0.0 initialized")
    return app


def main():
    """Main entry point"""
    app = create_app()
    
    # Run the application
    port = config.get('PORT', 5000)
    debug = config.get('DEBUG', False)
    
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
    main()
