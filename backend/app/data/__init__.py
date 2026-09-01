"""
JALNETRA Demo Data — Hilly Village Alpha
=========================================
DEMO / SYNTHETIC DATA
This is a fictional demonstration region for hackathon purposes.
All coordinates, names, and values are synthetic.

Region: Hilly village in Uttarakhand-like terrain (~30.5°N, 78.5°E)
Features: River, streams, settlements, roads, bridges, shelters, sensors
"""

from datetime import datetime, timedelta

# ===========================================================================
# Region Center & Bounds
# ===========================================================================

REGION_CENTER = {"lat": 30.4500, "lon": 78.0800}

REGION_BOUNDS = {
    "north": 30.4600,
    "south": 30.4400,
    "east": 78.0950,
    "west": 78.0650,
}

REGION_INFO = {
    "region_id": "region-hilly-village-alpha",
    "name": "Hilly Village Alpha",
    "description": "DEMO / SYNTHETIC DATA — Fictional hilly village region for demonstration. "
                   "Inspired by vulnerable Himalayan settlements with river valleys, steep slopes, "
                   "and limited road access.",
    "center": REGION_CENTER,
    "bounds": REGION_BOUNDS,
    "elevation_range_m": {"min": 820, "max": 1450},
    "population_estimate": 2800,
    "note": "DEMO / SYNTHETIC DATA — Not a real location",
}


# ===========================================================================
# Zones
# ===========================================================================

ZONES = [
    {
        "zone_id": "zone-riverside",
        "name": "Riverside Settlement",
        "description": "Low-lying area along the main river — highest flood risk",
        "center": {"lat": 30.4480, "lon": 78.0780},
        "elevation_m": 840,
        "slope_degrees": 5,
        "drainage_quality": "poor",
        "population": 650,
        "vulnerability": "high",
        "geojson": {
            "type": "Feature",
            "properties": {"zone_id": "zone-riverside", "name": "Riverside Settlement"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[78.0740, 30.4460], [78.0820, 30.4460],
                                 [78.0820, 30.4500], [78.0740, 30.4500],
                                 [78.0740, 30.4460]]],
            },
        },
    },
    {
        "zone_id": "zone-hillside",
        "name": "Hillside Colony",
        "description": "Steep terrain above the river — landslide risk",
        "center": {"lat": 30.4540, "lon": 78.0750},
        "elevation_m": 1100,
        "slope_degrees": 35,
        "drainage_quality": "moderate",
        "population": 420,
        "vulnerability": "high",
        "geojson": {
            "type": "Feature",
            "properties": {"zone_id": "zone-hillside", "name": "Hillside Colony"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[78.0710, 30.4520], [78.0790, 30.4520],
                                 [78.0790, 30.4560], [78.0710, 30.4560],
                                 [78.0710, 30.4520]]],
            },
        },
    },
    {
        "zone_id": "zone-valley",
        "name": "Valley Market",
        "description": "Commercial area in the valley — moderate risk",
        "center": {"lat": 30.4500, "lon": 78.0830},
        "elevation_m": 880,
        "slope_degrees": 10,
        "drainage_quality": "moderate",
        "population": 800,
        "vulnerability": "moderate",
        "geojson": {
            "type": "Feature",
            "properties": {"zone_id": "zone-valley", "name": "Valley Market"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[78.0800, 30.4480], [78.0880, 30.4480],
                                 [78.0880, 30.4520], [78.0800, 30.4520],
                                 [78.0800, 30.4480]]],
            },
        },
    },
    {
        "zone_id": "zone-plateau",
        "name": "Upper Plateau",
        "description": "Higher ground — safest area, hosts main shelter",
        "center": {"lat": 30.4560, "lon": 78.0860},
        "elevation_m": 1250,
        "slope_degrees": 8,
        "drainage_quality": "good",
        "population": 530,
        "vulnerability": "low",
        "geojson": {
            "type": "Feature",
            "properties": {"zone_id": "zone-plateau", "name": "Upper Plateau"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[78.0830, 30.4540], [78.0910, 30.4540],
                                 [78.0910, 30.4580], [78.0830, 30.4580],
                                 [78.0830, 30.4540]]],
            },
        },
    },
    {
        "zone_id": "zone-bridge",
        "name": "Bridge Junction",
        "description": "Critical river crossing — access bottleneck",
        "center": {"lat": 30.4490, "lon": 78.0810},
        "elevation_m": 850,
        "slope_degrees": 3,
        "drainage_quality": "poor",
        "population": 400,
        "vulnerability": "critical",
        "geojson": {
            "type": "Feature",
            "properties": {"zone_id": "zone-bridge", "name": "Bridge Junction"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[78.0795, 30.4480], [78.0825, 30.4480],
                                 [78.0825, 30.4500], [78.0795, 30.4500],
                                 [78.0795, 30.4480]]],
            },
        },
    },
]


# ===========================================================================
# River & Streams (GeoJSON)
# ===========================================================================

WATER_FEATURES = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"id": "river-main", "name": "Main River", "type": "river", "width_m": 15},
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [78.0650, 30.4490], [78.0720, 30.4485], [78.0780, 30.4480],
                    [78.0810, 30.4490], [78.0860, 30.4485], [78.0950, 30.4480],
                ],
            },
        },
        {
            "type": "Feature",
            "properties": {"id": "stream-north", "name": "North Stream", "type": "stream", "width_m": 4},
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [78.0730, 30.4570], [78.0750, 30.4540], [78.0770, 30.4510],
                    [78.0780, 30.4490],
                ],
            },
        },
        {
            "type": "Feature",
            "properties": {"id": "stream-east", "name": "East Stream", "type": "stream", "width_m": 3},
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [78.0870, 30.4560], [78.0860, 30.4530], [78.0855, 30.4500],
                    [78.0860, 30.4485],
                ],
            },
        },
    ],
}


# ===========================================================================
# Sensors
# ===========================================================================

SENSORS = [
    {
        "sensor_id": "sensor-rain-01",
        "name": "Rainfall Gauge Alpha",
        "type": "rainfall",
        "location": {"lat": 30.4530, "lon": 78.0760},
        "elevation_m": 1050,
        "zone_id": "zone-hillside",
        "status": "ONLINE",
        "battery_percent": 92,
        "signal_strength": 85,
    },
    {
        "sensor_id": "sensor-rain-02",
        "name": "Rainfall Gauge Beta",
        "type": "rainfall",
        "location": {"lat": 30.4480, "lon": 78.0840},
        "elevation_m": 870,
        "zone_id": "zone-valley",
        "status": "ONLINE",
        "battery_percent": 88,
        "signal_strength": 78,
    },
    {
        "sensor_id": "sensor-water-01",
        "name": "River Level Station A",
        "type": "water_level",
        "location": {"lat": 30.4485, "lon": 78.0780},
        "elevation_m": 835,
        "zone_id": "zone-riverside",
        "status": "ONLINE",
        "battery_percent": 95,
        "signal_strength": 90,
    },
    {
        "sensor_id": "sensor-water-02",
        "name": "Bridge Level Sensor",
        "type": "water_level",
        "location": {"lat": 30.4490, "lon": 78.0810},
        "elevation_m": 845,
        "zone_id": "zone-bridge",
        "status": "ONLINE",
        "battery_percent": 79,
        "signal_strength": 72,
    },
    {
        "sensor_id": "sensor-soil-01",
        "name": "Hillside Soil Probe",
        "type": "soil_moisture",
        "location": {"lat": 30.4545, "lon": 78.0740},
        "elevation_m": 1120,
        "zone_id": "zone-hillside",
        "status": "ONLINE",
        "battery_percent": 84,
        "signal_strength": 68,
    },
    {
        "sensor_id": "sensor-soil-02",
        "name": "Valley Soil Probe",
        "type": "soil_moisture",
        "location": {"lat": 30.4500, "lon": 78.0850},
        "elevation_m": 890,
        "zone_id": "zone-valley",
        "status": "ONLINE",
        "battery_percent": 91,
        "signal_strength": 82,
    },
    {
        "sensor_id": "sensor-temp-01",
        "name": "Weather Station Alpha",
        "type": "temperature",
        "location": {"lat": 30.4560, "lon": 78.0860},
        "elevation_m": 1260,
        "zone_id": "zone-plateau",
        "status": "ONLINE",
        "battery_percent": 97,
        "signal_strength": 91,
    },
    {
        "sensor_id": "sensor-humidity-01",
        "name": "Humidity Sensor Alpha",
        "type": "humidity",
        "location": {"lat": 30.4555, "lon": 78.0855},
        "elevation_m": 1255,
        "zone_id": "zone-plateau",
        "status": "ONLINE",
        "battery_percent": 96,
        "signal_strength": 89,
    },
]


# ===========================================================================
# Roads
# ===========================================================================

ROADS = [
    {
        "road_id": "road-main-highway",
        "name": "Main Highway (NH-58 Link)",
        "type": "highway",
        "status": "SAFE",
        "length_km": 3.2,
        "travel_time_minutes": 8,
        "elevation_m": 950,
        "flood_vulnerable": False,
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [78.0650, 30.4520], [78.0720, 30.4530], [78.0800, 30.4540],
                [78.0880, 30.4550], [78.0950, 30.4560],
            ],
        },
    },
    {
        "road_id": "road-riverside",
        "name": "Riverside Road",
        "type": "local",
        "status": "SAFE",
        "length_km": 1.8,
        "travel_time_minutes": 5,
        "elevation_m": 845,
        "flood_vulnerable": True,
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [78.0740, 30.4470], [78.0780, 30.4475], [78.0820, 30.4480],
                [78.0860, 30.4475],
            ],
        },
    },
    {
        "road_id": "road-bridge",
        "name": "Old Bridge Road",
        "type": "bridge",
        "status": "SAFE",
        "length_km": 0.4,
        "travel_time_minutes": 2,
        "elevation_m": 848,
        "flood_vulnerable": True,
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [78.0800, 30.4495], [78.0810, 30.4490], [78.0820, 30.4495],
            ],
        },
    },
    {
        "road_id": "road-hillside",
        "name": "Hillside Track",
        "type": "local",
        "status": "SAFE",
        "length_km": 2.1,
        "travel_time_minutes": 7,
        "elevation_m": 1080,
        "flood_vulnerable": False,
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [78.0720, 30.4530], [78.0740, 30.4540], [78.0760, 30.4550],
                [78.0780, 30.4555],
            ],
        },
    },
    {
        "road_id": "road-plateau",
        "name": "Plateau Connector",
        "type": "local",
        "status": "SAFE",
        "length_km": 1.5,
        "travel_time_minutes": 4,
        "elevation_m": 1200,
        "flood_vulnerable": False,
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [78.0800, 30.4540], [78.0840, 30.4550], [78.0870, 30.4560],
            ],
        },
    },
    {
        "road_id": "road-valley-market",
        "name": "Valley Market Road",
        "type": "local",
        "status": "SAFE",
        "length_km": 1.2,
        "travel_time_minutes": 3,
        "elevation_m": 875,
        "flood_vulnerable": True,
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [78.0810, 30.4500], [78.0830, 30.4505], [78.0860, 30.4500],
            ],
        },
    },
]


# ===========================================================================
# Shelters
# ===========================================================================

SHELTERS = [
    {
        "shelter_id": "shelter-school",
        "name": "Government School (Shelter A)",
        "type": "school",
        "capacity": 200,
        "occupancy": 0,
        "medical": False,
        "water": True,
        "power": True,
        "accessibility": "accessible",
        "elevation_m": 1220,
        "location": {"lat": 30.4555, "lon": 78.0850},
        "zone_id": "zone-plateau",
        "access_roads": ["road-plateau", "road-main-highway"],
    },
    {
        "shelter_id": "shelter-community",
        "name": "Community Hall (Shelter B)",
        "type": "community_hall",
        "capacity": 150,
        "occupancy": 0,
        "medical": True,
        "water": True,
        "power": True,
        "accessibility": "accessible",
        "elevation_m": 960,
        "location": {"lat": 30.4530, "lon": 78.0800},
        "zone_id": "zone-valley",
        "access_roads": ["road-main-highway", "road-hillside"],
    },
    {
        "shelter_id": "shelter-temple",
        "name": "Hill Temple (Shelter C)",
        "type": "religious",
        "capacity": 80,
        "occupancy": 0,
        "medical": False,
        "water": True,
        "power": False,
        "accessibility": "limited",
        "elevation_m": 1350,
        "location": {"lat": 30.4570, "lon": 78.0730},
        "zone_id": "zone-hillside",
        "access_roads": ["road-hillside"],
    },
]


# ===========================================================================
# Hospital / Critical Infrastructure
# ===========================================================================

CRITICAL_INFRASTRUCTURE = [
    {
        "id": "hospital-phc",
        "name": "Primary Health Center",
        "type": "hospital",
        "location": {"lat": 30.4550, "lon": 78.0845},
        "elevation_m": 1210,
        "capacity": 30,
        "zone_id": "zone-plateau",
        "access_roads": ["road-plateau"],
    },
    {
        "id": "infra-power",
        "name": "Power Substation",
        "type": "power",
        "location": {"lat": 30.4510, "lon": 78.0870},
        "elevation_m": 900,
        "zone_id": "zone-valley",
        "access_roads": ["road-valley-market"],
    },
    {
        "id": "infra-telecom",
        "name": "Telecom Tower",
        "type": "telecom",
        "location": {"lat": 30.4565, "lon": 78.0870},
        "elevation_m": 1280,
        "zone_id": "zone-plateau",
        "access_roads": ["road-plateau"],
    },
    {
        "id": "infra-bridge-old",
        "name": "Old River Bridge",
        "type": "bridge",
        "location": {"lat": 30.4490, "lon": 78.0810},
        "elevation_m": 848,
        "zone_id": "zone-bridge",
        "access_roads": ["road-bridge"],
    },
]


# ===========================================================================
# Historical Events (DEMO / SYNTHETIC)
# ===========================================================================

HISTORICAL_EVENTS = [
    {
        "event_id": "event-2024-monsoon",
        "name": "2024 Monsoon Flash Flood",
        "date": "2024-08-15",
        "type": "flash_flood",
        "max_rainfall_mm": 180,
        "max_water_level_m": 6.2,
        "affected_zones": ["zone-riverside", "zone-bridge"],
        "roads_closed": ["road-riverside", "road-bridge"],
        "population_affected": 450,
        "duration_hours": 8,
        "note": "DEMO / SYNTHETIC DATA",
    },
    {
        "event_id": "event-2023-landslide",
        "name": "2023 Landslide-Flood Cascade",
        "date": "2023-09-02",
        "type": "landslide_cascade",
        "max_rainfall_mm": 220,
        "max_water_level_m": 5.8,
        "affected_zones": ["zone-hillside", "zone-riverside", "zone-bridge"],
        "roads_closed": ["road-hillside", "road-riverside", "road-bridge"],
        "population_affected": 680,
        "duration_hours": 14,
        "note": "DEMO / SYNTHETIC DATA",
    },
    {
        "event_id": "event-2022-near-miss",
        "name": "2022 Near Miss Event",
        "date": "2022-07-20",
        "type": "near_miss",
        "max_rainfall_mm": 140,
        "max_water_level_m": 4.5,
        "affected_zones": ["zone-riverside"],
        "roads_closed": [],
        "population_affected": 0,
        "duration_hours": 4,
        "note": "DEMO / SYNTHETIC DATA — High risk detected but major flooding did not occur",
    },
]


# ===========================================================================
# Demo Users
# ===========================================================================

DEMO_USERS = [
    {
        "user_id": "user-admin",
        "username": "admin",
        "password": "jalnetra2026",
        "name": "System Admin",
        "role": "ADMIN",
    },
    {
        "user_id": "user-authority",
        "username": "authority",
        "password": "jalnetra2026",
        "name": "District Authority",
        "role": "AUTHORITY",
    },
    {
        "user_id": "user-responder",
        "username": "responder",
        "password": "jalnetra2026",
        "name": "Field Responder Alpha",
        "role": "RESPONDER",
    },
    {
        "user_id": "user-citizen",
        "username": "citizen",
        "password": "jalnetra2026",
        "name": "Demo Citizen",
        "role": "CITIZEN",
    },
]


# ===========================================================================
# Responders
# ===========================================================================

RESPONDERS = [
    {
        "responder_id": "responder-alpha",
        "name": "Rescue Team Alpha",
        "type": "rescue",
        "status": "AVAILABLE",
        "location": {"lat": 30.4540, "lon": 78.0830},
        "capabilities": ["rescue", "medical", "evacuation"],
    },
    {
        "responder_id": "responder-beta",
        "name": "Rescue Team Beta",
        "type": "rescue",
        "status": "AVAILABLE",
        "location": {"lat": 30.4520, "lon": 78.0780},
        "capabilities": ["rescue", "evacuation"],
    },
]


# ===========================================================================
# Default Sensor Readings (NORMAL conditions)
# ===========================================================================

def get_normal_readings():
    """Return baseline 'normal' sensor readings for demo."""
    now = datetime.utcnow()
    return {
        "sensor-rain-01": {
            "timestamp": now, "rainfall_mm": 2.5, "battery_percent": 92, "signal_strength": 85,
        },
        "sensor-rain-02": {
            "timestamp": now, "rainfall_mm": 3.1, "battery_percent": 88, "signal_strength": 78,
        },
        "sensor-water-01": {
            "timestamp": now, "water_level_m": 2.1, "battery_percent": 95, "signal_strength": 90,
        },
        "sensor-water-02": {
            "timestamp": now, "water_level_m": 1.8, "battery_percent": 79, "signal_strength": 72,
        },
        "sensor-soil-01": {
            "timestamp": now, "soil_moisture_percent": 45.0, "battery_percent": 84, "signal_strength": 68,
        },
        "sensor-soil-02": {
            "timestamp": now, "soil_moisture_percent": 42.0, "battery_percent": 91, "signal_strength": 82,
        },
        "sensor-temp-01": {
            "timestamp": now, "temperature_c": 22.5, "humidity_percent": 65.0,
            "battery_percent": 97, "signal_strength": 91,
        },
        "sensor-humidity-01": {
            "timestamp": now, "humidity_percent": 68.0, "battery_percent": 96, "signal_strength": 89,
        },
    }


# ===========================================================================
# Complete Region GeoJSON for Frontend Map
# ===========================================================================

def get_region_geojson():
    """Build complete GeoJSON FeatureCollection for the demo region."""
    features = []

    # Region boundary
    features.append({
        "type": "Feature",
        "properties": {"id": "region-boundary", "name": "Hilly Village Alpha", "type": "boundary"},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[78.0650, 30.4400], [78.0950, 30.4400],
                             [78.0950, 30.4600], [78.0650, 30.4600],
                             [78.0650, 30.4400]]],
        },
    })

    # Zones
    for zone in ZONES:
        features.append(zone["geojson"])

    # Water features
    for f in WATER_FEATURES["features"]:
        features.append(f)

    # Roads
    for road in ROADS:
        features.append({
            "type": "Feature",
            "properties": {
                "id": road["road_id"], "name": road["name"],
                "type": "road", "road_type": road["type"],
                "status": road["status"], "vulnerable": road["flood_vulnerable"],
            },
            "geometry": road["geometry"],
        })

    # Sensors
    for sensor in SENSORS:
        features.append({
            "type": "Feature",
            "properties": {
                "id": sensor["sensor_id"], "name": sensor["name"],
                "type": "sensor", "sensor_type": sensor["type"],
                "zone_id": sensor["zone_id"],
            },
            "geometry": {
                "type": "Point",
                "coordinates": [sensor["location"]["lon"], sensor["location"]["lat"]],
            },
        })

    # Shelters
    for shelter in SHELTERS:
        features.append({
            "type": "Feature",
            "properties": {
                "id": shelter["shelter_id"], "name": shelter["name"],
                "type": "shelter", "capacity": shelter["capacity"],
                "medical": shelter["medical"],
            },
            "geometry": {
                "type": "Point",
                "coordinates": [shelter["location"]["lon"], shelter["location"]["lat"]],
            },
        })

    # Critical infrastructure
    for infra in CRITICAL_INFRASTRUCTURE:
        features.append({
            "type": "Feature",
            "properties": {
                "id": infra["id"], "name": infra["name"],
                "type": infra["type"],
            },
            "geometry": {
                "type": "Point",
                "coordinates": [infra["location"]["lon"], infra["location"]["lat"]],
            },
        })

    return {"type": "FeatureCollection", "features": features}
