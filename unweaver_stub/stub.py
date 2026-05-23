"""
local dev stub for Unweaver

mimics Unweaver's /shortest_path/<profile>.json endpoint so I can
develop the API layer without a running Unweaver instance

Kai Ketcham, WWU CS, 2026
"""

import math

from flask import Flask, request, jsonify


app = Flask(__name__)


def _interpolate_edges(lon1, lat1, lon2, lat2):
    waypoints = []
    for t in (1 / 3, 2 / 3):
        lon = lon1 + t * (lon2 - lon1)
        lat = lat1 + t * (lat2 - lat1)
        waypoints.append((lon, lat))
    
    points = [(lon1, lat1), waypoints[0], waypoints[1], (lon2, lat2)]
    edges = []
    for i in range(len(points) - 1):
        a = points[i]
        b = points[i + 1]
        edges.append({
            "geometry": {
                "type": "LineString",
                "coordinates": [[a[0], a[1]], [b[0], b[1]]],
            },
            "properties": {},
        })
    return edges


def _point_feature(lon, lat):
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": {},
    }


@app.route("/shortest_path/<profile>.json", methods=["GET"])
def shortest_path(profile):
    try:
        lon1 = float(request.args["lon1"])
        lat1 = float(request.args["lat1"])
        lon2 = float(request.args["lon2"])
        lat2 = float(request.args["lat2"])
    except (KeyError, ValueError):
        return jsonify({"error": "missing or invalid query parameters"}), 400
    
    edges = _interpolate_edges(lon1, lat1, lon2, lat2)
    total_cost = math.sqrt((lon2 - lon1) ** 2 + (lat2 - lat1) ** 2)

    return jsonify({
        "status": "Ok",
        "origin": _point_feature(lon1, lat1),
        "destination": _point_feature(lon2, lat2),
        "total_cost": total_cost,
        "edges": edges,
    })


if __name__ == "__main__":
    print("Starting Unweaver stub on port 8000 for local dev")
    app.run(host="0.0.0.0", port=8000, debug=False)
