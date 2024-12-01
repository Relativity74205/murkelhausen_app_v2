"""
API Documentations:
https://openweathermap.org/api/one-call-3
https://openweathermap.org/current

name = "Mülheim"
gps_lat = 51.4300
gps_lon = 6.8264
"""

import os
from dataclasses import dataclass
from logging import getLogger

import requests
from cachetools import TTLCache, cached

from murkelhausen_app_v2.backend.owm_models import OWMOneCall

log = getLogger(__name__)


@dataclass
class City:
    name: str
    gps_lat: float
    gps_lon: float


@dataclass
class OWMConfig:
    url_weather: str
    url_onecall: str
    units: str
    api_key: str


# TODO: move to config
MUELHEIM = City(name="Mülheim", gps_lat=51.4300, gps_lon=6.8264)


def query_one_call_api(city: City, owm_config: OWMConfig) -> OWMOneCall:
    data = _query_owm(
        owm_config.url_onecall, city, owm_config.api_key, owm_config.units
    )
    return OWMOneCall(**data)


def query_weather(city: City, owm_config: OWMConfig) -> dict:
    return _query_owm(
        owm_config.url_weather, city, owm_config.api_key, owm_config.units
    )


def _query_owm(url: str, city: City, api_key: str, units: str) -> dict:
    query_params: dict = {
        "lat": city.gps_lat,
        "lon": city.gps_lon,
        "appid": api_key,
        "units": units,
        "lang": "de",
    }
    # TODO: move timeout to config
    r = requests.get(url, params=query_params, timeout=2)

    if r.status_code == 200:
        return_dict: dict = r.json()
        return return_dict
    elif r.status_code == 401:
        raise RuntimeError(f"Authentication error, {api_key=}.")
    else:
        raise RuntimeError(
            f"Query to openweatherapi one call api returned non 200 status code for city {city.name} with {api_key=}: "
            f"status_code: {r.status_code}"
            f"response_text: {r.text}"
        )


@cached(cache=TTLCache(maxsize=1, ttl=120))  # 2 minutes
def get_weather_data_muelheim() -> tuple[OWMOneCall | None, str | None]:
    # TODO: move to config
    owm_config = OWMConfig(
        url_weather="https://api.openweathermap.org/data/2.5/weather",
        url_onecall="https://api.openweathermap.org/data/3.0/onecall",
        units="metric",
        api_key=os.environ.get("OPENWEATHERMAP_API_KEY"),
    )

    try:
        data = query_one_call_api(MUELHEIM, owm_config)
    except Exception as e:
        return None, str(e)

    return data, ""
