from math import asin, cos, radians, sin, sqrt


def haversine_km(a: dict, b: dict) -> float:
    """Local straight-line screening only; never represents real driving time."""
    lat1, lon1, lat2, lon2 = map(radians, [a["lat"], a["lng"], b["lat"], b["lng"]])
    delta_lat, delta_lon = lat2 - lat1, lon2 - lon1
    value = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    return round(2 * 6371 * asin(sqrt(value)), 2)
