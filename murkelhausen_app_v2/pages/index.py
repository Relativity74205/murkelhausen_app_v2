import reflex as rx

from murkelhausen_app_v2 import styles
from murkelhausen_app_v2.pages.weather import WeatherState
from murkelhausen_app_v2.templates.template import template


@template(route="/", title="Startpage", on_load=WeatherState.update_weather)
def index() -> rx.Component:
    return rx.vstack(
        rx.heading("Murkelhausen V2"),
        rx.card(
            rx.flex(
                rx.text("Heute"),
                rx.card(
                    # show_appointment_list(),
                ),
                rx.card(
                    rx.data_list.root(
                        rx.data_list.item(
                            rx.data_list.label("Temperatur", color_scheme="tomato"),
                            rx.data_list.value(
                                f"{WeatherState.owm_weather.current.temp} °C"
                            ),
                            align="center",
                        ),
                        rx.data_list.item(
                            rx.data_list.label("Temperatur gefühlt"),
                            rx.data_list.value(
                                f"{WeatherState.owm_weather.current.feels_like} °C"
                            ),
                            align="end",
                        ),
                        size="3",
                    ),
                    width="100%",
                ),
                direction="column",
                spacing="4",
            ),
            box_shadow=styles.box_shadow_style,
            size="3",
            width="100%",
        ),
        rx.card(
            rx.flex(
                rx.text("Morgen"),
                rx.card(
                    rx.text("..."),
                    size="3",
                    width="100%",
                ),
                direction="column",
                spacing="4",
            ),
            box_shadow=styles.box_shadow_style,
            size="3",
            width="100%",
        ),
        rx.card(
            rx.flex(
                rx.text("Diese Woche"),
                rx.card(
                    rx.text("..."),
                    size="3",
                    width="100%",
                ),
                direction="column",
                spacing="4",
            ),
            box_shadow=styles.box_shadow_style,
            size="3",
            width="100%",
        ),
        width="100%",
    )
