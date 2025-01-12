from datetime import date, timedelta

import reflex as rx
from babel.dates import format_date

from murkelhausen_app_v2 import styles
from murkelhausen_app_v2.backend.google_calendar import Appointment
from murkelhausen_app_v2.pages.calendar import CalendarState, show_appointment_table
from murkelhausen_app_v2.pages.weather import WeatherState, Forecast
from murkelhausen_app_v2.templates.template import template


@template(route="/", title="Startpage", on_load=WeatherState.update_weather)
def index() -> rx.Component:
    return rx.vstack(
        rx.heading("Murkelhausen V2"),
        rx.card(
            rx.text("Aktuell"),
            rx.card(
                rx.data_list.root(
                    rx.data_list.item(
                        rx.data_list.label("Temperatur", color_scheme="tomato"),
                        rx.data_list.value(WeatherState.current_temp),
                        align="center",
                    ),
                    rx.data_list.item(
                        rx.data_list.label("Temperatur gefühlt"),
                        rx.data_list.value(WeatherState.current_feels_like),
                        align="end",
                    ),
                    size="3",
                ),
                width="100%",
            ),
            box_shadow=styles.box_shadow_style,
            size="3",
            width="100%",
        ),
        rx.card(
            show_day_card(
                heading=f"Heute ({format_date(date.today(), format="dd.MM.yyyy (EEE)", locale="de_DE")})",
                appointments=CalendarState.todays_appointments,
                forecast=WeatherState.today_forecast,
            ),
            box_shadow=styles.box_shadow_style,
            size="3",
            width="100%",
        ),
        rx.card(
            show_day_card(
                heading=f"Morgen ({format_date(date.today() + timedelta(days=1), format="dd.MM.yyyy (EEE)", locale="de_DE")})",
                appointments=CalendarState.tomorrows_appointments,
                forecast=WeatherState.tomorrow_forecast,
            ),
            box_shadow=styles.box_shadow_style,
            size="3",
            width="100%",
        ),
        width="100%",
    )


def show_day_card(
    heading: str, appointments: list[Appointment], forecast: Forecast
) -> rx.Component:
    return rx.flex(
        rx.text(heading),
        rx.card(
            show_appointment_table(
                appointments,
                show_calendar_col=True,
                show_edit_col=False,
                show_delete_col=False,
                show_row_colors=False,
            ),
        ),
        rx.card(
            rx.data_list.root(
                rx.data_list.item(
                    rx.data_list.label("Temperatur", color_scheme="tomato"),
                    rx.data_list.value(forecast.temp),
                    align="center",
                ),
                rx.data_list.item(
                    rx.data_list.label("Temperatur gefühlt"),
                    rx.data_list.value(forecast.feels_like),
                    align="end",
                ),
                size="3",
            ),
            width="100%",
        ),
        direction="column",
        spacing="4",
    )
