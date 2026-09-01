"""
JALNETRA API — Forecast Routes
"""

from fastapi import APIRouter

from app.providers.weather import DemoWeatherProvider
from app.simulation.demo_controller import demo_controller
from app.schemas import ForecastResponse

router = APIRouter(prefix="/api", tags=["Forecast"])

# Weather provider (will be replaced by factory in main.py)
_weather_provider = DemoWeatherProvider()


@router.get("/forecast", response_model=ForecastResponse)
async def get_forecast():
    """
    Get weather forecast for the demo region.

    Returns hourly forecast with rainfall, temperature, humidity,
    wind speed, and cloud cover.
    """
    _weather_provider.set_rainfall_multiplier(demo_controller.rainfall_multiplier)
    _weather_provider.set_base_rainfall(demo_controller.base_rainfall_mm)
    return await _weather_provider.get_forecast()
