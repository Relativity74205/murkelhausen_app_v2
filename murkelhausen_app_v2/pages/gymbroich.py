
import reflex as rx

from murkelhausen_app_v2.templates.template import template
from murkelhausen_app_v2.backend.gymbroich import Vertretungsplan, get_vertretungsplan_dates, \
    VertretungsplanEvent, get_vertretungsplan_mattis


class State(rx.State):
    dates: bool = False
    vertretungsplaene: dict[str, Vertretungsplan]

    @rx.event
    def dates_present(self):
        self.dates = len(self.vertretungsplaene) > 0

    def get_dates(self):
        vertretungsplan_dates = get_vertretungsplan_dates()
        self.vertretungsplaene = {
            datum.isoformat(): get_vertretungsplan_mattis(datum)
            for datum in vertretungsplan_dates
        }
        self.dates_present()


def show_table_header() -> rx.Component:
    return rx.table.header(
        rx.table.row(
            rx.table.column_header_cell("Klasse(n)"),
            rx.table.column_header_cell("Stunde(n)"),
            rx.table.column_header_cell("altes Fach"),
            rx.table.column_header_cell("neues Fach"),
            rx.table.column_header_cell("alter Raum"),
            rx.table.column_header_cell("neuer Raum"),
            rx.table.column_header_cell("Kommentar"),
            rx.table.column_header_cell("entfällt"),
        ),
    )


def show_table_row(event: VertretungsplanEvent) -> rx.Component:
    return rx.table.row(
        rx.table.cell(event.classes),
        rx.table.cell(event.lessons),
        rx.table.cell(event.previousSubject),
        rx.table.cell(event.subject),
        rx.table.cell(event.previousRoom),
        rx.table.cell(event.room),
        rx.table.cell(event.comment),
        rx.table.cell(
            rx.cond(
                event.canceled == "true",
                rx.text("X", color="red", weight="bold"),
                None
            ),
            align="center"
        )
    )


def show_table(vertretungsplan_tuple) -> rx.Component:
    return rx.vstack(
        rx.heading(f"Vertretungsplan für {vertretungsplan_tuple[0]}"),
        rx.table.root(
            show_table_header(),
            rx.foreach(
                vertretungsplan_tuple[1].events,
                show_table_row
            )
        )
    )


@template(route="/gymbroich", title="Gym. Broich", icon="school", on_load=State.get_dates())
def gymbroich_page() -> rx.Component:
    return rx.vstack(
            rx.cond(
                State.dates,
                rx.foreach(
                    State.vertretungsplaene, show_table
                ),
            )
        )
