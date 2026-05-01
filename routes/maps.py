import os
import requests
from flask import Blueprint, request, jsonify

maps_bp = Blueprint('maps', __name__)

@maps_bp.route('/find-booths', methods=['POST'])
def find_booths():
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    data = request.json
    pincode = data.get('pincode')
    state = data.get('state')
    
    if not api_key:
        return jsonify({
            "error": "Maps API key missing. Please visit eci.gov.in to find your booth."
        }), 400
        
    try:
        # 1. Geocode pincode
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={pincode},{state},India&key={api_key}"
        geo_res = requests.get(geocode_url).json()
        
        if geo_res['status'] != 'OK':
            return jsonify({"error": "Could not find location for this pincode"}), 400
            
        location = geo_res['results'][0]['geometry']['location']
        lat, lng = location['lat'], location['lng']
        
        # 2. Find places near location (mocking exact 'polling booth' as it requires specific Google Places types, usually school/community center)
        # Using a keyword search for demonstration
        places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=3000&keyword=school|community center|polling&key={api_key}"
        places_res = requests.get(places_url).json()
        
        results = []
        for place in places_res.get('results', [])[:5]: # Return top 5
            results.append({
                "name": place.get('name'),
                "address": place.get('vicinity'),
                "lat": place['geometry']['location']['lat'],
                "lng": place['geometry']['location']['lng'],
                "distance": "~ 1-3 km" # Mocked distance for simplicity
            })
            
        return jsonify({
            "center": {"lat": lat, "lng": lng},
            "booths": results
        })
        
    except Exception as e:
        print(f"Maps Error: {e}")
        return jsonify({"error": "Failed to fetch booths"}), 500
