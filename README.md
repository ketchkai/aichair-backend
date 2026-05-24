# aichair-backend

Backend for an accessibility-focused routing app in Bellingham, WA.

## stack

- FastAPI (REST API)
- Supabase (Postgres + PostGIS)
- Unweaver (routing engine)
- Docker Compose

## quick start

```bash
git clone git@github.com:ketchkai/aichair-backend.git
cd aichair-backend
cp .env.example .env
# make sure you fill in real values in .env
docker compose up --build
```

## endpoints

All endpoints return JSON. Requests with a body must send `Content-Type: application/json`.
Coordinates outside the Bellingham bbox (`48.68, -122.55, 48.82, -122.35`) are rejected with `422`.

### GET /health

Liveness check. No request body.

**Response 200**
```json
{ "status": "ok" }
```

**Example**
```bash
curl http://localhost:8001/health
```

### POST /obstacles

Report an obstacle.

**Request body**
```json
{
  "lat": 48.75,
  "lon": -122.48,
  "obstacle_type": "Pothole",
  "description": "Deep, near curb cut"
}
```

**Response 201**
```json
{
  "id": 42,
  "lat": 48.75,
  "lon": -122.48,
  "obstacle_type": "Pothole",
  "description": "Deep, near curb cut",
  "created_at": "2026-05-23T19:42:00.123456+00:00"
}
```

**Errors**
- `422` — validation failure (bad coordinates, missing fields, length violations)

**Example**
```bash
curl -X POST http://localhost:8001/obstacles \
  -H "Content-Type: application/json" \
  -d '{"lat":48.75,"lon":-122.48,"obstacle_type":"Pothole","description":"Deep, near curb cut"}'
```

### POST /route

Compute a route between two points. Returns the route as line segments, plus any reported obstacles within 25m of the route.

**Request body**
```json
{
  "lat1": 48.75,
  "lon1": -122.48,
  "lat2": 48.76,
  "lon2": -122.47,
  "profile": "powered_wheelchair"
}
```

**Response 200**
```json
{
  "segments": [
    { "coordinates": [[-122.48, 48.75], [-122.477, 48.753]] },
    { "coordinates": [[-122.477, 48.753], [-122.473, 48.757]] }
  ],
  "obstacles": [
    {
      "id": 42,
      "lat": 48.754,
      "lon": -122.476,
      "obstacle_type": "Pothole",
      "description": "Deep, near curb cut"
    }
  ]
}
```

**Errors**
- `404` — no route found between the points
- `422` — validation failure, or invalid waypoint (e.g. nowhere near a road)
- `502` — routing engine returned an unexpected response
- `503` — routing engine has no graph loaded

**Example**
```bash
curl -X POST http://localhost:8001/route \
  -H "Content-Type: application/json" \
  -d '{"lat1":48.75,"lon1":-122.48,"lat2":48.76,"lon2":-122.47,"profile":"powered_wheelchair"}'
```