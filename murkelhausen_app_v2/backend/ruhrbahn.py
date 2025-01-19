import logging

import reflex as rx
import requests
from cachetools import TTLCache, cached

from murkelhausen_app_v2.backend.ruhrbahn_DepartureModel import DepartureModel
from murkelhausen_app_v2.backend.ruhrbahn_StationModel import StationModel
from murkelhausen_app_v2.config import config

logger = logging.getLogger(__name__)


URLS = {
    "stations": "https://ifa.ruhrbahn.de/stations",
    "routes": "https://ifa.ruhrbahn.de/routes",
    "locations": "https://ifa.ruhrbahn.de/locations",
    "stopFinder": "https://ifa.ruhrbahn.de/stopFinder/",
    "departure": "https://ifa.ruhrbahn.de/departure/",
    "trafficinfos": "https://ifa.ruhrbahn.de/trafficinfos",
    "tripRequest": "https://ifa.ruhrbahn.de/tripRequest/20015062/20015065/20230806/21:25/dep",
}


class Departure(rx.Base):
    richtung: str
    departure_time: str
    delay: int
    line: str
    platform: str


@cached(cache=TTLCache(maxsize=1, ttl=60))  # 1 minute
def get_departure_data(station_id: str, _: int = None) -> DepartureModel:
    json_data = requests.get(
        URLS["departure"] + station_id, timeout=config.ruhrbahn.request_timeout
    ).json()
    logger.info(
        f"Retrieved departure data from the Ruhrbahn API for station {station_id}."
    )
    return DepartureModel(**json_data)


@cached(cache=TTLCache(maxsize=1, ttl=60))  # 1 minute
def get_stations(_: int = None) -> StationModel:
    json_data = requests.get(
        URLS["stations"], timeout=config.ruhrbahn.request_timeout
    ).json()
    data = {"stations": json_data}
    logger.info("Retrieved stations data from the Ruhrbahn API.")
    return StationModel(**data)


def get_lierberg_departure_data() -> list[Departure]:
    # TODO(arkadius): move to config
    station = "Lierberg"
    station_id = get_stations().get_station_id(station, "Mülheim")
    logger.info(f"Retrieved station id {station_id} for station {station}.")

    raw_departure_data = get_departure_data(station_id)
    raw_departures = raw_departure_data.get_departure_list()

    departures = []
    for raw_departure in raw_departures:
        departures.append(
            Departure(
                richtung=raw_departure.richtung,
                departure_time=raw_departure.planned_departure_time,
                delay=raw_departure.delay,
                line=raw_departure.servingLine.number,
                platform=raw_departure.platform,
            )
        )

    return departures
