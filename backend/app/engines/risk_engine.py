"""
JALNETRA Risk Engine
====================
Hybrid risk assessment: rule-based thresholds + ML probability estimation.
Produces explainable, transparent risk predictions.

Model: jalnetra-risk-v1.0-demo
Note: Demo thresholds are NOT official disaster thresholds.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import numpy as np

from app.config import settings
from app.engines.confidence_engine import confidence_engine
from app.schemas import (
    RiskLevel, RiskTrend, ConfidenceLevel,
    RiskDriver, ZoneRisk, RiskResponse, DataFreshness,
)
from app.data import ZONES


class RiskEngine:
    """
    Transparent hybrid risk assessment engine.

    Layer 1: Threshold/rule-based classification
    Layer 2: ML probability estimation (XGBoost-compatible, using logistic for demo)

    Outputs:
        risk_probability, risk_level, confidence, uncertainty,
        estimated_onset, trend, risk_drivers, model_version
    """

    MODEL_VERSION = "jalnetra-risk-v1.0-demo"

    def __init__(self):
        # Configurable thresholds (from settings)
        self._thresholds = {
            RiskLevel.AWARENESS: settings.RISK_THRESHOLD_AWARENESS,
            RiskLevel.WATCH: settings.RISK_THRESHOLD_WATCH,
            RiskLevel.WARNING: settings.RISK_THRESHOLD_WARNING,
            RiskLevel.EVACUATE: settings.RISK_THRESHOLD_EVACUATE,
            RiskLevel.CRITICAL: settings.RISK_THRESHOLD_CRITICAL,
        }

        # Feature weights for rule-based scoring
        self._weights = {
            "rainfall_intensity": 0.20,
            "accumulated_rainfall": 0.10,
            "soil_moisture": 0.15,
            "water_level": 0.20,
            "water_level_trend": 0.10,
            "slope_factor": 0.08,
            "drainage_factor": 0.07,
            "historical_frequency": 0.05,
            "forecast_rainfall": 0.05,
        }

        # Risk history for trend calculation
        self._risk_history: Dict[str, List[Tuple[datetime, float]]] = {}

    def assess_zone(
        self,
        zone_id: str,
        rainfall_mm: float = 0.0,
        accumulated_rainfall_mm: float = 0.0,
        soil_moisture_percent: float = 40.0,
        water_level_m: float = 2.0,
        water_level_previous_m: Optional[float] = None,
        slope_degrees: float = 10.0,
        drainage_quality: str = "moderate",
        historical_flood_frequency: float = 0.3,
        forecast_rainfall_mm: float = 0.0,
        total_sensors: int = 8,
        online_sensors: int = 8,
        avg_sensor_health: float = 85.0,
        avg_data_age_seconds: float = 15.0,
        weather_available: bool = True,
    ) -> ZoneRisk:
        """Assess risk for a single zone."""

        # --- Normalize features to 0-1 scale ---
        features = {}

        # Rainfall intensity (0-200mm → 0-1)
        features["rainfall_intensity"] = min(rainfall_mm / 100.0, 1.0)

        # Accumulated rainfall (0-300mm → 0-1)
        features["accumulated_rainfall"] = min(accumulated_rainfall_mm / 200.0, 1.0)

        # Soil moisture (30-100% → 0-1, higher = worse)
        features["soil_moisture"] = max(0, min((soil_moisture_percent - 30) / 70.0, 1.0))

        # Water level (normal ~2m, danger ~6m)
        features["water_level"] = max(0, min((water_level_m - 1.5) / 4.5, 1.0))

        # Water level trend
        if water_level_previous_m is not None:
            delta = water_level_m - water_level_previous_m
            features["water_level_trend"] = max(0, min(delta / 2.0, 1.0))
        else:
            features["water_level_trend"] = 0.0

        # Slope factor (steeper = more risk for landslide)
        features["slope_factor"] = min(slope_degrees / 45.0, 1.0)

        # Drainage quality
        drainage_map = {"good": 0.1, "moderate": 0.4, "poor": 0.8}
        features["drainage_factor"] = drainage_map.get(drainage_quality, 0.5)

        # Historical frequency
        features["historical_frequency"] = min(historical_flood_frequency, 1.0)

        # Forecast rainfall
        features["forecast_rainfall"] = min(forecast_rainfall_mm / 100.0, 1.0)

        # --- Layer 1: Weighted rule-based score ---
        rule_score = sum(
            self._weights.get(k, 0) * v for k, v in features.items()
        )
        rule_score = max(0.0, min(1.0, rule_score))

        # --- Layer 2: Simple logistic model (demo substitute for XGBoost) ---
        # Uses a sigmoid to smooth the rule-based score
        feature_array = np.array([features.get(k, 0) for k in self._weights.keys()])
        weight_array = np.array(list(self._weights.values()))

        # Logistic combination with nonlinearity
        z = np.dot(feature_array, weight_array) * 6 - 2  # Scale to sigmoid range
        ml_score = float(1 / (1 + np.exp(-z)))

        # --- Combined probability (average of both layers) ---
        risk_probability = 0.5 * rule_score + 0.5 * ml_score
        risk_probability = max(0.0, min(1.0, risk_probability))

        # --- Risk level from thresholds ---
        risk_level = self._probability_to_level(risk_probability)

        # --- Confidence ---
        model_uncertainty = abs(rule_score - ml_score) * 0.5 + 0.05
        conf_level, conf_score, conf_reason = confidence_engine.compute(
            total_sensors=total_sensors,
            online_sensors=online_sensors,
            avg_health_score=avg_sensor_health,
            avg_data_age_seconds=avg_data_age_seconds,
            weather_available=weather_available,
            model_uncertainty=model_uncertainty,
        )

        # --- Trend ---
        trend = self._calculate_trend(zone_id, risk_probability)

        # --- Risk drivers ---
        risk_drivers = self._identify_drivers(features)

        # --- Estimated onset ---
        estimated_onset = self._estimate_onset(risk_probability, features)

        # --- Cascade risk (landslide-flood) ---
        cascade_risk, cascade_factors = self._assess_cascade(features)

        # --- Zone metadata ---
        zone_data = next((z for z in ZONES if z["zone_id"] == zone_id), None)
        zone_name = zone_data["name"] if zone_data else zone_id

        return ZoneRisk(
            zone_id=zone_id,
            zone_name=zone_name,
            risk_probability=round(risk_probability, 4),
            risk_level=risk_level,
            confidence=ConfidenceLevel(conf_level),
            confidence_score=round(conf_score, 3),
            confidence_reason=conf_reason,
            uncertainty=round(model_uncertainty, 3),
            estimated_onset_minutes=estimated_onset,
            trend=trend,
            risk_drivers=risk_drivers,
            model_version=self.MODEL_VERSION,
            timestamp=datetime.now(timezone.utc),
            is_demo=settings.DEMO_MODE,
            cascade_risk=round(cascade_risk, 3) if cascade_risk else None,
            cascade_factors=cascade_factors,
        )

    def assess_all_zones(self, sensor_data: Dict, weather_data: Optional[Dict] = None) -> RiskResponse:
        """Assess risk for all zones using current sensor data."""
        zone_risks = []

        for zone in ZONES:
            zone_id = zone["zone_id"]

            # Extract relevant sensor data for this zone
            zone_sensors = self._get_zone_sensor_data(zone_id, sensor_data)

            risk = self.assess_zone(
                zone_id=zone_id,
                rainfall_mm=zone_sensors.get("rainfall_mm", 2.0),
                accumulated_rainfall_mm=zone_sensors.get("accumulated_rainfall_mm", 5.0),
                soil_moisture_percent=zone_sensors.get("soil_moisture_percent", 42.0),
                water_level_m=zone_sensors.get("water_level_m", 2.0),
                water_level_previous_m=zone_sensors.get("water_level_previous_m"),
                slope_degrees=zone.get("slope_degrees", 10),
                drainage_quality=zone.get("drainage_quality", "moderate"),
                historical_flood_frequency=0.3,
                forecast_rainfall_mm=weather_data.get("forecast_rainfall_mm", 0) if weather_data else 0,
                total_sensors=zone_sensors.get("total_sensors", 8),
                online_sensors=zone_sensors.get("online_sensors", 8),
                avg_sensor_health=zone_sensors.get("avg_health", 85.0),
                avg_data_age_seconds=zone_sensors.get("avg_age_seconds", 15.0),
                weather_available=weather_data is not None,
            )
            zone_risks.append(risk)

        # Overall risk = highest zone risk
        overall_risk = max(zone_risks, key=lambda z: z.risk_probability)

        # Overall trend
        trends_order = {
            RiskTrend.DECREASING: 0,
            RiskTrend.STABLE: 1,
            RiskTrend.INCREASING: 2,
            RiskTrend.RAPIDLY_INCREASING: 3,
        }
        overall_trend = max(zone_risks, key=lambda z: trends_order.get(z.trend, 1)).trend

        now = datetime.now(timezone.utc)
        return RiskResponse(
            region="Hilly Village Alpha",
            zones=zone_risks,
            overall_risk=overall_risk.risk_level,
            overall_trend=overall_trend,
            model_version=self.MODEL_VERSION,
            timestamp=now,
            freshness=DataFreshness(
                timestamp=now, age_seconds=0, quality="good", source="demo"
            ),
        )

    def _probability_to_level(self, prob: float) -> RiskLevel:
        if prob >= self._thresholds[RiskLevel.CRITICAL]:
            return RiskLevel.CRITICAL
        elif prob >= self._thresholds[RiskLevel.EVACUATE]:
            return RiskLevel.EVACUATE
        elif prob >= self._thresholds[RiskLevel.WARNING]:
            return RiskLevel.WARNING
        elif prob >= self._thresholds[RiskLevel.WATCH]:
            return RiskLevel.WATCH
        elif prob >= self._thresholds[RiskLevel.AWARENESS]:
            return RiskLevel.AWARENESS
        else:
            return RiskLevel.NORMAL

    def _calculate_trend(self, zone_id: str, current_prob: float) -> RiskTrend:
        now = datetime.now(timezone.utc)
        history = self._risk_history.get(zone_id, [])
        history.append((now, current_prob))

        # Keep last 10 entries
        if len(history) > 10:
            history = history[-10:]
        self._risk_history[zone_id] = history

        if len(history) < 2:
            return RiskTrend.STABLE

        # Compare with 3 readings ago or earliest
        compare_idx = max(0, len(history) - 4)
        delta = current_prob - history[compare_idx][1]

        if delta > 0.15:
            return RiskTrend.RAPIDLY_INCREASING
        elif delta > 0.05:
            return RiskTrend.INCREASING
        elif delta < -0.05:
            return RiskTrend.DECREASING
        else:
            return RiskTrend.STABLE

    def _identify_drivers(self, features: Dict[str, float]) -> List[RiskDriver]:
        drivers = []
        driver_descriptions = {
            "rainfall_intensity": ("rainfall_intensity_increasing", "Heavy rainfall detected"),
            "accumulated_rainfall": ("accumulated_rainfall_high", "Significant cumulative rainfall"),
            "soil_moisture": ("soil_saturation_high", "Soil approaching saturation"),
            "water_level": ("water_level_rising", "Water level elevated above normal"),
            "water_level_trend": ("water_level_trend_up", "Water level rising rapidly"),
            "slope_factor": ("terrain_susceptibility_high", "Steep terrain increases risk"),
            "drainage_factor": ("poor_drainage", "Drainage capacity limited"),
            "historical_frequency": ("historical_risk_area", "Historical flood-prone area"),
            "forecast_rainfall": ("forecast_rainfall_expected", "Additional rainfall forecast"),
        }

        for feature_key, (factor_id, description) in driver_descriptions.items():
            value = features.get(feature_key, 0)
            if value > 0.4:
                severity = "high" if value > 0.7 else "moderate"
                drivers.append(RiskDriver(
                    factor=factor_id,
                    description=description,
                    severity=severity,
                ))

        return drivers

    def _estimate_onset(self, prob: float, features: Dict[str, float]) -> Optional[float]:
        """Estimate minutes until hazard onset. Very simplified."""
        if prob < 0.3:
            return None

        # Higher current risk = sooner onset
        # Base estimate inversely proportional to risk
        base_minutes = max(5, 60 * (1 - prob))

        # Adjust for water level trend (rising = sooner)
        trend_factor = 1.0 - features.get("water_level_trend", 0) * 0.5

        onset = base_minutes * trend_factor
        return round(max(5, min(120, onset)), 1)

    def _assess_cascade(self, features: Dict[str, float]) -> Tuple[Optional[float], List[str]]:
        """
        Assess landslide-flood cascade risk.
        Chain: Heavy Rain → Soil Saturation → Slope Instability → Drainage Block → Flash Flood
        """
        factors = []
        cascade_score = 0.0

        soil = features.get("soil_moisture", 0)
        slope = features.get("slope_factor", 0)
        rain = features.get("rainfall_intensity", 0)
        drainage = features.get("drainage_factor", 0)

        if soil > 0.6:
            factors.append("soil_saturation_high")
            cascade_score += 0.25

        if slope > 0.5:
            factors.append("slope_instability_risk")
            cascade_score += 0.25

        if rain > 0.5:
            factors.append("heavy_rainfall_trigger")
            cascade_score += 0.25

        if drainage > 0.5:
            factors.append("drainage_obstruction_risk")
            cascade_score += 0.25

        if cascade_score < 0.25:
            return None, []

        return min(cascade_score, 1.0), factors

    def _get_zone_sensor_data(self, zone_id: str, sensor_data: Dict) -> Dict:
        """Extract and aggregate sensor data relevant to a zone."""
        from app.data import SENSORS

        zone_sensor_ids = [s["sensor_id"] for s in SENSORS if s.get("zone_id") == zone_id]
        all_sensor_ids = [s["sensor_id"] for s in SENSORS]

        rainfall_values = []
        water_level_values = []
        soil_values = []
        online_count = 0
        total_count = len(zone_sensor_ids) if zone_sensor_ids else len(all_sensor_ids)

        target_ids = zone_sensor_ids if zone_sensor_ids else all_sensor_ids

        for sid in target_ids:
            data = sensor_data.get(sid, {})
            if data:
                online_count += 1
                if "rainfall_mm" in data:
                    rainfall_values.append(data["rainfall_mm"])
                if "water_level_m" in data:
                    water_level_values.append(data["water_level_m"])
                if "soil_moisture_percent" in data:
                    soil_values.append(data["soil_moisture_percent"])

        return {
            "rainfall_mm": max(rainfall_values) if rainfall_values else 2.0,
            "accumulated_rainfall_mm": sum(rainfall_values) * 2 if rainfall_values else 5.0,
            "water_level_m": max(water_level_values) if water_level_values else 2.0,
            "water_level_previous_m": None,
            "soil_moisture_percent": max(soil_values) if soil_values else 42.0,
            "total_sensors": max(total_count, 1),
            "online_sensors": online_count,
            "avg_health": 85.0,
            "avg_age_seconds": 15.0,
        }

    def reset(self):
        """Reset risk history (used by demo reset)."""
        self._risk_history.clear()


# Singleton
risk_engine = RiskEngine()
