import reflex as rx

from murkelhausen_app_v2.backend.owm import get_weather_data_muelheim, OWMOneCall
from murkelhausen_app_v2.templates.template import template


class WeatherState(rx.State):
    owm_weather: OWMOneCall = None
    foo: str

    def update_weather(self):
        self.owm_weather = get_weather_data_muelheim()


@template(route="/weather", title="Wetter", on_load=WeatherState.update_weather)
def weather_page() -> rx.Component:
    return rx.vstack(
        rx.heading("Wetter"),
        rx.text(WeatherState.owm_weather.current.weather[0].description),
            )
