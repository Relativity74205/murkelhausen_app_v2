from __future__ import annotations

from datetime import date, datetime

import reflex as rx
from pydantic import Field
from pydantic.v1 import BaseModel

from murkelhausen_app_v2.backend.owm_functions import (
    _get_moon_phase_string,
    _get_uv_index_category,
    _get_wind_direction,
    _unix_timestamp_to_met_hour,
    _unix_timestamp_to_met_timestamp,
)


class WeatherItem(rx.Base):
    id: int  # https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2
    main: str
    description: str
    icon: str  # see https://openweathermap.org/weather-conditions#How-to-get-icon-URL


class Current(rx.Base):
    dt: int
    sunrise: int
    sunset: int
    temp: float
    feels_like: float
    pressure: int
    humidity: int
    dew_point: float
    uvi: float  # Current UV index
    clouds: int
    visibility: int
    wind_speed: float
    wind_deg: int
    rain: dict[str, float] | None = None
    snow: dict[str, float] | None = None
    weather: tuple[WeatherItem, ...]

    @property
    def temp_unit(self) -> str:
        return f"{self.temp:.1f} °C"

    @property
    def feels_like_unit(self) -> str:
        return f"{self.feels_like:.1f} °C"

    @property
    def timestamp(self) -> datetime:
        return datetime.fromtimestamp(self.dt)

    @property
    def pressure_unit(self) -> str:
        return f"{self.pressure} hPa"

    @property
    def humidity_unit(self) -> str:
        return f"{self.humidity} %"

    @property
    def dew_point_unit(self) -> str:
        return f"{self.dew_point:.1f} °C"

    @property
    def uvi_unit(self) -> str:
        return f"{self.uvi} ({_get_uv_index_category(self.uvi)})"

    @property
    def clouds_unit(self) -> str:
        return f"{self.clouds} %"

    @property
    def visibility_unit(self) -> str:
        return f"{self.visibility} m"

    @property
    def wind_speed_unit(self) -> str:
        return f"{self.wind_speed:.0f} m/s"

    @property
    def wind_direction(self) -> str:
        return _get_wind_direction(self.wind_deg)

    @property
    def sunrise_time(self) -> str:
        return _unix_timestamp_to_met_hour(self.sunrise)

    @property
    def sunset_time(self) -> str:
        return _unix_timestamp_to_met_hour(self.sunset)

    @property
    def rain_unit(self) -> str | None:
        return (
            f"{self.rain.get('1h', None):.1f} mm/h" if self.rain is not None else None
        )

    @property
    def snow_unit(self) -> str | None:
        return (
            f"{self.snow.get('1h', None):.1f} mm/h" if self.snow is not None else None
        )


class MinutelyItem(rx.Base):
    dt: int
    precipitation: float = Field(default=1)

    @property
    def time(self) -> str:
        return _unix_timestamp_to_met_hour(self.dt)

    @property
    def rain(self) -> float:
        return self.precipitation


class Rain(rx.Base):
    field_1h: float = Field(..., alias="1h")


class HourlyItem(rx.Base):
    dt: int
    temp: float
    feels_like: float
    pressure: int
    humidity: int
    dew_point: float
    uvi: float
    clouds: int
    visibility: int = Field(default=0)
    wind_speed: float
    wind_deg: int
    wind_gust: float
    weather: tuple[WeatherItem, ...]
    pop: float
    rain1h: Rain | None = Field(None, alias="rain")
    snow1h: Rain | None = Field(None, alias="snow")

    @property
    def time(self) -> str:
        return _unix_timestamp_to_met_hour(self.dt)

    @property
    def rain(self) -> float:
        if self.rain1h is None:
            return 0
        else:
            return self.rain1h.field_1h

    @property
    def snow(self) -> float:
        if self.snow1h is None:
            return 0
        else:
            return self.snow1h.field_1h


class Temp(rx.Base):
    min: float
    max: float
    day: float
    night: float
    eve: float
    morn: float

    @property
    def min_unit(self) -> str:
        return f"{self.min:.1f} °C"

    @property
    def max_unit(self) -> str:
        return f"{self.max:.1f} °C"

    @property
    def day_unit(self) -> str:
        return f"{self.day:.1f} °C"

    @property
    def night_unit(self) -> str:
        return f"{self.night:.1f} °C"

    @property
    def eve_unit(self) -> str:
        return f"{self.eve:.1f} °C"

    @property
    def morn_unit(self) -> str:
        return f"{self.morn:.1f} °C"


class FeelsLike(rx.Base):
    day: float
    night: float
    eve: float
    morn: float

    @property
    def day_unit(self) -> str:
        return f"{self.day:.1f} °C"

    @property
    def night_unit(self) -> str:
        return f"{self.night:.1f} °C"

    @property
    def eve_unit(self) -> str:
        return f"{self.eve:.1f} °C"

    @property
    def morn_unit(self) -> str:
        return f"{self.morn:.1f} °C"


class DailyItem(rx.Base):
    dt: int
    sunrise: int
    sunset: int
    moonrise: int
    moonset: int
    moon_phase: float
    summary: str
    temp: Temp
    feels_like: FeelsLike
    pressure: int
    humidity: int
    dew_point: float
    wind_speed: float
    wind_deg: int
    wind_gust: float
    weather: tuple[WeatherItem, ...]
    clouds: int
    pop: float
    rain_: float | None = Field(None, alias="rain")
    snow_: float | None = Field(None, alias="snow")
    uvi: float

    @property
    def temp_min(self) -> float:
        return min(self.temp.eve, self.temp.day, self.temp.morn)

    @property
    def temp_max(self) -> float:
        return max(self.temp.eve, self.temp.day, self.temp.morn)

    @property
    def rain(self) -> float:
        if self.rain_ is None:
            return 0
        else:
            return self.rain_

    @property
    def snow(self) -> float:
        if self.snow_ is None:
            return 0
        else:
            return self.snow_

    @property
    def temp_unit(self) -> str:
        return f"{self.temp.morn:.1f} °C -> {self.temp.day:.1f} °C -> {self.temp.eve:.1f} °C ({self.temp.night:.1f} °C Nachts)"

    @property
    def feels_like_unit(self) -> str:
        return f"{self.feels_like.morn:.1f} -> {self.feels_like.day:.1f} -> {self.feels_like.eve:.1f} °C ({self.feels_like.night:.1f} °C Nachts)"

    @property
    def pressure_unit(self) -> str:
        return f"{self.pressure} hPa"

    @property
    def humidity_unit(self) -> str:
        return f"{self.humidity} %"

    @property
    def dew_point_unit(self) -> str:
        return f"{self.dew_point:.1f} °C"

    @property
    def wind_speed_unit(self) -> str:
        return f"{self.wind_speed:.0f} m/s"

    @property
    def day(self) -> date:
        return date.fromtimestamp(self.dt)

    @property
    def sunrise_time(self) -> str:
        return _unix_timestamp_to_met_hour(self.sunrise)

    @property
    def sunset_time(self) -> str:
        return _unix_timestamp_to_met_hour(self.sunset)

    @property
    def moon_phase_string(self) -> str:
        return _get_moon_phase_string(self.moon_phase)

    @property
    def feels_like_today_min(self) -> float:
        return min(self.feels_like.__dict__.values())

    @property
    def feels_like_today_max(self) -> float:
        return max(self.feels_like.__dict__.values())

    @property
    def wind_direction(self) -> str:
        return _get_wind_direction(self.wind_deg)

    @property
    def clouds_unit(self) -> str:
        return f"{self.clouds} %"

    @property
    def pop_unit(self) -> str:
        return f"{self.pop * 100:.0f} %"

    @property
    def rain_unit(self) -> str | None:
        return f"{self.rain:.1f} mm/h" if self.rain is not None else None

    @property
    def snow_unit(self) -> str | None:
        return f"{self.snow:.1f} mm/h" if self.snow is not None else None


class Alert(rx.Base):
    sender_name: str
    event: str
    start: int
    end: int
    description: str
    tags: tuple[str, ...]

    @property
    def start_timestamp(self):
        return _unix_timestamp_to_met_timestamp(self.start)

    @property
    def end_timestamp(self):
        return _unix_timestamp_to_met_timestamp(self.end)


class OWMOneCall(BaseModel):
    lat: float
    lon: float
    timezone: str
    timezone_offset: int
    current: Current
    hourly: tuple[HourlyItem, ...]
    daily: tuple[DailyItem, ...]
    minutely: tuple[MinutelyItem, ...] = ()
    alerts: tuple[Alert, ...] = ()

    @property
    def current_pop_unit(self) -> str:
        return f"{self.hourly[0].pop * 100:.0f} %"

    @property
    def max_rain_minutely(self) -> float:
        max_rain = max([minute.rain for minute in self.minutely])
        if max_rain == 0:
            return 0.1
        else:
            return max_rain

    @property
    def max_snow_hourly(self) -> float:
        return max([hour.snow for hour in self.hourly])

    @property
    def max_snow_daily(self) -> float:
        return max([day.snow for day in self.daily])
