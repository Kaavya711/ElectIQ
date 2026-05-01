let map;
let markers = [];

function initMap(lat = 20.5937, lng = 78.9629, zoom = 5) {
    // Basic map initialization if API is loaded
    if (typeof google === 'undefined' || !google.maps) {
        console.log("Google Maps API not loaded");
        return;
    }
    
    map = new google.maps.Map(document.getElementById("map-container"), {
        center: { lat, lng },
        zoom: zoom,
        styles: [
            // Custom light theme to match cream background roughly
            {
                "featureType": "all",
                "elementType": "geometry.fill",
                "stylers": [{"color": "#F0EBE1"}] // cream
            },
            {
                "featureType": "water",
                "elementType": "geometry",
                "stylers": [{"color": "#e9e9e9"}]
            }
        ],
        mapTypeControl: false
    });
}

// Global callback for Google Maps script
window.initMap = initMap;

document.addEventListener('DOMContentLoaded', () => {
    const searchBtn = document.getElementById('find-booth-btn');
    const pincodeInput = document.getElementById('pincode-input');
    const stateSelect = document.getElementById('state-select');
    const resultsContainer = document.getElementById('booth-results');
    const mapErrorEl = document.getElementById('map-error');

    if (searchBtn) {
        searchBtn.addEventListener('click', async () => {
            const pincode = pincodeInput.value;
            const state = stateSelect.value;
            
            if (!pincode || pincode.length !== 6) {
                alert("Please enter a valid 6-digit pincode.");
                return;
            }
            if (!state) {
                alert("Please select a state.");
                return;
            }

            searchBtn.textContent = 'Searching...';
            searchBtn.disabled = true;
            resultsContainer.innerHTML = '';
            if (mapErrorEl) mapErrorEl.style.display = 'none';

            try {
                const response = await fetch('/api/find-booths', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ pincode, state })
                });
                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'Failed to fetch');
                }

                displayResults(data.booths);
                updateMap(data.center, data.booths);
                
            } catch (error) {
                console.error("Map search error:", error);
                if (mapErrorEl) {
                    mapErrorEl.textContent = error.message;
                    mapErrorEl.style.display = 'block';
                }
            } finally {
                searchBtn.textContent = 'Find Booths 🔍';
                searchBtn.disabled = false;
            }
        });
    }

    function displayResults(booths) {
        if (booths.length === 0) {
            resultsContainer.innerHTML = '<p class="muted">No booths found nearby.</p>';
            return;
        }

        booths.forEach(booth => {
            const div = document.createElement('div');
            div.className = 'card mb-4';
            div.innerHTML = `
                <h4 style="margin-bottom: 4px">${booth.name}</h4>
                <p class="muted" style="font-size: 14px; margin-bottom: 8px">${booth.address}</p>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 12px; font-weight: bold; color: var(--color-accent)">${booth.distance}</span>
                    <a href="https://www.google.com/maps/dir/?api=1&destination=${booth.lat},${booth.lng}" target="_blank" class="btn-outline" style="padding: 4px 12px; font-size: 12px">Get Directions →</a>
                </div>
            `;
            resultsContainer.appendChild(div);
        });
    }

    function updateMap(center, booths) {
        if (!map) return;
        
        map.setCenter(center);
        map.setZoom(14);
        
        // Clear old markers
        markers.forEach(m => m.setMap(null));
        markers = [];
        
        const infoWindow = new google.maps.InfoWindow();

        booths.forEach(booth => {
            const marker = new google.maps.Marker({
                position: { lat: booth.lat, lng: booth.lng },
                map: map,
                title: booth.name,
                animation: google.maps.Animation.DROP
            });
            
            marker.addListener("click", () => {
                infoWindow.setContent(`
                    <div style="padding: 8px; color: #1A1A1A;">
                        <h4 style="margin: 0 0 4px 0">${booth.name}</h4>
                        <p style="margin: 0; font-size: 12px;">${booth.address}</p>
                    </div>
                `);
                infoWindow.open(map, marker);
            });
            
            markers.push(marker);
        });
    }
});
