// JavaScript for SpotifyToWLED Application

// API Base URL
const API_BASE = '/api';

// Start sync
async function startSync() {
    try {
        showLoading();
        const response = await fetch(`${API_BASE}/sync/start`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Sync started successfully!');
            setTimeout(() => location.reload(), 1000);
        } else {
            showError(data.message || 'Failed to start sync');
        }
    } catch (error) {
        showError('Error starting sync: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Stop sync
async function stopSync() {
    try {
        showLoading();
        const response = await fetch(`${API_BASE}/sync/stop`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Sync stopped');
            setTimeout(() => location.reload(), 1000);
        } else {
            showError(data.message || 'Failed to stop sync');
        }
    } catch (error) {
        showError('Error stopping sync: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Update color extraction method
async function updateColorMethod(method) {
    try {
        const response = await fetch(`${API_BASE}/config/color-method`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ method: method })
        });
        const data = await response.json();
        
        if (data.success) {
            showSuccess(`Color extraction method changed to ${method}`);
        } else {
            showError(data.message || 'Failed to update method');
        }
    } catch (error) {
        showError('Error updating color method: ' + error.message);
    }
}

// Remove WLED device
async function removeWled(ip) {
    if (!confirm(`Remove WLED device ${ip}?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/wled/remove?ip=${encodeURIComponent(ip)}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        
        if (data.success) {
            showSuccess('WLED device removed');
            setTimeout(() => location.reload(), 1000);
        } else {
            showError(data.message || 'Failed to remove device');
        }
    } catch (error) {
        showError('Error removing device: ' + error.message);
    }
}

// Check WLED health
async function checkWledHealth(ip) {
    try {
        showLoading();
        const response = await fetch(`${API_BASE}/wled/health?ip=${encodeURIComponent(ip)}`);
        const data = await response.json();
        
        if (data.online) {
            showSuccess(`${ip} is online ✓`);
        } else {
            showError(`${ip} is offline ✗`);
        }
    } catch (error) {
        showError('Error checking health: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Update status in real-time
async function updateStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const data = await response.json();
        
        // Update current color
        if (data.current_color) {
            const [r, g, b] = data.current_color;
            const colorDisplay = document.getElementById('colorDisplay');
            const colorRGB = document.getElementById('colorRGB');
            const colorHex = document.getElementById('colorHex');
            
            if (colorDisplay) {
                colorDisplay.style.backgroundColor = `rgb(${r}, ${g}, ${b})`;
            }
            if (colorRGB) {
                colorRGB.textContent = `RGB: (${r}, ${g}, ${b})`;
            }
            if (colorHex) {
                const hex = rgbToHex(r, g, b);
                colorHex.textContent = hex;
            }
        }
        
        // Update album cover
        if (data.current_album_image_url) {
            const albumCover = document.getElementById('albumCover');
            if (albumCover && albumCover.src !== data.current_album_image_url) {
                albumCover.src = data.current_album_image_url;
            }
        }
        
        // Update track info
        if (data.current_track) {
            const trackName = document.getElementById('trackName');
            const trackArtist = document.getElementById('trackArtist');
            const trackAlbum = document.getElementById('trackAlbum');
            
            if (trackName) trackName.textContent = data.current_track.name;
            if (trackArtist) {
                setElementWithIcon(trackArtist, 'bi-person', data.current_track.artist);
            }
            if (trackAlbum) {
                setElementWithIcon(trackAlbum, 'bi-disc', data.current_track.album);
            }
        }
        
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

// Utility: Set element content with icon (XSS-safe)
function setElementWithIcon(element, iconClass, text) {
    element.innerHTML = '';
    const icon = document.createElement('i');
    icon.className = 'bi ' + iconClass;
    element.appendChild(icon);
    element.appendChild(document.createTextNode(' ' + text));
}

// Utility: RGB to Hex
function rgbToHex(r, g, b) {
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase();
}

// Show loading indicator
function showLoading() {
    // Create a simple loading overlay
    const overlay = document.createElement('div');
    overlay.id = 'loadingOverlay';
    overlay.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 9999;';
    overlay.innerHTML = '<div class="spinner-border text-light" role="status"><span class="visually-hidden">Loading...</span></div>';
    document.body.appendChild(overlay);
}

// Hide loading indicator
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.remove();
    }
}

// Show success message
function showSuccess(message) {
    showToast(message, 'success');
}

// Show error message
function showError(message) {
    showToast(message, 'danger');
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show`;
    toast.style.cssText = 'position: fixed; top: 70px; right: 20px; z-index: 1050; min-width: 300px;';
    
    // Create text node to prevent XSS
    const messageNode = document.createTextNode(message);
    toast.appendChild(messageNode);
    
    // Add close button
    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'btn-close';
    closeButton.setAttribute('data-bs-dismiss', 'alert');
    toast.appendChild(closeButton);
    
    document.body.appendChild(toast);
    
    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('SpotifyToWLED initialized');
});
