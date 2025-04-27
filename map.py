from flask import Blueprint, request, jsonify
import requests

map_bp=Blueprint('map',__name__)

@map_bp.route('',methods=['GET'])
def get_nearby_hospitals():
    """Fetch nearby hospitals using OpenStreetMap Overpass API."""
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if not lat or not lon:
        return jsonify({"error": "Latitude and longitude are required"}), 400

    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    node
      [amenity=hospital]
      (around:5000,{lat},{lon});
    out tags center;
    """

    try:
        response = requests.get(overpass_url, params={'data': query})
        response.raise_for_status()
        data = response.json()

        hospitals = []
        for element in data.get("elements", []):
            tags = element.get("tags", {})
            hospitals.append({
                "name": tags.get("name", "Unnamed Hospital"),
                "lat": element.get("lat"),
                "lon": element.get("lon"),
                "address": {
                    "street": tags.get("addr:street", ""),
                    "city": tags.get("addr:city", ""),
                    "postcode": tags.get("addr:postcode", "")
                },
                "details": {
                    "phone": tags.get("phone", "N/A"),
                    "website": tags.get("website", "N/A"),
                    "operator": tags.get("operator", "N/A"),
                    "speciality": tags.get("healthcare:speciality", "General")
                }
            })

        return jsonify(hospitals)
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500