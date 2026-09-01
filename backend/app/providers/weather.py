"""
JALNETRA Weather Provider
=========================
WeatherProvider ABC with Demo and Real implementations.
The application functions without an external weather API.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
from typing import List, Optional
import math

from app.schemas import ForecastPoint, ForecastResponse, DataFreshness


class WeatherProvider(ABC):
    """Abstract base for weather data providers."""

    @abstractmethod
    async def get_forecast(self, lat: float, lon: float, hours: int = 24) -> ForecastResponse:
        pass

    @abstractmethod
    async def get_current(self, lat: float, lon: float) -> dict:
        pass


class DemoWeatherProvider(WeatherProvider):
    """
    Deterministic demo weather provider.
    Generates realistic monsoon-season weather without external API.
    """

    def __init__(self):
        self._rainfall_multiplier = 1.0  # Adjustable for demo scenarios
        self._base_rainfall = 5.0

    async def get_forecast(self, lat: float = 30.45, lon: float = 78.08, hours: int = 24) -> ForecastResponse:
        now = datetime.now(timezone.utc)
        forecast_points = []

        for h in range(hours):
            t = now + timedelta(hours=h)
            hour_of_day = (t.hour + 5) % 24  # IST offset

            # Realistic diurnal pattern for monsoon
            base_rain = self._base_rainfall * self._rainfall_multiplier

            # Afternoon thunderstorm pattern
            if 14 <= hour_of_day <= 20:
                rain = base_rain * (2.0 + math.sin((hour_of_day - 14) * math.pi / 6))
            elif 2 <= hour_of_day <= 6:
                rain = base_rain * 1.5  # Early morning convection
            else:
                rain = base_rain * 0.5

            # Temperature (cooler at altitude, typical hill station)
            temp = 18 + 6 * math.sin((hour_of_day - 6) * math.pi / 12)

            # Humidity (high in monsoon)
            humidity = 75 + 15 * math.sin((hour_of_day - 2) * math.pi / 12)

            forecast_points.append(ForecastPoint(
                timestamp=t,
                rainfall_mm=round(max(0, rain), 1),
                temperature_c=round(temp, 1),
                humidity_percent=round(min(98, max(50, humidity)), 1),
                wind_speed_kmh=round(8 + 5 * math.sin(h * 0.5), 1),
                cloud_cover_percent=round(min(100, 60 + rain * 2), 0),
                description=self._weather_description(rain),
            ))

        return ForecastResponse(
            region="Hilly Village Alpha",
            forecast=forecast_points,
            source="demo",
            freshness=DataFreshness(
                timestamp=now, age_seconds=0, quality="demo", source="demo_weather_provider"
            ),
        )

    async def get_current(self, lat: float = 30.45, lon: float = 78.08) -> dict:
        now = datetime.now(timezone.utc)
        hour_of_day = (now.hour + 5) % 24

        rain = self._base_rainfall * self._rainfall_multiplier
        if 14 <= hour_of_day <= 20:
            rain *= 2.0

        return {
            "timestamp": now.isoformat(),
            "rainfall_mm": round(rain, 1),
            "temperature_c": round(18 + 4 * math.sin((hour_of_day - 6) * math.pi / 12), 1),
            "humidity_percent": round(75 + 10 * math.sin((hour_of_day - 2) * math.pi / 12), 1),
            "wind_speed_kmh": round(10 + 3 * math.sin(hour_of_day * 0.5), 1),
            "pressure_hpa": 920,
            "source": "demo",
        }

    def set_rainfall_multiplier(self, multiplier: float):
        """Adjust rainfall intensity for demo scenarios."""
        self._rainfall_multiplier = max(0.0, multiplier)

    def set_base_rainfall(self, mm: float):
        self._base_rainfall = max(0.0, mm)

    def _weather_description(self, rain_mm: float) -> str:
        if rain_mm > 50:
            return "Very heavy rain"
        elif rain_mm > 30:
            return "Heavy rain"
        elif rain_mm > 15:
            return "Moderate rain"
        elif rain_mm > 5:
            return "Light rain"
        elif rain_mm > 1:
            return "Drizzle"
        else:
            return "Cloudy"


class RealWeatherProvider(WeatherProvider):
    """
    Real weather API provider (stub for external integration).
    Falls back to DemoWeatherProvider on failure.
    """

    def __init__(self, api_url: str = None, api_key: str = None):
        self._api_url = api_url
        self._api_key = api_key
        self._fallback = DemoWeatherProvider()

    async def get_forecast(self, lat: float = 30.45, lon: float = 78.08, hours: int = 24) -> ForecastResponse:
        # TODO: Implement real weather API call (e.g., OpenMeteo, IMD)
        # For now, fall back to demo
        response = await self._fallback.get_forecast(lat, lon, hours)
        response.source = "real_weather_fallback"
        return response

    async def get_current(self, lat: float = 30.45, lon: float = 78.08) -> dict:
        return await self._fallback.get_current(lat, lon)


def get_weather_provider(use_real: bool = False, api_url: str = None, api_key: str = None) -> WeatherProvider:
    """Factory: returns appropriate weather provider based on config."""
    if use_real and api_url:
        return RealWeatherProvider(api_url=api_url, api_key=api_key)
    return DemoWeatherProvider()
