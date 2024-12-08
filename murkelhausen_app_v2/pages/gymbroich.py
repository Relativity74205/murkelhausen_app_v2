import reflex as rx

from murkelhausen_app_v2.templates.template import template
from murkelhausen_app_v2.backend.gymbroich import (
    Vertretungsplan,
    get_vertretungsplan_dates,
    VertretungsplanEvent,
    get_vertretungsplan_mattis,
    get_vertretungsplan, get_full_class_of_mattis,
)


class State(rx.State):
    dates: bool = False
    vertretungsplaene_all: dict[str, Vertretungsplan]
    vertretungsplaene_mattis: dict[str, Vertretungsplan]
    updated_at: str

    @rx.event
    def dates_present(self):
        self.dates = len(self.vertretungsplaene_mattis) > 0

    @rx.event()
    def get_dates(self):
        # TODO: make this a background task
        vertretungsplan_dates = get_vertretungsplan_dates()
        self.vertretungsplaene_all = {
            datum.isoformat(): get_vertretungsplan(datum)
            for datum in vertretungsplan_dates
        }
        self.vertretungsplaene_mattis = {
            datum.isoformat(): get_vertretungsplan_mattis(datum)
            for datum in vertretungsplan_dates
        }
        if self.vertretungsplaene_mattis:
            self.updated_at = {plan.timestamp_aktualisiert for plan in self.vertretungsplaene_mattis.values()}.pop()
        else:
            self.updated_at = ""
        self.dates_present()


def show_table_header() -> rx.Component:
    return rx.table.header(
        rx.table.row(
            rx.table.column_header_cell("Klasse(n)"),
            rx.table.column_header_cell("Stunde(n)"),
            rx.table.column_header_cell("altes Fach"),
            rx.table.column_header_cell("alter Raum"),
            rx.table.column_header_cell("entfällt"),
            rx.table.column_header_cell("neues Fach"),
            rx.table.column_header_cell("neuer Raum"),
            rx.table.column_header_cell("Kommentar"),
        ),
    )


def show_table_row(event: VertretungsplanEvent) -> rx.Component:
    color = rx.color("gray")
    return rx.table.row(
        rx.table.cell(event.classes),
        rx.table.cell(event.lessons),
        rx.table.cell(event.previousSubject),
        rx.table.cell(event.previousRoom),
        rx.table.cell(
            rx.cond(
                event.canceled == "true", rx.text("X", color="red", weight="bold"), None
            ),
            align="center",
        ),
        rx.table.cell(event.subject),
        rx.table.cell(event.room),
        rx.table.cell(event.comment),
        bg=color,
        style={"_hover": {"bg": color, "opacity": 0.5}},
    )


def show_infos(vertretungsplan: Vertretungsplan) -> rx.Component:
    return rx.cond(
            vertretungsplan.infos_present,
            rx.vstack(
                rx.heading("Infos", size="4"),
                rx.list.unordered(
                    rx.foreach(vertretungsplan.infos, lambda info: rx.list.item(info)),
                ),
            ),
            None,
        )


def show_table(vertretungsplan_tuple) -> rx.Component:
    return rx.vstack(
        rx.heading(vertretungsplan_tuple[1].datum),
        show_infos(vertretungsplan_tuple[1]),
        rx.heading("Vertretungen", size="4"),
        rx.table.root(
            show_table_header(),
            rx.foreach(vertretungsplan_tuple[1].events, show_table_row),
            variant="surface",
            size="2",
        ),
    )


def show_tab_content(state_var, tab_name: str) -> rx.Component:
    return rx.tabs.content(
        rx.vstack(
            rx.heading(f"Vertretungsplan {tab_name}"),
            rx.cond(
                State.dates,
                rx.foreach(state_var, show_table),
            )
        ),
        value=tab_name,
    )


@template(
    route="/gymbroich", title="Gym. Broich", icon="school", on_load=State.get_dates()
)
def gymbroich_page() -> rx.Component:
    MATTIS_TAB = f"Mattis ({get_full_class_of_mattis()})"
    ALL_TAB = "Komplett"

    return rx.vstack(
        rx.text(f"Stand: {State.updated_at}"),
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger(MATTIS_TAB, value=MATTIS_TAB),
                rx.tabs.trigger(ALL_TAB, value=ALL_TAB),
            ),
        show_tab_content(State.vertretungsplaene_mattis, MATTIS_TAB),
        show_tab_content(State.vertretungsplaene_all, ALL_TAB),
        default_value=MATTIS_TAB,
    ))
