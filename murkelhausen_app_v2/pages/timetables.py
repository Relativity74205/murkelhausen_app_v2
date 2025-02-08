from datetime import datetime, timedelta
from enum import StrEnum, auto

import reflex as rx
from reflex import Var
from reflex.constants.colors import Color

from murkelhausen_app_v2.templates.template import template


class SchoolVisitors(StrEnum):
    Andrea = auto()
    Mattis = auto()
    Erik = auto()


class Day(StrEnum):
    Monday = auto()
    Tuesday = auto()
    Wednesday = auto()
    Thursday = auto()
    Friday = auto()


class TimeBlocks(StrEnum):
    First = auto()
    Second = auto()
    Third = auto()
    Fourth = auto()
    Fifth = auto()
    Sixth = auto()
    Sgeradeth = auto()
    Eighth = auto()
    Ninth = auto()
    LunchBreak = auto()


times = {
    SchoolVisitors.Mattis: {
        TimeBlocks.First: "8:00 - 9:30",
        TimeBlocks.Second: "9:50 - 11:20",
        TimeBlocks.Third: "11:40 - 13:10",
        TimeBlocks.LunchBreak: "13:10 - 14:00",
        TimeBlocks.Fourth: "14:00 - 15:30",
    },
    SchoolVisitors.Erik: {
        TimeBlocks.First: "8:00 - 8:45",
        TimeBlocks.Second: "8:50 - 9:30",
        TimeBlocks.Third: "10:00 - 10:45",
        TimeBlocks.Fourth: "10:45 - 11:30",
        TimeBlocks.Fifth: "11:45 - 12:30",
        TimeBlocks.Sixth: "12:30 - 13:15",
    },
}


timetables = {
    SchoolVisitors.Erik: {
        TimeBlocks.First: ["x", "x", None, "x", "x"],
        TimeBlocks.Second: ["x", "x", "x", "x", "x"],
        TimeBlocks.Third: ["x", "x", "x", "Englisch", "Englisch"],
        TimeBlocks.Fourth: ["x", "x", "x", "x", "Englisch"],
        TimeBlocks.Fifth: [
            "Sport",
            "x",
            "Schwimmen",
            "Religion",
            None,
        ],
        TimeBlocks.Sixth: [
            "Sport",
            "Digitales Lernen",
            "Schwimmen",
            "Religion",
            None,
        ],
    },
    SchoolVisitors.Andrea: {},
}


def _get_header_bg_color(weekday_number: int) -> Color:
    if datetime.now().isoweekday() == weekday_number:
        return rx.color("yellow")
    else:
        return rx.color("gray", 3)


def _parse_subject_name(subject_name: str | None) -> str:
    return subject_name if subject_name is not None else ""


def _get_subject_color(subject: str) -> Var:
    return rx.cond(
        subject == "Sport",
        rx.color("cyan", shade=6),
        rx.cond(
            subject == "Schwimmen", rx.color("red", shade=6), rx.color("white", shade=6)
        ),
    )


def show_block(subject_list: list[str], time: str) -> rx.Component:
    return rx.table.row(
        rx.table.cell(time, align="right"),
        rx.table.cell(
            _parse_subject_name(subject_list[0]),
            bg=_get_subject_color(subject_list[0]),
            align="center",
        ),
        rx.table.cell(
            _parse_subject_name(subject_list[1]),
            bg=_get_subject_color(subject_list[1]),
            align="center",
        ),
        rx.table.cell(
            _parse_subject_name(subject_list[2]),
            bg=_get_subject_color(subject_list[2]),
            align="center",
        ),
        rx.table.cell(
            _parse_subject_name(subject_list[3]),
            bg=_get_subject_color(subject_list[3]),
            align="center",
        ),
        rx.table.cell(
            _parse_subject_name(subject_list[4]),
            bg=_get_subject_color(subject_list[4]),
            align="center",
        ),
        style={"_hover": {"opacity": 0.5}},
        align="center",
    )


def show_mattis_timetable(
    timetable_mattis: list[list[str]], times_mattis: dict
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
            show_block(
                timetable_mattis[0],
                times_mattis[TimeBlocks.First],
            ),
            show_block(
                timetable_mattis[1],
                times_mattis[TimeBlocks.Second],
            ),
            show_block(
                timetable_mattis[2],
                times_mattis[TimeBlocks.Third],
            ),
            show_block(
                ["", "", "Mittagspause", "", ""], times_mattis[TimeBlocks.LunchBreak]
            ),
            show_block(
                ["", "", "", "", ""],
                times_mattis[TimeBlocks.Fourth],
            ),
        ),
        variant="surface",
        size="3",
    )


def show_erik_timetable(timetable_erik: dict, times_erik: dict) -> rx.Component:
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
            show_block(
                timetable_erik.get(TimeBlocks.First, []), times_erik[TimeBlocks.First]
            ),
            show_block(
                timetable_erik.get(TimeBlocks.Second, []), times_erik[TimeBlocks.Second]
            ),
            show_block(
                timetable_erik.get(TimeBlocks.Third, []), times_erik[TimeBlocks.Third]
            ),
            show_block(
                timetable_erik.get(TimeBlocks.Fourth, []), times_erik[TimeBlocks.Fourth]
            ),
            show_block(
                timetable_erik.get(TimeBlocks.Fifth, []), times_erik[TimeBlocks.First]
            ),
            show_block(
                timetable_erik.get(TimeBlocks.Sixth, []), times_erik[TimeBlocks.Sixth]
            ),
        ),
        variant="surface",
        size="3",
    )


class TimetableMattisState(rx.State):
    now: str

    @rx.event
    def load(self):
        self.now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    @rx.var
    def timetable_mattis_ungerade(self) -> list[list[str]]:
        return [
            [
                "Religion",
                "Physik",
                "Mathe",
                "Biologie",
                "Deutsch",
            ],
            [
                "Englisch",
                "Deutsch",
                "Sport",
                "Geschichte",
                "Mathe",
            ],
            [
                "Mathe",
                "Kunst",
                "Informatik",
                "Englisch",
                None,
            ],
        ]

    @rx.var
    def timetable_mattis_gerade(self) -> list[list[str]]:
        return [
            [
                "Sport",
                "Physik",
                "Mathe",
                "Sport",
                "Religion",
            ],
            [
                "Biologie",
                "Informatik",
                "Englisch",
                "Kunst",
                "Englisch",
            ],
            [
                "Mathe",
                "Deutsch",
                "Geschichte",
                None,
                "Deutsch",
            ],
        ]


def show_mattis() -> rx.Component:
    times_mattis = times[SchoolVisitors.Mattis]

    current_date = datetime.now()
    current_week = datetime.now().isocalendar()[1]
    start_of_week = current_date - timedelta(days=current_date.weekday())
    start_of_week_string = start_of_week.strftime("%d.%m.%Y")
    end_of_week = start_of_week + timedelta(days=6)
    end_of_week_string = end_of_week.strftime("%d.%m.%Y")
    next_start_of_week = start_of_week + timedelta(days=7)
    next_start_of_week_string = next_start_of_week.strftime("%d.%m.%Y")
    next_end_of_week = end_of_week + timedelta(days=7)
    next_end_of_week_string = next_end_of_week.strftime("%d.%m.%Y")

    this_week_type = "ungerade" if current_week % 2 != 0 else "gerade"
    next_week_type = "gerade" if this_week_type == "ungerade" else "ungerade"

    return rx.vstack(
        rx.spacer(),
        rx.heading(f"Mattis' timetable {TimetableMattisState.now}"),
        rx.text(
            f"Aktuelle Woche ({this_week_type} Kalenderwoche {current_week}; {start_of_week_string}-{end_of_week_string})"
        ),
        show_mattis_timetable(
            TimetableMattisState.timetable_mattis_ungerade, times_mattis
        ),
        rx.spacer(spacing="2"),
        rx.text(
            f"Nächste Woche ({next_week_type} Kalenderwoche {current_week + 1}; {next_start_of_week_string}-{next_end_of_week_string})"
        ),
        show_mattis_timetable(
            TimetableMattisState.timetable_mattis_gerade, times_mattis
        ),
    )


def show_erik() -> rx.Component:
    times_mattis = times[SchoolVisitors.Erik]
    time_tables = timetables[SchoolVisitors.Erik]
    return rx.vstack(
        rx.spacer(),
        rx.heading("Erik's timetable"),
        show_erik_timetable(time_tables, times_mattis),
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
    on_load=TimetableMattisState.load,
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
            show_mattis(),
            value=SchoolVisitors.Mattis,
        ),
        rx.tabs.content(
            show_erik(),
            value=SchoolVisitors.Erik,
        ),
        rx.tabs.content(
            show_andrea(),
            value=SchoolVisitors.Andrea,
        ),
        default_value=SchoolVisitors.Mattis,
    )
