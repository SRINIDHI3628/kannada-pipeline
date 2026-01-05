from flask import Blueprint, request, jsonify
from math import radians, sin, cos, sqrt, atan2
from models import GovernmentOffice

map_bp = Blueprint("map_bp", __name__)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

@map_bp.route("/offices/nearby", methods=["GET"])
def nearby_offices():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)

    if lat is None or lon is None:
        return jsonify({"error": "lat and lon are required"}), 400

    offices = GovernmentOffice.query.all()
    result = []

    for office in offices:
        distance = haversine(lat, lon, office.latitude, office.longitude)
        if distance <= 5:  # 5 km radius
            result.append({
                "name": office.office_name,
                "department": office.department,
                "latitude": office.latitude,
                "longitude": office.longitude,
                "distance_km": round(distance, 2)
            })

    return jsonify(result), 200
