from datetime import date, datetime

import reflex as rx
from gcsa.event import Event

from murkelhausen_app_v2.backend.google_calendar import get_list_of_appointments, Termin, create_appointment, \
    delete_appointment
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
        if "whole_day" in form_data.keys():
            event = Event(
                summary=form_data["event_name"],
                start=date.fromisoformat(form_data["event_date"]),
                end=date.fromisoformat(form_data["event_date"]),
            )
        else:
            event = Event(
                summary=form_data["event_name"],
                start=datetime.fromisoformat(f"{form_data['event_date']}T{form_data['start_time']}:00"),
                end=datetime.fromisoformat(f"{form_data['event_date']}T{form_data['end_time']}:00"),
            )
        create_appointment(event)
        yield rx.toast(f"Event erstellt: {event}")
        self.get_appointments()

    @rx.event
    def get_appointments(self):
        self.appointments = get_list_of_appointments()

    @rx.event
    def delete_appointment(self, event_id: id):
        delete_appointment(Event(summary=None, start=date(1970,1,1), event_id=event_id))
        yield rx.toast(f"Event {event_id} gelöscht")
        self.get_appointments()


# TODO: how to set time input to use 24 hour format?
def form_field(label: str, placeholder: str, data_type: str, name: str) -> rx.Component:
    return rx.form.field(
        rx.flex(
            rx.form.label(label),
            rx.form.control(
                rx.input(placeholder=placeholder, type=data_type),
                as_child=True,
            ),
            direction="column",
            spacing="1",
        ),
        name=name,
        width="100%",
    )


def termin_form() -> rx.Component:
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
                        rx.checkbox("Ganztägig", name="whole_day", on_change=CalendarState.set_whole_day),
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
                on_submit=CalendarState.handle_add_termin_submit,
                reset_on_submit=True,
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
        # TODO make nice: https://reflex.dev/docs/library/overlay/alert-dialog/
        rx.table.cell(
            rx.alert_dialog.root(
                rx.alert_dialog.trigger(
                    rx.badge(rx.icon(tag="delete")),
                ),
                rx.alert_dialog.content(
                    rx.alert_dialog.title("Revoke access"),
                    rx.alert_dialog.description(
                        "Are you sure? This application will no longer be accessible and any existing sessions will be expired.",
                    ),
                    rx.flex(
                        rx.alert_dialog.cancel(
                            rx.button("Cancel"),
                        ),
                        rx.alert_dialog.action(
                            rx.button("Revoke access", on_click=CalendarState.delete_appointment(appointment.id)),
                            spacing="3",
                        ),
                    ),
                )
            )
        ),
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
            rx.table.column_header_cell("Löschen"),
        ),
    )


@template(
    route="/cal",
    title="Kalender",
    icon="calendar",
    on_load=CalendarState.get_appointments,
)
def calendar_page() -> rx.Component:
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
