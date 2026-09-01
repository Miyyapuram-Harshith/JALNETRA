"""
JALNETRA Pydantic Schemas
All request/response models for the API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ===========================================================================
# Enums
# ===========================================================================

class RiskLevel(str, Enum):
    NORMAL = "NORMAL"
    AWARENESS = "AWARENESS"
    WATCH = "WATCH"
    WARNING = "WARNING"
    EVACUATE = "EVACUATE"
    CRITICAL = "CRITICAL"


class RiskTrend(str, Enum):
    STABLE = "STABLE"
    INCREASING = "INCREASING"
    RAPIDLY_INCREASING = "RAPIDLY_INCREASING"
    DECREASING = "DECREASING"


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class SensorType(str, Enum):
    RAINFALL = "rainfall"
    WATER_LEVEL = "water_level"
    SOIL_MOISTURE = "soil_moisture"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    BATTERY = "battery"
    SIGNAL = "signal"


class SensorStatus(str, Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    ANOMALY = "ANOMALY"
    BATTERY_LOW = "BATTERY_LOW"
    DEGRADED = "DEGRADED"


class SimulationScenario(str, Enum):
    NORMAL = "NORMAL"
    RISING = "RISING"
    HIGH = "HIGH"
    ANOMALY = "ANOMALY"
    OFFLINE = "OFFLINE"
    BATTERY_LOW = "BATTERY_LOW"


class RoadStatus(str, Enum):
    SAFE = "SAFE"
    THREATENED = "THREATENED"
    UNSAFE = "UNSAFE"
    CLOSED = "CLOSED"


class IncidentStatus(str, Enum):
    NEW = "NEW"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    ASSIGNED = "ASSIGNED"
    EN_ROUTE = "EN_ROUTE"
    ON_SCENE = "ON_SCENE"
    RESOLVED = "RESOLVED"


class IncidentPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AlertChannel(str, Enum):
    WHATSAPP = "WHATSAPP"
    PUSH = "PUSH"
    SMS = "SMS"
    VOICE = "VOICE"
    LOCAL_NODE = "LOCAL_NODE"


class AlertType(str, Enum):
    AWARENESS = "AWARENESS"
    WATCH = "WATCH"
    WARNING = "WARNING"
    EVACUATION_RECOMMENDED = "EVACUATION_RECOMMENDED"
    CRITICAL = "CRITICAL"
    ROUTE_UPDATED = "ROUTE_UPDATED"
    SHELTER_UPDATED = "SHELTER_UPDATED"
    ALERT_RESOLVED = "ALERT_RESOLVED"


class WhatsAppStatus(str, Enum):
    MESSAGE_PREPARED = "MESSAGE_PREPARED"
    SENT = "SENT"
    DELIVERY_CONFIRMED = "DELIVERY_CONFIRMED"
    FAILED = "FAILED"
    DEMO_MESSAGE_GENERATED = "DEMO_MESSAGE_GENERATED"


class NetworkStatus(str, Enum):
    ONLINE = "ONLINE"
    DEGRADED = "DEGRADED"
    OFFLINE = "OFFLINE"


class UserRole(str, Enum):
    CITIZEN = "CITIZEN"
    RESPONDER = "RESPONDER"
    AUTHORITY = "AUTHORITY"
    ADMIN = "ADMIN"


class DemoScenario(str, Enum):
    NORMAL = "NORMAL"
    WATCH = "WATCH"
    WARNING = "WARNING"
    FLASH_FLOOD = "FLASH_FLOOD"
    LANDSLIDE_CASCADE = "LANDSLIDE_CASCADE"
    SENSOR_FAILURE = "SENSOR_FAILURE"
    NETWORK_FAILURE = "NETWORK_FAILURE"
    NEAR_MISS = "NEAR_MISS"


# ===========================================================================
# Base Models
# ===========================================================================

class TimestampMixin(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow())


class DataFreshness(BaseModel):
    """Every data source exposes freshness metadata."""
    timestamp: datetime
    age_seconds: float
    quality: str = "good"
    source: str = "demo"


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Dict[str, Any] = {}
    timestamp: str
    request_id: str


# ===========================================================================
# Sensor Schemas
# ===========================================================================

class SensorReading(BaseModel):
    timestamp: datetime
    rainfall_mm: Optional[float] = None
    water_level_m: Optional[float] = None
    soil_moisture_percent: Optional[float] = None
    temperature_c: Optional[float] = None
    humidity_percent: Optional[float] = None
    battery_percent: Optional[float] = None
    signal_strength: Optional[float] = None


class SensorHealth(BaseModel):
    sensor_id: str
    name: str
    type: str
    status: SensorStatus
    health_score: float = Field(ge=0, le=100)
    quality_score: float = Field(ge=0, le=100)
    reliability_score: float = Field(ge=0, le=100)
    last_seen: Optional[datetime] = None
    battery_percent: Optional[float] = None
    signal_strength: Optional[float] = None
    anomalies: List[str] = []
    location: Dict[str, float] = {}
    freshness: Optional[DataFreshness] = None


class SensorSimulateRequest(BaseModel):
    scenario: SimulationScenario = SimulationScenario.NORMAL
    duration_seconds: int = 60


class SensorResponse(BaseModel):
    sensors: List[SensorHealth]
    total: int
    demo_mode: bool = True
    freshness: DataFreshness


# ===========================================================================
# Risk Schemas
# ===========================================================================

class RiskDriver(BaseModel):
    factor: str
    description: str
    severity: str = "moderate"


class ZoneRisk(BaseModel):
    zone_id: str
    zone_name: str
    risk_probability: float = Field(ge=0, le=1)
    risk_level: RiskLevel
    confidence: ConfidenceLevel
    confidence_score: float = Field(ge=0, le=1)
    confidence_reason: str = ""
    uncertainty: float = Field(ge=0, le=1)
    estimated_onset_minutes: Optional[float] = None
    trend: RiskTrend
    risk_drivers: List[RiskDriver] = []
    model_version: str = "jalnetra-risk-v1.0-demo"
    timestamp: datetime
    is_demo: bool = True
    cascade_risk: Optional[float] = None
    cascade_factors: List[str] = []


class RiskResponse(BaseModel):
    region: str
    zones: List[ZoneRisk]
    overall_risk: RiskLevel
    overall_trend: RiskTrend
    model_version: str
    timestamp: datetime
    freshness: DataFreshness


# ===========================================================================
# Forecast Schemas
# ===========================================================================

class ForecastPoint(BaseModel):
    timestamp: datetime
    rainfall_mm: float
    temperature_c: float
    humidity_percent: float
    wind_speed_kmh: float
    cloud_cover_percent: float
    description: str = ""


class ForecastResponse(BaseModel):
    region: str
    forecast: List[ForecastPoint]
    source: str = "demo"
    freshness: DataFreshness


# ===========================================================================
# Propagation Schemas
# ===========================================================================

class PropagationTimestep(BaseModel):
    time_offset_minutes: int
    hazard_geometry: Dict[str, Any]  # GeoJSON
    hazard_intensity: str  # low, moderate, high, extreme
    arrival_estimate_minutes: Optional[float] = None
    uncertainty_meters: float = 100.0
    affected_area_km2: float = 0.0


class PropagationResponse(BaseModel):
    timesteps: List[PropagationTimestep]
    model_version: str = "jalnetra-propagation-v1.0-prototype"
    model_note: str = "PROTOTYPE SIMPLIFIED MODEL — not validated for operational use"
    timestamp: datetime
    freshness: DataFreshness


# ===========================================================================
# Impact Schemas
# ===========================================================================

class AffectedFacility(BaseModel):
    id: str
    name: str
    type: str
    status: str
    hazard_arrival_minutes: Optional[float] = None
    location: Dict[str, float] = {}


class ImpactResponse(BaseModel):
    affected_area_km2: float
    affected_population_estimate: int
    population_note: str = "Modeled estimate based on aggregated data"
    threatened_roads: List[Dict[str, Any]] = []
    threatened_facilities: List[AffectedFacility] = []
    isolated_zones: List[str] = []
    timestamp: datetime
    freshness: DataFreshness


# ===========================================================================
# Route Schemas
# ===========================================================================

class RouteSegment(BaseModel):
    road_id: str
    road_name: str
    status: RoadStatus
    travel_time_minutes: float
    hazard_arrival_minutes: Optional[float] = None
    safety_margin_minutes: Optional[float] = None


class RouteOption(BaseModel):
    route_id: str
    route_name: str
    segments: List[RouteSegment]
    total_travel_time_minutes: float
    total_distance_km: float
    risk: RiskLevel
    confidence: ConfidenceLevel
    geometry: Optional[Dict[str, Any]] = None  # GeoJSON LineString


class SafeDepartureWindow(BaseModel):
    """Central JALNETRA intelligence feature."""
    safe_departure_window_minutes: float
    hazard_arrival_minutes: float
    travel_time_minutes: float
    safety_buffer_minutes: float
    confidence: ConfidenceLevel
    confidence_score: float
    uncertainty_minutes: float
    recommended_route: Optional[RouteOption] = None
    recommended_shelter: Optional[str] = None
    recommended_shelter_name: Optional[str] = None
    note: str = "MODELED ESTIMATE — not a guarantee of safety"
    timestamp: datetime


class RouteResponse(BaseModel):
    routes: List[RouteOption]
    safe_departure: SafeDepartureWindow
    timestamp: datetime
    freshness: DataFreshness


# ===========================================================================
# Road Schemas
# ===========================================================================

class RoadRisk(BaseModel):
    road_id: str
    road_name: str
    current_status: RoadStatus
    predicted_hazard_arrival_minutes: Optional[float] = None
    risk: RiskLevel
    confidence: ConfidenceLevel
    geometry: Optional[Dict[str, Any]] = None  # GeoJSON


class RoadResponse(BaseModel):
    roads: List[RoadRisk]
    timestamp: datetime
    freshness: DataFreshness


# ===========================================================================
# Shelter Schemas
# ===========================================================================

class ShelterInfo(BaseModel):
    shelter_id: str
    name: str
    capacity: int
    occupancy: int = 0
    available_capacity: int
    medical: bool = False
    water: bool = True
    power: bool = True
    accessibility: str = "accessible"
    current_access: RoadStatus = RoadStatus.SAFE
    predicted_access: RoadStatus = RoadStatus.SAFE
    travel_time_minutes: Optional[float] = None
    location: Dict[str, float] = {}
    rank: int = 1


class ShelterResponse(BaseModel):
    shelters: List[ShelterInfo]
    timestamp: datetime
    freshness: DataFreshness


# ===========================================================================
# Incident Schemas
# ===========================================================================

class SOSRequest(BaseModel):
    latitude: float
    longitude: float
    message: str = "Need assistance"
    people_count: int = 1
    medical_needed: bool = False
    phone: Optional[str] = None


class IncidentCreate(BaseModel):
    location_lat: float
    location_lon: float
    priority: IncidentPriority = IncidentPriority.HIGH
    severity: str = "moderate"
    people_affected: int = 1
    description: str = ""
    medical_needed: bool = False


class IncidentInfo(BaseModel):
    id: str
    location: Dict[str, float]
    priority: IncidentPriority
    severity: str
    people_affected: int
    hazard_arrival_minutes: Optional[float] = None
    recommended_route: Optional[str] = None
    status: IncidentStatus
    assigned_responder: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    source: str = "manual"


class IncidentUpdate(BaseModel):
    status: Optional[IncidentStatus] = None
    assigned_responder: Optional[str] = None
    priority: Optional[IncidentPriority] = None
    notes: Optional[str] = None


class IncidentResponse(BaseModel):
    incidents: List[IncidentInfo]
    total: int
    timestamp: datetime


# ===========================================================================
# Alert Schemas
# ===========================================================================

class AlertCreate(BaseModel):
    zone_id: str = "zone-riverside"
    alert_type: AlertType = AlertType.WARNING
    channel: AlertChannel = AlertChannel.WHATSAPP
    language: str = "en"
    recipient: Optional[str] = None


class WhatsAppAlertRequest(BaseModel):
    alert_id: Optional[str] = None
    recipient: Optional[str] = None
    zone_id: str = "zone-riverside"
    alert_type: AlertType = AlertType.WARNING
    language: str = "en"


class AlertInfo(BaseModel):
    alert_id: str
    zone_id: str
    alert_type: AlertType
    risk_level: RiskLevel
    channel: AlertChannel
    message: str
    status: WhatsAppStatus
    recipient: Optional[str] = None
    provider_response: Optional[Dict[str, Any]] = None
    created_at: datetime
    delivered_at: Optional[datetime] = None
    is_demo: bool = True


class AlertResponse(BaseModel):
    alerts: List[AlertInfo]
    total: int
    timestamp: datetime


# ===========================================================================
# Simulation Schemas
# ===========================================================================

class SimulationRequest(BaseModel):
    scenario: DemoScenario = DemoScenario.FLASH_FLOOD
    rainfall_intensity: float = 75.0
    soil_moisture: float = 84.0
    water_level: float = 4.8
    duration_minutes: int = 60


class SimulationTimelinePoint(BaseModel):
    time_offset_minutes: int
    rainfall_mm: float
    water_level_m: float
    soil_moisture_percent: float
    risk_level: RiskLevel
    risk_probability: float
    roads_threatened: int = 0
    shelters_affected: int = 0
    departure_window_minutes: Optional[float] = None


class SimulationResponse(BaseModel):
    simulation_id: str
    scenario: str
    timeline: List[SimulationTimelinePoint]
    peak_risk: RiskLevel
    peak_time_minutes: int
    total_duration_minutes: int
    timestamp: datetime
    note: str = "DEMO SIMULATION — synthetic data only"


# ===========================================================================
# System Schemas
# ===========================================================================

class HealthResponse(BaseModel):
    status: str = "healthy"
    api: str = "healthy"
    database: str = "healthy"
    model: str = "healthy"
    weather: str = "demo"
    whatsapp: str = "mock"
    iot: str = "simulator"
    realtime: str = "healthy"
    demo_mode: bool = True
    version: str = "1.0.0"
    uptime_seconds: float = 0


class ConnectivityReport(BaseModel):
    status: NetworkStatus = NetworkStatus.ONLINE
    latency_ms: Optional[float] = None


class SystemStatus(BaseModel):
    network: NetworkStatus
    last_verified_update: datetime
    sync_status: str = "synchronized"
    data_freshness: Dict[str, DataFreshness] = {}


# ===========================================================================
# Auth Schemas
# ===========================================================================

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    user_id: str
    name: str


class LoginRequest(BaseModel):
    username: str
    password: str


# ===========================================================================
# Region Schemas
# ===========================================================================

class RegionInfo(BaseModel):
    region_id: str
    name: str
    description: str
    center: Dict[str, float]
    bounds: Dict[str, float]
    geojson: Dict[str, Any]
    zones: List[Dict[str, Any]]
    sensors: List[Dict[str, Any]]
    roads: List[Dict[str, Any]]
    shelters: List[Dict[str, Any]]
    is_demo: bool = True
    note: str = "DEMO / SYNTHETIC DATA"


# ===========================================================================
# Audit Schemas
# ===========================================================================

class AuditEntry(BaseModel):
    id: str
    actor: str
    action: str
    timestamp: datetime
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    details: Dict[str, Any] = {}


class EventsResponse(BaseModel):
    events: List[AuditEntry]
    total: int
    timestamp: datetime
