from dataclasses import dataclass

import reflex as rx

from murkelhausen_app_v2.backend.owm import get_weather_data_muelheim, OWMOneCall
from murkelhausen_app_v2.templates.template import template


@dataclass
class Forecast:
    temp: str
    feels_like: str


class WeatherState(rx.State):
    owm_weather: OWMOneCall | None = None
    error_message: str = ""

    def update_weather(self):
        self.owm_weather, self.error_message = get_weather_data_muelheim()

    @rx.var(cache=True)
    def current_temp(self) -> str:
        return self.owm_weather.current.temp_unit

    @rx.var(cache=True)
    def current_feels_like(self) -> str:
        return self.owm_weather.current.feels_like_unit

    @rx.var(cache=True)
    def today_forecast(self) -> Forecast:
        return Forecast(
            temp=self.owm_weather.daily[0].temp_unit,
            feels_like=self.owm_weather.daily[0].feels_like_unit,
        )

    @rx.var(cache=True)
    def tomorrow_forecast(self) -> Forecast:
        return Forecast(
            temp=self.owm_weather.daily[1].temp_unit,
            feels_like=self.owm_weather.daily[1].feels_like_unit,
        )


@template(route="/weather", title="Wetter", on_load=WeatherState.update_weather)
def weather_page() -> rx.Component:
    return rx.vstack(
        rx.heading("Wetter"),
        rx.cond(
            WeatherState.error_message != "",
            rx.text(WeatherState.error_message),
            rx.text(WeatherState.owm_weather.current.weather[0].description),
        ),
    )
