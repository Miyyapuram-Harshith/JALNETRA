"""
JALNETRA Confidence Engine
Computes confidence score based on sensor coverage, health, freshness,
weather availability, and model uncertainty.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple


class ConfidenceEngine:
    """
    Assesses the confidence level of predictions based on
    the quality and availability of input data.
    """

    def __init__(self):
        self._weights = {
            "sensor_coverage": 0.30,
            "sensor_health": 0.25,
            "data_freshness": 0.20,
            "weather_availability": 0.15,
            "model_uncertainty": 0.10,
        }

    def compute(
        self,
        total_sensors: int,
        online_sensors: int,
        avg_health_score: float,
        avg_data_age_seconds: float,
        weather_available: bool,
        model_uncertainty: float = 0.1,
    ) -> Tuple[str, float, str]:
        """
        Compute confidence level.

        Returns:
            (level, score, reason) — e.g. ("HIGH", 0.85, "All sensors reporting normally.")
        """
        reasons = []

        # --- Sensor Coverage ---
        if total_sensors > 0:
            coverage_ratio = online_sensors / total_sensors
        else:
            coverage_ratio = 0.0
        coverage_score = coverage_ratio

        if coverage_ratio < 0.5:
            offline_count = total_sensors - online_sensors
            reasons.append(
                f"Confidence reduced: {offline_count} of {total_sensors} local sensors are offline"
            )
        elif coverage_ratio < 0.8:
            offline_count = total_sensors - online_sensors
            reasons.append(f"{offline_count} sensor(s) offline")

        # --- Sensor Health ---
        health_score = avg_health_score / 100.0
        if health_score < 0.5:
            reasons.append("Sensor health is degraded")

        # --- Data Freshness ---
        if avg_data_age_seconds < 30:
            freshness_score = 1.0
        elif avg_data_age_seconds < 120:
            freshness_score = 0.8
        elif avg_data_age_seconds < 300:
            freshness_score = 0.6
            reasons.append("Some sensor data is older than 2 minutes")
        elif avg_data_age_seconds < 600:
            freshness_score = 0.3
            reasons.append("Sensor data may be stale (>5 minutes old)")
        else:
            freshness_score = 0.1
            reasons.append("WARNING: Sensor data is significantly stale")

        # --- Weather Availability ---
        weather_score = 1.0 if weather_available else 0.3
        if not weather_available:
            reasons.append("Weather forecast unavailable — using demo data")

        # --- Model Uncertainty ---
        uncertainty_score = max(0, 1.0 - model_uncertainty)
        if model_uncertainty > 0.4:
            reasons.append("Model uncertainty is elevated")

        # --- Weighted Score ---
        score = (
            self._weights["sensor_coverage"] * coverage_score
            + self._weights["sensor_health"] * health_score
            + self._weights["data_freshness"] * freshness_score
            + self._weights["weather_availability"] * weather_score
            + self._weights["model_uncertainty"] * uncertainty_score
        )

        score = max(0.0, min(1.0, score))

        # --- Level ---
        if score >= 0.7:
            level = "HIGH"
        elif score >= 0.4:
            level = "MEDIUM"
        else:
            level = "LOW"

        # --- Reason ---
        if not reasons:
            reason = "All data sources reporting normally."
        else:
            reason = "; ".join(reasons) + "."

        return level, round(score, 3), reason


# Singleton
confidence_engine = ConfidenceEngine()
