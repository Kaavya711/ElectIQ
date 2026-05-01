"""
Maps routes for ElectIQ — polling booth finder via Google Maps APIs.

Provides a single endpoint that geocodes an Indian pincode and returns
nearby candidate polling locations using the Places Nearby Search API.
"""

import logging
import os

import requests
from flask import Blueprint, jsonify, request

logger = logging.getLogger(__name__)

maps_bp = Blueprint("maps", __name__)

_GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
_PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
_MAX_RESULTS = 5
_SEARCH_RADIUS_METRES = 3000


def _geocode_pincode(pincode: str, state: str, api_key: str) -> dict | None:
    """
    Geocode an Indian pincode to latitude/longitude coordinates.

    Args:
        pincode: 6-digit Indian postal code.
        state: State name to narrow geocoding results.
        api_key: Google Maps API key.

    Returns:
        Dict with 'lat' and 'lng' keys, or None if geocoding fails.
    """
    params = {
        "address": f"{pincode},{state},India",
        "key": api_key,
    }
    try:
        response = requests.get(_GEOCODE_URL, params=params, timeout=10)
        response.raise_for_status()
        geo_data: dict = response.json()
        if geo_data.get("status") != "OK" or not geo_data.get("results"):
            return None
        return geo_data["results"][0]["geometry"]["location"]
    except requests.RequestException as exc:
        logger.error("Geocoding request failed: %s", exc)
        return None


def _fetch_nearby_places(lat: float, lng: float, api_key: str) -> list[dict]:
    """
    Fetch nearby places that could serve as polling booths.

    Uses a keyword search for schools and community centres within
    ``_SEARCH_RADIUS_METRES`` of the given coordinates.

    Args:
        lat: Latitude of the search centre.
        lng: Longitude of the search centre.
        api_key: Google Maps API key.

    Returns:
        List of place dicts (name, address, lat, lng).
    """
    params = {
        "location": f"{lat},{lng}",
        "radius": _SEARCH_RADIUS_METRES,
        "keyword": "school|community center|polling",
        "key": api_key,
    }
    try:
        response = requests.get(_PLACES_URL, params=params, timeout=10)
        response.raise_for_status()
        places_data: dict = response.json()
    except requests.RequestException as exc:
        logger.error("Places API request failed: %s", exc)
        return []

    results: list[dict] = []
    for place in places_data.get("results", [])[:_MAX_RESULTS]:
        results.append(
            {
                "name": place.get("name", "Unknown"),
                "address": place.get("vicinity", ""),
                "lat": place["geometry"]["location"]["lat"],
                "lng": place["geometry"]["location"]["lng"],
                "distance": "~ 1-3 km",
            }
        )
    return results


@maps_bp.route("/find-booths", methods=["POST"])
def find_booths():
    """
    Find nearby polling booth candidates for a given pincode.

    Accepts JSON: {pincode: str, state: str}
    Returns JSON: {center: {lat, lng}, booths: list}

    Returns:
        200 with booth data on success.
        400 if API key is missing, input is invalid, or location is not found.
        500 on unexpected server error.
    """
    api_key: str | None = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return (
            jsonify(
                {
                    "error": (
                        "Maps API key missing. "
                        "Please visit eci.gov.in to find your booth."
                    )
                }
            ),
            400,
        )

    data: dict = request.get_json(silent=True) or {}
    pincode: str = str(data.get("pincode", "")).strip()[:10]
    state: str = str(data.get("state", "")).strip()[:100]

    if not pincode or not state:
        return jsonify({"error": "Both pincode and state are required."}), 400

    # Basic pincode format validation (India: 6 digits)
    if not pincode.isdigit() or len(pincode) != 6:
        return jsonify({"error": "Please enter a valid 6-digit pincode."}), 400

    try:
        location = _geocode_pincode(pincode, state, api_key)
        if location is None:
            return jsonify({"error": "Could not find location for this pincode."}), 400

        lat: float = location["lat"]
        lng: float = location["lng"]
        booths: list[dict] = _fetch_nearby_places(lat, lng, api_key)

        return jsonify({"center": {"lat": lat, "lng": lng}, "booths": booths})

    except Exception as exc:
        logger.error("Unexpected error in find_booths: %s", exc)
        return jsonify({"error": "Failed to fetch booths. Please try again."}), 500