import reflex as rx

from murkelhausen_app_v2.backend.ruhrbahn import Departure, get_lierberg_departure_data
from murkelhausen_app_v2.templates.template import template


class State(rx.State):
    departures: list[Departure]

    def get_departures(self):
        self.departures = get_lierberg_departure_data()


def show_departure(departure: Departure):
    color = rx.cond(
        departure.delay >= 5,  # TODO(arkadius): move to config
        rx.color("orange"),
        rx.cond(
            departure.delay > 1,
            rx.color("yellow"),
            rx.color("gray"),
        ),
    )

    return rx.table.row(
        rx.table.cell(departure.line),
        rx.table.cell(departure.departure_time),
        rx.table.cell(rx.cond(departure.delay == 0, "", departure.delay)),
        rx.table.cell(departure.platform),
        rx.table.cell(departure.richtung),
        bg=color,
        style={"_hover": {"bg": color, "opacity": 0.5}},
        align="center",
    )


@template(route="/ruhrbahn", title="Bus", icon="bus")
def ruhrbahn_page() -> rx.Component:
    return rx.vstack(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Linie"),
                    rx.table.column_header_cell("Abfahrt"),
                    rx.table.column_header_cell("Verspätung"),
                    rx.table.column_header_cell("Gleis"),
                    rx.table.column_header_cell("Richtung"),
                ),
            ),
            rx.table.body(
                rx.foreach(State.departures, show_departure),
            ),
            variant="surface",
            on_mount=State.get_departures,
            size="3",
        ),
        width="100%",
    )
