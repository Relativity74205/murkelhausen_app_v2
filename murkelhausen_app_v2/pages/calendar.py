import itertools
from datetime import date, datetime, timedelta
from enum import Enum

import pytz
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


ALL_CALENDARS = "Alle"
DEFAULT_APPOINTMENT_CALENDAR_NAME = "Arkadius"


class CalendarState(rx.State):
    appointments: list[Appointment]
    appointments_loaded: bool = False
    new_appointment_form: dict
    form_event_id: str
    form_event_name: str
    form_event_start_date: str
    form_event_end_date: str
    form_start_time: str
    form_end_time: str
    form_whole_day: bool
    form_button_text: str = FormState.ADD.value
    current_calendar_name: str = ALL_CALENDARS
    form_appointment_calendar_name: str = DEFAULT_APPOINTMENT_CALENDAR_NAME
    form_original_appointment_calendar_name: str | None = None
    amount_of_weeks_to_show: str = "2"

    @rx.var(cache=False)
    def appointments_to_show(self) -> list[Appointment]:
        return [
            appointment
            for appointment in self.appointments
            if self.current_calendar_name == ALL_CALENDARS
            or self.current_calendar_name == appointment.calendar_name
        ]

    @rx.var(cache=True)
    def todays_appointments(self) -> list[Appointment]:
        return [
            appointment
            for appointment in self.appointments
            if appointment.start_date == date.today()
        ]

    @rx.var(cache=True)
    def tomorrows_appointments(self) -> list[Appointment]:
        return [
            appointment
            for appointment in self.appointments
            if appointment.start_date == date.today() + timedelta(days=1)
        ]

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
            event_start = date.fromisoformat(self.form_event_start_date).astimezone(
                pytz.timezone("Europe/Berlin")
            )
            event_end = date.fromisoformat(self.form_event_end_date).astimezone(
                pytz.timezone("Europe/Berlin")
            ) + timedelta(days=1)
        else:
            event_start = datetime.fromisoformat(
                f"{self.form_event_start_date}T{self.form_start_time}:00"
            ).astimezone(pytz.timezone("Europe/Berlin"))

            event_end = datetime.fromisoformat(
                f"{self.form_event_start_date}T{self.form_end_time}:00"
            ).astimezone(pytz.timezone("Europe/Berlin"))
            if self.form_end_time < self.form_start_time:
                event_end = event_end + timedelta(days=1)

        if self.form_button_text == FormState.EDIT.value:
            event = Event(
                event_id=self.form_event_id,
                summary=self.form_event_name,
                start=event_start,
                end=event_end,
            )
            if (
                self.form_original_appointment_calendar_name
                != self.form_appointment_calendar_name
            ):
                delete_appointment(
                    event=event,
                    calendar_id=self._get_calendar_id(
                        self.form_original_appointment_calendar_name
                    ),
                )
                event = Event(
                    summary=self.form_event_name,
                    start=event_start,
                    end=event_end,
                )
                create_appointment(
                    event=event,
                    calendar_id=self._get_calendar_id(
                        self.form_appointment_calendar_name
                    ),
                )
            else:
                update_appointment(
                    event=event,
                    calendar_id=self._get_calendar_id(
                        self.form_appointment_calendar_name
                    ),
                )
            yield rx.toast(f"Event geändert: '{event.summary}'")
            self._clear_form()
        else:
            event = Event(
                summary=self.form_event_name,
                start=event_start,
                end=event_end,
            )
            yield rx.toast(f"Event erstellt: '{event.summary}'")
            create_appointment(
                event=event,
                calendar_id=self._get_calendar_id(self.form_appointment_calendar_name),
            )

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
        self.appointments_loaded = False
        calendar_ids = self._get_all_calendar_ids()

        self.appointments = list(
            itertools.chain(
                *[
                    get_list_of_appointments(
                        calendar_id=calendar_id,
                        calendar_name=self._get_calender_name(calendar_id),
                        amount_of_days_to_show=int(self.amount_of_weeks_to_show) * 7,
                    )
                    for calendar_id in calendar_ids
                ]
            )
        )
        self.appointments.sort(key=lambda x: x.start_timestamp)
        self.appointments_loaded = True

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
        self.form_appointment_calendar_name = appointment.calendar_name
        self.form_original_appointment_calendar_name = appointment.calendar_name
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
        self.form_appointment_calendar_name = DEFAULT_APPOINTMENT_CALENDAR_NAME
        self.form_original_appointment_calendar_name = None

    @rx.event
    def set_new_calendar(self, calendar: str):
        self.current_calendar_name = calendar
        # self.get_appointments()

    @rx.event
    def set_new_amount_of_weeks_to_show(self, amount_of_weeks: str):
        self.amount_of_weeks_to_show = amount_of_weeks
        self.get_appointments()

    def _get_all_calendar_ids(self) -> tuple[str, ...]:
        return tuple(config.google.calendars.values())

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
        rx.vstack(
            rx.heading(
                f"Termin {CalendarState.form_button_text} für",
                size="4",
                weight="bold",
            ),
            rx.select(
                [ALL_CALENDARS] + list(config.google.calendars.keys()),
                value=CalendarState.form_appointment_calendar_name,
                on_change=CalendarState.set_form_appointment_calendar_name,
            ),
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
                    "Zurücksetzen",
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


def show_edit_appointment_button(appointment: Appointment) -> rx.Component:
    return rx.badge(
        rx.icon(
            tag="pencil",
            style=rx.Style({"_hover": {"color": "blue", "opacity": 0.5}}),
            on_click=CalendarState.prepare_appointment_for_change(appointment),
        )
    )


def show_delete_appointment_button(appointment: Appointment) -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.trigger(
            rx.badge(
                rx.icon(
                    tag="trash-2",
                    style=rx.Style({"_hover": {"color": "red", "opacity": 0.5}}),
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
    )


def show_appointment_table_row(
    appointment: Appointment,
    show_calendar_col: bool,
    show_edit_col: bool,
    show_delete_col: bool,
    show_row_colors: bool,
) -> rx.Component:
    row_color = rx.cond(
        (appointment.start_date == date.today()) & show_row_colors,
        rx.color("red"),
        rx.cond(
            (appointment.start_date == date.today() + timedelta(days=1))
            & show_row_colors,
            rx.color("yellow"),
            rx.color("gray"),
        ),
    )

    return rx.table.row(
        rx.table.cell(
            rx.cond(appointment.is_recurring, rx.icon("repeat"), None),
            align="center",
        ),
        rx.cond(
            show_calendar_col,
            rx.table.cell(appointment.calendar_name),
            None,
        ),
        rx.table.cell(appointment.event_name),
        rx.table.cell(appointment.days_string),
        rx.table.cell(rx.cond(appointment.is_whole_day, "", appointment.start_time)),
        rx.table.cell(rx.cond(appointment.is_whole_day, "", appointment.end_time)),
        rx.cond(
            show_edit_col,
            rx.table.cell(
                show_edit_appointment_button(appointment),
                align="center",
            ),
            None,
        ),
        rx.cond(
            show_delete_col,
            rx.table.cell(
                show_delete_appointment_button(appointment),
                align="center",
            ),
            None,
        ),
        bg=row_color,
        align="center",
    )


def show_appointment_table_header(
    show_calendar_col: bool, show_edit_col: bool, show_delete_col: bool
) -> rx.Component:
    return rx.table.header(
        rx.table.row(
            rx.table.column_header_cell(""),
            rx.cond(
                show_calendar_col,
                rx.table.column_header_cell("Kalender"),
                None,
            ),
            rx.table.column_header_cell("Termin"),
            rx.table.column_header_cell("Tag"),
            rx.table.column_header_cell("Start"),
            rx.table.column_header_cell("Ende"),
            rx.cond(
                show_edit_col,
                rx.table.column_header_cell("Bearbeiten"),
                None,
            ),
            rx.cond(
                show_delete_col,
                rx.table.column_header_cell("Löschen"),
                None,
            ),
        ),
    )


def show_appointment_table(
    appointments: list[Appointment],
    show_calendar_col: bool,
    show_edit_col: bool,
    show_delete_col: bool,
    show_row_colors: bool,
) -> rx.Component:
    return rx.table.root(
        show_appointment_table_header(
            show_calendar_col=show_calendar_col,
            show_edit_col=show_edit_col,
            show_delete_col=show_delete_col,
        ),
        rx.foreach(
            appointments,
            lambda appointment: show_appointment_table_row(
                appointment,
                show_calendar_col=show_calendar_col,
                show_edit_col=show_edit_col,
                show_delete_col=show_delete_col,
                show_row_colors=show_row_colors,
            ),
        ),
        variant="surface",
        size="3",
    )


def show_appointment_list() -> rx.Component:
    header_string = (
        f"Termine in den nächsten {CalendarState.amount_of_weeks_to_show} Wochen für",
    )

    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(header_string),
                rx.select(
                    [ALL_CALENDARS] + list(config.google.calendars.keys()),
                    value=CalendarState.current_calendar_name,
                    on_change=CalendarState.set_new_calendar,
                ),
                align="center",
            ),
            rx.cond(
                CalendarState.appointments_loaded == True,
                show_appointment_table(
                    CalendarState.appointments_to_show,
                    show_calendar_col=CalendarState.current_calendar_name
                    == ALL_CALENDARS,
                    show_edit_col=True,
                    show_delete_col=True,
                    show_row_colors=True,
                ),
                rx.spinner("Suche nach Terminen..."),
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
    return rx.vstack(
        rx.hstack(
            show_appointment_list(),
            show_appointment_form(),
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
