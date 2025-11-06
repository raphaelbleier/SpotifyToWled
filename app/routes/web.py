"""
Web routes for the application
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
import logging

from app.core.config import config
from app.core.sync_engine import sync_engine
from app.utils.color_extractor import ColorExtractor

logger = logging.getLogger(__name__)


def register_routes(app):
    """Register all application routes"""
    
    @app.route('/')
    def index():
        """Main dashboard page"""
        status = sync_engine.get_status()
        
        return render_template(
            'index.html',
            is_running=status['is_running'],
            current_color=status['current_color'],
            current_color_hex=ColorExtractor.rgb_to_hex(*status['current_color']),
            current_album_image_url=status.get('current_album_image_url', ''),
            current_track=status.get('current_track', {}),
            color_history=status.get('color_history', []),
            color_method=status.get('color_extraction_method', 'vibrant'),
            spotify_client_id=config.get('SPOTIFY_CLIENT_ID', ''),
            spotify_client_secret=config.get('SPOTIFY_CLIENT_SECRET', ''),
            refresh_interval=config.get('REFRESH_INTERVAL', 30),
            wled_ips=config.get('WLED_IPS', []),
            spotify_authenticated=status.get('spotify_authenticated', False)
        )
    
    # API Routes
    @app.route('/api/status')
    def api_status():
        """Get current status as JSON"""
        status = sync_engine.get_status()
        status['current_color_hex'] = ColorExtractor.rgb_to_hex(*status['current_color'])
        return jsonify(status)
    
    @app.route('/api/sync/start', methods=['POST'])
    def api_sync_start():
        """Start the sync engine"""
        try:
            success = sync_engine.start()
            if success:
                return jsonify({'success': True, 'message': 'Sync started'})
            else:
                return jsonify({'success': False, 'message': 'Failed to start sync. Check configuration.'}), 400
        except Exception as e:
            logger.error(f"Error starting sync: {e}")
            return jsonify({'success': False, 'message': 'An error occurred while starting sync'}), 500
    
    @app.route('/api/sync/stop', methods=['POST'])
    def api_sync_stop():
        """Stop the sync engine"""
        try:
            sync_engine.stop()
            return jsonify({'success': True, 'message': 'Sync stopped'})
        except Exception as e:
            logger.error(f"Error stopping sync: {e}")
            return jsonify({'success': False, 'message': 'An error occurred while stopping sync'}), 500
    
    @app.route('/api/config/update', methods=['POST'])
    def api_config_update():
        """Update configuration"""
        try:
            client_id = request.form.get('client_id', '').strip()
            client_secret = request.form.get('client_secret', '').strip()
            
            # Validate and convert refresh interval with proper error handling
            try:
                refresh_interval = int(request.form.get('refresh_interval', 30))
                if refresh_interval < 1:
                    flash('Refresh interval must be at least 1 second', 'warning')
                    return redirect(url_for('index'))
            except (ValueError, TypeError):
                flash('Invalid refresh interval. Please enter a valid number.', 'warning')
                return redirect(url_for('index'))
            
            config.set('SPOTIFY_CLIENT_ID', client_id)
            config.set('SPOTIFY_CLIENT_SECRET', client_secret)
            config.set('REFRESH_INTERVAL', refresh_interval)
            
            config.save()
            
            flash('Configuration updated successfully', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            logger.error(f"Error updating config: {e}")
            flash('Error updating configuration. Please try again.', 'danger')
            return redirect(url_for('index'))
    
    @app.route('/api/config/color-method', methods=['POST'])
    def api_config_color_method():
        """Update color extraction method"""
        try:
            data = request.get_json()
            method = data.get('method', 'vibrant')
            
            if sync_engine.set_color_extraction_method(method):
                return jsonify({'success': True, 'message': f'Method set to {method}'})
            else:
                return jsonify({'success': False, 'message': 'Invalid method'}), 400
        except Exception as e:
            logger.error(f"Error updating color method: {e}")
            return jsonify({'success': False, 'message': 'An error occurred while updating color method'}), 500
    
    @app.route('/api/wled/add', methods=['POST'])
    def api_wled_add():
        """Add WLED device"""
        try:
            ip = request.form.get('ip', '').strip()
            
            if not ip:
                flash('Please enter a valid IP address', 'warning')
                return redirect(url_for('index'))
            
            wled_ips = config.get('WLED_IPS', [])
            
            if ip not in wled_ips:
                wled_ips.append(ip)
                config.set('WLED_IPS', wled_ips)
                config.save()
                flash(f'WLED device {ip} added', 'success')
            else:
                flash(f'WLED device {ip} already exists', 'info')
            
            return redirect(url_for('index'))
        except Exception as e:
            logger.error(f"Error adding WLED device: {e}")
            flash(f'Error adding device: {e}', 'danger')
            return redirect(url_for('index'))
    
    @app.route('/api/wled/remove', methods=['DELETE'])
    def api_wled_remove():
        """Remove WLED device"""
        try:
            ip = request.args.get('ip', '').strip()
            
            wled_ips = config.get('WLED_IPS', [])
            
            if ip in wled_ips:
                wled_ips.remove(ip)
                config.set('WLED_IPS', wled_ips)
                config.save()
                return jsonify({'success': True, 'message': f'Device {ip} removed'})
            else:
                return jsonify({'success': False, 'message': 'Device not found'}), 404
        except Exception as e:
            logger.error(f"Error removing WLED device: {e}")
            return jsonify({'success': False, 'message': 'An error occurred while removing device'}), 500
    
    @app.route('/api/wled/health')
    def api_wled_health():
        """Check WLED device health"""
        try:
            ip = request.args.get('ip', '').strip()
            
            online = sync_engine.wled_controller.health_check(ip)
            
            return jsonify({
                'ip': ip,
                'online': online,
                'status': 'online' if online else 'offline'
            })
        except Exception as e:
            logger.error(f"Error checking WLED health: {e}")
            return jsonify({'success': False, 'message': 'An error occurred while checking device health'}), 500
    
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring"""
        return jsonify({
            'status': 'healthy',
            'version': '2.0.0',
            'sync_running': sync_engine.is_running
        })
