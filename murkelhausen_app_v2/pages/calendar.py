import itertools
from datetime import date, datetime, timedelta
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


ALL_CALENDARS = "ALL_CALENDARS"


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
    current_calendar_name: str = next(iter(config.google.calendars.keys()))
    amount_of_weeks_to_show: str = "2"

    @rx.event
    def handle_add_termin_submit(self):
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
            event_start = date.fromisoformat(self.form_event_start_date)
            event_end = date.fromisoformat(self.form_event_end_date) + timedelta(days=1)
        else:
            event_start = datetime.fromisoformat(
                f"{self.form_event_start_date}T{self.form_start_time}:00"
            )

            event_end = datetime.fromisoformat(
                f"{self.form_event_start_date}T{self.form_end_time}:00"
            )
            if self.form_end_time < self.form_start_time:
                event_end = event_end + timedelta(days=1)

        if self.form_button_text == FormState.EDIT.value:
            event = Event(
                event_id=self.form_event_id,
                summary=self.form_event_name,
                start=event_start,
                end=event_end,
            )
            update_appointment(
                event=event,
                calendar_id=self._get_calendar_id(self.current_calendar_name),
            )
            yield rx.toast(f"Event geändert: {event}")
        else:
            event = Event(
                summary=self.form_event_name,
                start=event_start,
                end=event_end,
            )
            yield rx.toast(
                f"Event erstellt: {event.summary=}; {event.start=}; {event.end=}"
            )
            create_appointment(
                event=event,
                calendar_id=self._get_calendar_id(self.current_calendar_name),
            )

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
        calendar_ids = self._get_calendar_ids()

        self.appointments = list(
            itertools.chain(
                *[
                    get_list_of_appointments(
                        calendar_id=calendar_id,
                        amount_of_weeks_to_show=int(self.amount_of_weeks_to_show),
                    )
                    for calendar_id in calendar_ids
                ]
            )
        )

    @rx.event
    def delete_appointment(self, appointment: dict):
        """Appointment is a termin object as dict"""
        delete_appointment(
            Event(
                event_id=appointment["id"],
                summary=None,
                start=date(1970, 1, 1),
            ),
            calendar_id=appointment["calendar_id"],
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
            self.form_end_time = appointment.end_timestamp.strftime("%H:%M")

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
        self.current_calendar_name = calendar
        self.get_appointments()

    @rx.event
    def set_new_amount_of_weeks_to_show(self, amount_of_weeks: str):
        self.amount_of_weeks_to_show = amount_of_weeks
        self.get_appointments()

    def _get_calendar_ids(self) -> tuple[str, ...]:
        if self.current_calendar_name == ALL_CALENDARS:
            return tuple(config.google.calendars.values())

        return (self._get_calendar_id(self.current_calendar_name),)

    @staticmethod
    def _get_calender_name(searched_calendar_id: str) -> str:
        return next(
            (
                name
                for name, calendar_id in config.google.calendars.items()
                if calendar_id == searched_calendar_id
            ),
            None,
        )

    @staticmethod
    def _get_calendar_id(searched_calendar_name: str) -> str:
        return config.google.calendars[searched_calendar_name]


def show_appointment_form_header() -> rx.Component:
    return rx.hstack(
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
    )


def show_appointment_form_name() -> rx.Component:
    return rx.flex(
        rx.text("Name des Termins"),
        rx.input(
            placeholder="Terminname",
            type="text",
            value=CalendarState.form_event_name,
            on_change=CalendarState.set_form_event_name,
            id="event_name",
        ),
        direction="column",
        spacing="3",
    )


def show_appointment_form_dates() -> rx.Component:
    return rx.flex(
        rx.flex(
            rx.text(rx.cond(CalendarState.form_whole_day, "Start Datum", "Datum")),
            rx.input(
                type="date",
                value=CalendarState.form_event_start_date,
                on_change=CalendarState.set_form_event_start_date,
                id="event_start_date",
            ),
            direction="column",
            spacing="1",
        ),
        rx.flex(
            rx.text(
                "End Datum",
                hidden=~CalendarState.form_whole_day,
            ),
            rx.cond(
                CalendarState.form_whole_day,
                rx.input(
                    type="date",
                    value=CalendarState.form_event_end_date,
                    on_change=CalendarState.set_form_event_end_date,
                    id="event_end_date",
                ),
                rx.el.input(
                    type="hidden",
                    value=CalendarState.form_event_end_date,
                    on_change=CalendarState.set_form_event_end_date,
                    id="event_end_date",
                ),
            ),
            direction="column",
            spacing="1",
        ),
        spacing="3",
        flex_direction="row",
    )


def show_appointment_form_times() -> rx.Component:
    return rx.flex(
        rx.flex(
            rx.text("Startzeit", hidden=CalendarState.form_whole_day),
            rx.cond(
                CalendarState.form_whole_day,
                rx.el.input(
                    type="hidden",
                    value=CalendarState.form_start_time,
                    on_change=CalendarState.set_form_start_time,
                    id="start_time",
                ),
                rx.input(
                    type="time",
                    value=CalendarState.form_start_time,
                    on_change=CalendarState.set_form_start_time,
                    id="start_time",
                ),
            ),
            direction="column",
            spacing="1",
        ),
        rx.flex(
            rx.text("Endzeit", hidden=CalendarState.form_whole_day),
            rx.cond(
                CalendarState.form_whole_day,
                rx.el.input(
                    type="hidden",
                    value=CalendarState.form_end_time,
                    on_change=CalendarState.set_form_end_time,
                    id="end_time",
                ),
                rx.input(
                    type="time",
                    value=CalendarState.form_end_time,
                    on_change=CalendarState.set_form_end_time,
                    id="end_time",
                ),
            ),
            direction="column",
            spacing="1",
        ),
        spacing="3",
        flex_direction="row",
    )


def show_appointment_form() -> rx.Component:
    return rx.card(
        rx.flex(
            show_appointment_form_header(),
            rx.flex(
                show_appointment_form_name(),
                rx.checkbox(
                    "Ganztägig?",
                    name="is_whole_day",
                    checked=CalendarState.form_whole_day,
                    on_change=CalendarState.set_form_whole_day,
                    id="is_whole_day",
                ),
                show_appointment_form_dates(),
                show_appointment_form_times(),
                rx.button(
                    CalendarState.form_button_text,
                    on_click=CalendarState.handle_add_termin_submit,
                    type="submit",
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
            width="100%",
            direction="column",
            spacing="4",
        ),
        size="3",
    )


def show_appointment_table_row(appointment: Appointment) -> rx.Component:
    row_color = rx.cond(
        appointment.start_date == date.today(),
        rx.color("red"),
        rx.cond(
            appointment.start_date == date.today() + timedelta(days=1),
            rx.color("yellow"),
            rx.color("gray"),
        ),
    )

    return rx.table.row(
        rx.table.cell(
            rx.cond(appointment.is_recurring, rx.icon("repeat"), None),
            align="center",
        ),
        rx.table.cell(appointment.event_name),
        rx.table.cell(appointment.days_string),
        rx.table.cell(rx.cond(appointment.is_whole_day, "", appointment.start_time)),
        rx.table.cell(rx.cond(appointment.is_whole_day, "", appointment.end_time)),
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
                    rx.alert_dialog.title(
                        f"Termin '{appointment.event_name}' wirklich löschen?"
                    ),
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
        bg=row_color,
        # style={"_hover": {"bg": color, "opacity": 0.5}},
        align="center",
    )


def show_appointment_table_header() -> rx.Component:
    return rx.table.header(
        rx.table.row(
            rx.table.column_header_cell(""),
            rx.table.column_header_cell("Termin"),
            rx.table.column_header_cell("Tag"),
            rx.table.column_header_cell("Start"),
            rx.table.column_header_cell("Ende"),
            rx.table.column_header_cell("Bearbeiten"),
            rx.table.column_header_cell("Löschen"),
        ),
    )


def show_appointment_list() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.select(
                config.google.calendars.keys(),
                value=CalendarState.current_calendar_name,
                on_change=CalendarState.set_new_calendar,
            ),
            rx.heading(
                f"Termine in den nächsten {CalendarState.amount_of_weeks_to_show} Wochen für {CalendarState.current_calendar_name}"
            ),
            rx.table.root(
                show_appointment_table_header(),
                rx.foreach(
                    CalendarState.appointments,
                    show_appointment_table_row,
                ),
                variant="surface",
                size="3",
            ),
            rx.hstack(
                rx.text("Zeige Termine der nächsten Wochen:"),
                rx.select(
                    [str(i) for i in range(1, 11)],
                    value=CalendarState.amount_of_weeks_to_show,
                    on_change=CalendarState.set_new_amount_of_weeks_to_show,
                ),
                align="center",
            ),
            spacing="4",
        ),
    )


def show_appointment_page() -> rx.Component:
    return rx.hstack(
        show_appointment_list(),
        show_appointment_form(),
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
                    show_appointment_page(),
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
