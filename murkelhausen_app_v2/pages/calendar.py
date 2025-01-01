from datetime import date, datetime
from enum import Enum

import reflex as rx
from gcsa.event import Event

from murkelhausen_app_v2.backend.google_calendar import (
    get_list_of_appointments,
    Appointment,
    create_appointment,
    delete_appointment,
    update_appointment,
)
from murkelhausen_app_v2.config import config
from murkelhausen_app_v2.templates.template import template


class FormState(Enum):
    ADD = "Erstellen"
    EDIT = "Ändern"


class CalendarState(rx.State):
    appointments: list[Appointment]
    new_appointment_form: dict
    form_event_id: str
    form_event_name: str
    form_event_start_date: str
    form_event_end_date: str
    form_start_time: str
    form_end_time: str
    form_whole_day: bool
    form_button_text: str = FormState.ADD.value
    current_calendar: str = next(iter(config.google.calendars.keys()))

    @rx.event
    def handle_add_termin_submit(self, _: dict):
        if self.form_event_name == "" or self.form_event_start_date == "":
            yield rx.toast("Bitte Terminname und Datum angeben")
            return

        if (
            (self.form_whole_day is False or self.form_whole_day == 0)
            and (self.form_start_time is None or self.form_start_time == "")
            and (self.form_end_time is None or self.form_end_time == "")
        ):
            yield rx.toast("Bitte Start- und Endzeit angeben")
            return

        if self.form_whole_day is True:
            event_start = self.form_event_start_date
            event_end = self.form_event_end_date
        else:
            event_start = datetime.fromisoformat(
                f"{self.form_event_start_date}T{self.form_start_time}:00"
            )
            event_end = datetime.fromisoformat(
                f"{self.form_event_start_date}T{self.form_end_time}:00"
            )

        if self.form_button_text == FormState.EDIT.value:
            event = Event(
                event_id=self.form_event_id,
                summary=self.form_event_name,
                start=event_start,
                end=event_end,
            )
            update_appointment(event, calendar_id=self._get_calendar_id())
            yield rx.toast(f"Event geändert: {event}")
        else:
            event = Event(
                summary=self.form_event_name,
                start=event_start,
                end=event_end,
            )
            create_appointment(event, calendar_id=self._get_calendar_id())
            yield rx.toast(f"Event erstellt: {event}")

        self._clear_form()
        self.get_appointments()

    @rx.event
    def init(self):
        if self.appointments is None:
            self.appointments = []
        if self.new_appointment_form is None:
            self.new_appointment_form = {}

        self.get_appointments()

    @rx.event
    def get_appointments(self):
        calendar_id = self._get_calendar_id()
        self.appointments = get_list_of_appointments(calendar_id=calendar_id)

    @rx.event
    def delete_appointment(self, appointment: dict):
        """Appointment is a termin object as dict"""
        delete_appointment(
            Event(
                event_id=appointment["id"],
                summary=None,
                start=date(1970, 1, 1),
            ),
            calendar_id=self._get_calendar_id(),
        )
        yield rx.toast(f"Event '{appointment['event_name']}' gelöscht")
        self.get_appointments()

    @rx.event
    def prepare_appointment_for_change(self, appointment: Appointment):
        self.form_event_id = appointment.id
        self.form_event_name = appointment.event_name
        self.form_whole_day = appointment.is_whole_day
        self.form_event_start_date = appointment.start_timestamp.date().isoformat()
        self.form_event_end_date = appointment.end_timestamp.date().isoformat()

        self.form_button_text = FormState.EDIT.value
        if appointment.is_whole_day is False:
            self.form_start_time = appointment.start_timestamp.strftime("%H:%M")
            yield rx.set_value("start_time", self.form_start_time)
            self.form_end_time = appointment.end_timestamp.strftime("%H:%M")
            yield rx.set_value("end_time", self.form_end_time)

    @rx.event
    def clear_form(self):
        self._clear_form()
        yield rx.toast("Formular zurückgesetzt")

    def _clear_form(self):
        self.form_event_id = ""
        self.form_event_name = ""
        self.form_event_start_date = ""
        self.form_event_end_date = ""
        self.form_start_time = ""
        self.form_end_time = ""
        self.form_whole_day = False
        self.form_button_text = FormState.ADD.value

    @rx.event
    def set_new_calendar(self, calendar: str):
        self.current_calendar = calendar
        self.get_appointments()

    def _get_calendar_id(self) -> str:
        return config.google.calendars[self.current_calendar]


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


def show_appointment_form() -> rx.Component:
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
                    f"Termin {CalendarState.form_button_text}",
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
                                    placeholder="Terminname",
                                    type="text",
                                    value=CalendarState.form_event_name,
                                    on_change=CalendarState.set_form_event_name,
                                    id="event_name",
                                ),
                                as_child=True,
                            ),
                            direction="column",
                            spacing="1",
                        ),
                        width="100%",
                    ),
                    rx.checkbox(
                        "Ganztägig?",
                        name="is_whole_day",
                        checked=CalendarState.form_whole_day,
                        on_change=CalendarState.set_form_whole_day,
                        id="is_whole_day",
                    ),
                    rx.flex(
                        rx.form.field(
                            rx.flex(
                                rx.form.label("Start Datum"),
                                rx.form.control(
                                    rx.input(
                                        type="date",
                                        value=CalendarState.form_event_start_date,
                                        on_change=CalendarState.set_form_event_start_date,
                                        id="event_start_date",
                                    ),
                                    as_child=True,
                                ),
                                direction="column",
                                spacing="1",
                            ),
                            rx.form.field(
                                rx.flex(
                                    rx.form.label(
                                        "End Datum",
                                    ),
                                    rx.form.control(
                                        rx.input(
                                            type="date",
                                            value=CalendarState.form_event_end_date,
                                            on_change=CalendarState.set_form_event_end_date,
                                            id="event_end_date",
                                        ),
                                        as_child=True,
                                    ),
                                    direction="column",
                                    spacing="1",
                                ),
                                hidden=True,
                            ),
                        ),
                        spacing="3",
                        flex_direction="row",
                    ),
                    rx.cond(
                        CalendarState.form_whole_day,
                        rx.box(),
                        rx.flex(
                            rx.form.field(
                                rx.flex(
                                    rx.form.label("Startzeit"),
                                    rx.form.control(
                                        rx.input(
                                            type="time",
                                            # value=CalendarState.form_start_time,
                                            on_change=CalendarState.set_form_start_time,
                                            id="start_time",
                                        ),
                                        as_child=True,
                                    ),
                                    direction="column",
                                    spacing="1",
                                ),
                            ),
                            rx.form.field(
                                rx.flex(
                                    rx.form.label("Endzeit"),
                                    rx.form.control(
                                        rx.input(
                                            type="time",
                                            # value=CalendarState.form_end_time,
                                            on_change=CalendarState.set_form_end_time,
                                            id="end_time",
                                        ),
                                        as_child=True,
                                    ),
                                    direction="column",
                                    spacing="1",
                                ),
                            ),
                            spacing="3",
                            flex_direction="row",
                        ),
                    ),
                    rx.form.submit(
                        rx.button(CalendarState.form_button_text, type="submit"),
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


def show_appointment_table_row(appointment: Appointment) -> rx.Component:
    color = rx.cond(
        appointment.start_timestamp
        == datetime.combine(date.today(), datetime.min.time()),
        rx.color("yellow"),
        rx.color("gray"),
    )

    return rx.table.row(
        rx.table.cell(appointment.event_name),
        rx.table.cell(
            rx.cond(
                appointment.is_whole_day,
                appointment.start_day_string + " - " + appointment.end_day_string,
                appointment.start_day_string,
            )
        ),
        rx.table.cell(rx.cond(appointment.is_whole_day, "", appointment.start_time)),
        rx.table.cell(rx.cond(appointment.is_whole_day, "", appointment.end_time)),
        rx.table.cell(
            rx.cond(appointment.is_recurring, "Ja", "Nein"),
            align="center",
        ),
        rx.table.cell(
            rx.badge(
                rx.icon(
                    tag="pencil",
                    style=rx.Style({"_hover": {"color": "blue", "opacity": 0.5}}),
                    on_click=CalendarState.prepare_appointment_for_change(appointment),
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


def show_appointment_table_header() -> rx.Component:
    return rx.table.header(
        rx.table.row(
            rx.table.column_header_cell("Termin"),
            rx.table.column_header_cell("Tag"),
            rx.table.column_header_cell("Start"),
            rx.table.column_header_cell("Ende"),
            rx.table.column_header_cell("Serie"),
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
                    show_appointment_table_header(),
                    rx.foreach(
                        CalendarState.appointments,
                        show_appointment_table_row,
                    ),
                    variant="surface",
                    size="3",
                ),
                show_appointment_form(),
            ),
            spacing="4",
        ),
    )


@template(
    route="/cal",
    title="Kalender",
    icon="calendar",
    on_load=CalendarState.init,
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
