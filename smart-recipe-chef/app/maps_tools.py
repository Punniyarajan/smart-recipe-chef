import json
import os
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

def get_maps_api_key() -> str:
    key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not key:
        raise ValueError("GOOGLE_MAPS_API_KEY environment variable is missing in .env")
    return key

def geocode_address(address: str) -> Dict[str, Any]:
    """Converts a street address or location name into geographic coordinates (latitude and longitude).

    Args:
        address: Street address, neighborhood, or city name (e.g. '1600 Amphitheatre Pkwy, Mountain View, CA' or 'San Francisco').

    Returns:
        A dictionary containing the formatted address and coordinate location ({'lat': float, 'lng': float}).
    """
    try:
        api_key = get_maps_api_key()
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={urllib.parse.quote(address)}&key={api_key}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            if data.get("status") != "OK" or not data.get("results"):
                return {"status": "error", "message": f"Geocoding failed for '{address}': {data.get('status')}"}

            result = data["results"][0]
            loc = result["geometry"]["location"]
            return {
                "status": "success",
                "address": result.get("formatted_address"),
                "location": {"latitude": loc.get("lat"), "longitude": loc.get("lng")},
            }
    except Exception as e:
        return {"status": "error", "message": f"Geocoding exception: {str(e)}"}

def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "grocery_store",
    radius_meters: float = 3000.0,
) -> Dict[str, Any]:
    """Finds nearby places of a specific type (e.g., 'grocery_store', 'supermarket', 'bakery') around coordinates.

    Args:
        latitude: Latitude coordinate.
        longitude: Longitude coordinate.
        place_type: Type of place to search for (e.g., 'grocery_store', 'supermarket', 'bakery', 'restaurant').
        radius_meters: Search radius in meters (default 3000m).

    Returns:
        A dictionary containing a list of nearby places with name, address, and location coordinates.
    """
    try:
        api_key = get_maps_api_key()
        url = "https://places.googleapis.com/v1/places:searchNearby"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.primaryType",
        }
        body = json.dumps({
            "includedTypes": [place_type],
            "maxResultCount": 5,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                    "radius": float(radius_meters),
                }
            }
        }).encode("utf-8")

        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
            raw_places = data.get("places", [])

            places = []
            for p in raw_places:
                disp_name = p.get("displayName", {}).get("text") if isinstance(p.get("displayName"), dict) else p.get("displayName")
                loc = p.get("location", {})
                places.append({
                    "name": disp_name,
                    "address": p.get("formattedAddress"),
                    "location": {"latitude": loc.get("latitude"), "longitude": loc.get("longitude")},
                })

            return {
                "status": "success",
                "count": len(places),
                "place_type": place_type,
                "places": places,
            }
    except Exception as e:
        return {"status": "error", "message": f"Places search exception: {str(e)}"}
