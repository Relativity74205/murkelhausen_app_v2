from datetime import date

import reflex as rx

from murkelhausen_app_v2.backend.google_calendar import get_list_of_appointments, Termin
from murkelhausen_app_v2.templates.template import template


class CalendarState(rx.State):
    appointments: list[Termin] = []
    new_appointment_form: dict = {}
    whole_day: bool = False

    @rx.event
    def change_whole_day(self):
        self.whole_day = not self.whole_day
        rx.toast(f"foo={self.whole_day}")

    @rx.event
    def handle_add_termin_submit(self, form_data: dict):
        self.new_appointment_form = form_data

    def get_appointments(self):
        self.appointments = get_list_of_appointments()


# TODO: how to set time input to use 24 hour format?
def form_field(label: str, placeholder: str, type: str, name: str) -> rx.Component:
    return rx.form.field(
        rx.flex(
            rx.form.label(label),
            rx.form.control(
                rx.input(placeholder=placeholder, type=type),
                as_child=True,
            ),
            direction="column",
            spacing="1",
        ),
        name=name,
        width="100%",
    )


def termin_form() -> rx.Component:
    def foo_temp(form_data: dict) -> rx.Component:
        CalendarState.handle_add_termin_submit(form_data)
        return rx.window_alert(form_data.to_string())

    return rx.card(
        rx.flex(
            rx.hstack(
                rx.badge(
                    rx.icon(tag="calendar-plus", size=32),
                    color_scheme="mint",
                    radius="full",
                    padding="0.65rem",
                ),
                rx.heading(
                    "Erstelle einen Termin",
                    size="4",
                    weight="bold",
                ),
                height="100%",
                spacing="4",
                align_items="center",
                width="100%",
            ),
            rx.form.root(
                rx.flex(
                    form_field(
                        "Name des Termins",
                        "Termin name",
                        "text",
                        "event_name",
                    ),
                    rx.flex(
                        form_field("Datum", "", "date", "event_date"),
                        rx.checkbox("Ganztägig", name="whole_day", on_click=CalendarState.change_whole_day),
                        spacing="3",
                        flex_direction="row",
                        align="center",
                    ),
                    rx.cond(
                        CalendarState.whole_day,
                        rx.box(),
                        rx.flex(
                            form_field("Startzeit", "", "time", "start_time"),
                            form_field("Endzeit", "", "time", "end_time"),
                            spacing="3",
                            flex_direction="row",
                        ),
                    ),
                    direction="column",
                    spacing="2",
                ),
                rx.form.submit(
                    rx.button("Erstellen"),
                    as_child=True,
                    width="100%",
                ),
                on_submit=foo_temp,
                reset_on_submit=False,
            ),
            width="100%",
            direction="column",
            spacing="4",
        ),
        size="3",
    )


def show_appointment(appointment: Termin) -> rx.Component:
    color = rx.cond(
        appointment.start_day == date.today(),
        rx.color("yellow"),
        rx.color("gray"),
    )

    return rx.table.row(
        rx.table.cell(appointment.event_name),
        rx.table.cell(appointment.start_day_string),
        rx.table.cell(appointment.start_time),
        rx.table.cell(appointment.end_time),
        bg=color,
        style={"_hover": {"bg": color, "opacity": 0.5}},
        align="center",
    )


def show_termin_table_header() -> rx.Component:
    return rx.table.header(
        rx.table.row(
            rx.table.column_header_cell("Termin"),
            rx.table.column_header_cell("Tag"),
            rx.table.column_header_cell("Start"),
            rx.table.column_header_cell("Ende"),
        ),
    )


@template(
    route="/cal",
    title="Kalender",
    icon="calendar",
    on_load=CalendarState.get_appointments,
)
def calender() -> rx.Component:
    return rx.vstack(
        rx.heading("Termine in den nächsten 2 Wochen"),
        rx.hstack(
            rx.table.root(
                show_termin_table_header(),
                rx.foreach(
                    CalendarState.appointments,
                    show_appointment,
                ),
                variant="surface",
                size="3",
            ),
            rx.spacer(),
            termin_form(),
            justify="between",
            width="100%",
        ),
    )
