from datetime import date, datetime

import reflex as rx
from gcsa.event import Event

from murkelhausen_app_v2.backend.google_calendar import (
    get_list_of_appointments,
    Appointment,
    create_appointment,
    delete_appointment,
)
from murkelhausen_app_v2.config import config
from murkelhausen_app_v2.templates.template import template


class CalendarState(rx.State):
    appointments: list[Appointment]
    new_appointment_form: dict
    whole_day: bool = False
    form_appointment_name: str = ""
    current_calendar: str = next(iter(config.google.calendars.keys()))

    @rx.event
    def change_whole_day(self):
        self.whole_day = not self.whole_day
        rx.toast(f"foo={self.whole_day}")

    @rx.event
    def handle_add_termin_submit(self, form_data: dict):
        if self.form_appointment_name == "":
            return

        if "whole_day" in form_data.keys():
            event = Event(
                summary=self.form_appointment_name,
                start=date.fromisoformat(form_data["event_date"]),
                end=date.fromisoformat(form_data["event_date"]),
            )
        else:
            event = Event(
                summary=self.form_appointment_name,
                start=datetime.fromisoformat(
                    f"{form_data['event_date']}T{form_data['start_time']}:00"
                ),
                end=datetime.fromisoformat(
                    f"{form_data['event_date']}T{form_data['end_time']}:00"
                ),
            )
        create_appointment(event)
        self.form_appointment_name = ""
        yield rx.toast(f"Event erstellt: {event}")
        self.get_appointments()

    @rx.event
    def get_appointments(self):
        if self.appointments is None:
            self.appointments = []
        if self.new_appointment_form is None:
            self.new_appointment_form = {}

        calendar_id = config.google.calendars[self.current_calendar]
        self.appointments = get_list_of_appointments(calendar_id=calendar_id)

    @rx.event
    def delete_appointment(self, appointment: dict):
        """Appointment is a termin object as dict"""
        delete_appointment(
            Event(summary=None, start=date(1970, 1, 1), event_id=appointment["id"])
        )
        yield rx.toast(f"Event '{appointment['event_name']}' gelöscht")
        self.get_appointments()

    @rx.event
    def show_appointment(self, appointment: Appointment):
        self.form_appointment_name = appointment.event_name
        yield rx.toast(f"Event '{self.form_appointment_name}' wird angezeigt")

    @rx.event
    def clear_form(self):
        yield rx.toast("Formular zurückgesetzt")
        self.form_appointment_name = ""

    @rx.event
    def set_new_calendar(self, calendar: str):
        self.current_calendar = calendar
        self.get_appointments()


# TODO: how to set time input to use 24 hour format?
def form_field(
    label: str, placeholder: str, data_type: str, name: str, value: str | None = None
) -> rx.Component:
    return rx.form.field(
        rx.flex(
            rx.form.label(label),
            rx.form.control(
                rx.input(placeholder=placeholder, type=data_type, value=value),
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
                    rx.form.field(
                        rx.flex(
                            rx.form.label("Name des Termins"),
                            rx.form.control(
                                rx.input(
                                    placeholder="Termin name",
                                    type="text",
                                    value=CalendarState.form_appointment_name,
                                    on_change=CalendarState.set_form_appointment_name,
                                ),
                                as_child=True,
                            ),
                            direction="column",
                            spacing="1",
                        ),
                        name="event_name",
                        width="100%",
                    ),
                    rx.flex(
                        form_field("Datum", "", "date", "event_date"),
                        rx.checkbox(
                            "Ganztägig",
                            name="whole_day",
                            on_change=CalendarState.set_whole_day,
                        ),
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
                    rx.form.submit(
                        rx.button("Erstellen"),
                        as_child=True,
                        width="100%",
                    ),
                    rx.button(
                        "Abbrechen",
                        on_click=CalendarState.clear_form,
                        width="100%",
                        bg="grey",
                    ),
                    direction="column",
                    spacing="2",
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


def show_appointment(appointment: Appointment) -> rx.Component:
    color = rx.cond(
        appointment.start_timestamp
        == datetime.combine(date.today(), datetime.min.time()),
        rx.color("yellow"),
        rx.color("gray"),
    )

    return rx.table.row(
        rx.table.cell(appointment.event_name),
        rx.table.cell(appointment.start_day_string),
        rx.table.cell(
            rx.cond(appointment.start_time == "00:00", "", appointment.start_time)
        ),
        rx.table.cell(
            rx.cond(appointment.end_time == "00:00", "", appointment.end_time)
        ),
        rx.table.cell(
            rx.badge(
                rx.icon(
                    tag="pencil",
                    style=rx.Style({"_hover": {"color": "blue", "opacity": 0.5}}),
                    on_click=CalendarState.show_appointment(appointment),
                )
            ),
            align="center",
        ),
        rx.table.cell(
            rx.alert_dialog.root(
                rx.alert_dialog.trigger(
                    rx.badge(
                        rx.icon(
                            tag="trash-2",
                            style=rx.Style(
                                {"_hover": {"color": "red", "opacity": 0.5}}
                            ),
                        )
                    ),
                ),
                rx.alert_dialog.content(
                    rx.alert_dialog.title("Termin wirklich löschen?"),
                    rx.flex(
                        rx.alert_dialog.cancel(
                            rx.button("Abbruch"),
                        ),
                        rx.alert_dialog.action(
                            rx.button(
                                "Löschen",
                                on_click=CalendarState.delete_appointment(appointment),
                            ),
                            spacing="12",
                        ),
                        direction="row",
                        justify="between",
                    ),
                ),
            ),
            align="center",
        ),
        bg=color,
        # style={"_hover": {"bg": color, "opacity": 0.5}},
        align="center",
    )


def show_termin_table_header() -> rx.Component:
    return rx.table.header(
        rx.table.row(
            rx.table.column_header_cell("Termin"),
            rx.table.column_header_cell("Tag"),
            rx.table.column_header_cell("Start"),
            rx.table.column_header_cell("Ende"),
            rx.table.column_header_cell("Bearbeiten"),
            rx.table.column_header_cell("Löschen"),
        ),
    )


def show_appointment_list():
    return (
        rx.vstack(
            rx.select(
                config.google.calendars.keys(),
                value=CalendarState.current_calendar,
                on_change=CalendarState.set_new_calendar,
            ),
            rx.heading(
                f"Termine in den nächsten 2 Wochen für {CalendarState.current_calendar}"
            ),
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
                termin_form(),
            ),
            spacing="4",
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
        rx.tabs.root(
            rx.vstack(
                rx.tabs.list(
                    rx.tabs.trigger("Liste", value="liste"),
                    rx.tabs.trigger("Kalender Papa Arbeit", value="kalender_work"),
                ),
                rx.tabs.content(
                    show_appointment_list(),
                    value="liste",
                ),
                rx.tabs.content(
                    rx.vstack(
                        rx.el.Iframe(
                            src="https://calendar.google.com/calendar/embed?src=d8vonkqtg15pf4en7eluh5kk1egdrm0t%40import.calendar.google.com&ctz=Europe%2FBerlin",
                            width="100%",
                            height=600,
                            style={"border": "0"},
                            frameborder="0",
                            scrolling="no",
                        ),
                        width="100%",
                    ),
                    value="kalender_work",
                    width="100%",
                ),
                width="100%",
                spacing="5",
            ),
            default_value="liste",
            width="100%",
        ),
        width="100%",
    )
