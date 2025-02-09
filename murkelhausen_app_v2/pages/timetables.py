from datetime import datetime, timedelta
from enum import StrEnum, auto
from typing import cast

import reflex as rx
from reflex import Var
from reflex.constants.colors import Color

from murkelhausen_app_v2.templates.template import template


class SchoolVisitors(StrEnum):
    Andrea = auto()
    Mattis = auto()
    Erik = auto()


class TimeTableMattis(rx.Model, table=True):
    __tablename__ = "time_table_mattis"
    block: int
    timeframe: str
    even_week: bool
    subject_monday: str | None
    subject_tuesday: str | None
    subject_wednesday: str | None
    subject_thursday: str | None
    subject_friday: str | None


class TimeTableErik(rx.Model, table=True):
    __tablename__ = "time_table_erik"
    block: int
    timeframe: str
    subject_monday: str | None
    subject_tuesday: str | None
    subject_wednesday: str | None
    subject_thursday: str | None
    subject_friday: str | None


def _get_header_bg_color(weekday_number: int) -> Color:
    if datetime.now().isoweekday() == weekday_number:
        return rx.color("yellow")
    else:
        return rx.color("gray", 3)


def _parse_subject_name(subject_name: str | None) -> str:
    return subject_name if subject_name is not None else ""


def _get_subject_color(subject: str) -> Var:
    return rx.cond(
        subject == "Mittagspause",
        rx.color("orange", shade=4),
        rx.cond(
            subject == "Sport",
            rx.color("cyan", shade=6),
            rx.cond(
                subject == "Schwimmen",
                rx.color("red", shade=6),
                rx.color("white", shade=6),
            ),
        ),
    )


def _get_subject_opacity(subject: str) -> Var:
    return rx.cond(
        subject == "Mittagspause",
        0.5,
        1,
    )


def show_block(timetable: TimeTableMattis | TimeTableErik) -> rx.Component:
    return rx.table.row(
        rx.table.cell(timetable.timeframe, align="right"),
        rx.table.cell(
            _parse_subject_name(timetable.subject_monday),
            bg=_get_subject_color(timetable.subject_monday),
            opacity=_get_subject_opacity(timetable.subject_monday),
            align="center",
        ),
        rx.table.cell(
            _parse_subject_name(timetable.subject_tuesday),
            bg=_get_subject_color(timetable.subject_tuesday),
            opacity=_get_subject_opacity(timetable.subject_tuesday),
            align="center",
        ),
        rx.table.cell(
            _parse_subject_name(timetable.subject_wednesday),
            bg=_get_subject_color(timetable.subject_wednesday),
            opacity=_get_subject_opacity(timetable.subject_wednesday),
            align="center",
        ),
        rx.table.cell(
            _parse_subject_name(timetable.subject_thursday),
            bg=_get_subject_color(timetable.subject_thursday),
            opacity=_get_subject_opacity(timetable.subject_thursday),
            align="center",
        ),
        rx.table.cell(
            _parse_subject_name(timetable.subject_friday),
            bg=_get_subject_color(timetable.subject_friday),
            opacity=_get_subject_opacity(timetable.subject_friday),
            align="center",
        ),
        style={"_hover": {"opacity": 0.5}},
        align="center",
    )


def show_timetable(
    timetable: list[TimeTableMattis] | list[TimeTableErik],
) -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Zeit", align="right"),
                rx.table.column_header_cell("Montag", bg=_get_header_bg_color(1)),
                rx.table.column_header_cell("Dienstag", bg=_get_header_bg_color(2)),
                rx.table.column_header_cell("Mittwoch", bg=_get_header_bg_color(3)),
                rx.table.column_header_cell("Donnerstag", bg=_get_header_bg_color(4)),
                rx.table.column_header_cell("Freitag", bg=_get_header_bg_color(5)),
            ),
        ),
        rx.table.body(
            rx.foreach(timetable, show_block),
        ),
        variant="surface",
        size="3",
    )


class TimeTableState(rx.State):
    timetable_mattis_this_week: list[TimeTableMattis]
    timetable_mattis_next_week: list[TimeTableMattis]
    timetable_erik: list[TimeTableErik]
    current_week: int
    this_week_type: str
    next_week_type: str
    start_of_week_string: str
    end_of_week_string: str
    next_start_of_week_string: str
    next_end_of_week_string: str

    @rx.event
    def load(self):
        current_date = datetime.now()
        self.current_week = datetime.now().isocalendar()[1]
        start_of_week = current_date - timedelta(days=current_date.weekday())
        self.start_of_week_string = start_of_week.strftime("%d.%m.%Y")
        end_of_week = start_of_week + timedelta(days=6)
        self.end_of_week_string = end_of_week.strftime("%d.%m.%Y")
        next_start_of_week = start_of_week + timedelta(days=7)
        self.next_start_of_week_string = next_start_of_week.strftime("%d.%m.%Y")
        next_end_of_week = end_of_week + timedelta(days=7)
        self.next_end_of_week_string = next_end_of_week.strftime("%d.%m.%Y")

        self.this_week_type = "ungerade" if self.current_week % 2 != 0 else "gerade"
        self.next_week_type = (
            "gerade" if self.this_week_type == "ungerade" else "ungerade"
        )

        with rx.session() as session:
            timetable_mattis_even = session.exec(
                TimeTableMattis.select()
                .filter(TimeTableMattis.even_week == True)
                .order_by(TimeTableMattis.block.asc())
            )
            timetable_mattis_odd = session.exec(
                TimeTableMattis.select()
                .filter(TimeTableMattis.even_week == False)
                .order_by(TimeTableMattis.block.asc())
            )
            timetable_erik = session.exec(TimeTableErik.select())
            if self.this_week_type == "gerade":
                self.timetable_mattis_this_week = cast(
                    list[TimeTableMattis], timetable_mattis_even.all()
                )
                self.timetable_mattis_next_week = cast(
                    list[TimeTableMattis], timetable_mattis_odd.all()
                )
            else:
                self.timetable_mattis_this_week = cast(
                    list[TimeTableMattis], timetable_mattis_odd.all()
                )
                self.timetable_mattis_next_week = cast(
                    list[TimeTableMattis], timetable_mattis_even.all()
                )
            self.timetable_erik = cast(list[TimeTableErik], timetable_erik.all())
            session.close()


def show_timetable_mattis() -> rx.Component:
    return rx.vstack(
        rx.spacer(),
        rx.heading("Mattis' timetable"),
        rx.text(
            f"Aktuelle Woche ({TimeTableState.this_week_type} Kalenderwoche {TimeTableState.current_week}; {TimeTableState.start_of_week_string}-{TimeTableState.end_of_week_string})"
        ),
        show_timetable(TimeTableState.timetable_mattis_this_week),
        rx.spacer(spacing="2"),
        rx.text(
            f"Nächste Woche ({TimeTableState.next_week_type} Kalenderwoche {TimeTableState.current_week + 1}; {TimeTableState.next_start_of_week_string}-{TimeTableState.next_end_of_week_string})"
        ),
        show_timetable(TimeTableState.timetable_mattis_next_week),
    )


def show_timetable_erik() -> rx.Component:
    return rx.vstack(
        rx.spacer(),
        rx.heading("Erik's timetable"),
        show_timetable(TimeTableState.timetable_erik),
    )


def show_andrea() -> rx.Component:
    return rx.vstack(
        rx.spacer(),
        rx.heading("Andrea's timetable"),
        rx.text("Wednesday: 8:00 - 13:00"),
    )


@template(
    route="/school",
    title="Stundenpläne",
    icon="school",
    on_load=TimeTableState.load,
)
def school_page() -> rx.Component:
    return rx.tabs.root(
        rx.tabs.list(
            rx.tabs.trigger(
                SchoolVisitors.Mattis.capitalize(), value=SchoolVisitors.Mattis
            ),
            rx.tabs.trigger(
                SchoolVisitors.Erik.capitalize(), value=SchoolVisitors.Erik
            ),
            rx.tabs.trigger(
                SchoolVisitors.Andrea.capitalize(), value=SchoolVisitors.Andrea
            ),
        ),
        rx.tabs.content(
            show_timetable_mattis(),
            value=SchoolVisitors.Mattis,
        ),
        rx.tabs.content(
            show_timetable_erik(),
            value=SchoolVisitors.Erik,
        ),
        rx.tabs.content(
            show_andrea(),
            value=SchoolVisitors.Andrea,
        ),
        default_value=SchoolVisitors.Mattis,
    )
