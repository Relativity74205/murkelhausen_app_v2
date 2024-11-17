from datetime import date

import reflex as rx

from murkelhausen_app_v2.backend import handballnordrhein
from murkelhausen_app_v2.backend.mheg import BASE_URL
from murkelhausen_app_v2.templates.template import template


BASE_URL = "https://hnr-handball.liga.nu/"


class State(rx.State):
    d_jugend: list[handballnordrhein.HandballGame]

    @rx.event
    def update_termine(self):
        self.d_jugend = handballnordrhein.get_djk_saarn_d_jugend()


def show_game(game: handballnordrhein.HandballGame) -> rx.Component:
    color = rx.cond(
        game.game_date == date.today(),
        rx.color("yellow"),
        rx.color("gray"),
    )

    return rx.table.row(
        rx.table.cell(game.game_date_formatted),
        rx.table.cell(game.time),
        rx.table.cell(game.home_team),
        rx.table.cell(game.away_team),
        rx.table.cell(
            rx.cond(
                game.link_to_spielbericht is not None and game.result != "WH",
                rx.link(
                    game.result,
                    href=BASE_URL + game.link_to_spielbericht,
                    is_external=True,
                ),
                rx.text(game.result),
            ),
            align="center",
        ),
        bg=color,
        style={"_hover": {"bg": color, "opacity": 0.5}},
        align="center",
    )


def show_table_header() -> rx.Component:
    return rx.table.header(
        rx.table.row(
            rx.table.column_header_cell("Tag"),
            rx.table.column_header_cell("Zeit"),
            rx.table.column_header_cell("Heim"),
            rx.table.column_header_cell("Gast"),
            rx.table.column_header_cell("Ergebnis", align="center"),
        ),
    )


@template(route="/handball", title="DJK Saarn", icon="trophy")
def handball() -> rx.Component:
    return rx.vstack(
        rx.heading("DJK Saarn D-Jugend"),
        rx.table.root(
            show_table_header(),
            rx.table.body(
                rx.foreach(State.d_jugend, show_game),
            ),
            on_mount=State.update_termine,
            variant="surface",
            size="3",
        ),
        width="100%",
    )
