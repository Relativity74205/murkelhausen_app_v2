from datetime import date, datetime, timedelta

import reflex as rx
from gcsa.event import Event

from murkelhausen_app_v2.backend import handballnordrhein
from murkelhausen_app_v2.backend.google_calendar import create_appointment_if_not_exists
from murkelhausen_app_v2.config import config
from murkelhausen_app_v2.templates.template import template


class State(rx.State):
    d_jugend: list[handballnordrhein.HandballGame]
    erste_herren: list[handballnordrhein.HandballGame]

    @rx.event
    def update_termine_d_jugend(self):
        self.d_jugend = handballnordrhein.get_djk_saarn_d_jugend()

    @rx.event
    def update_termine_erste_herren(self):
        self.erste_herren = handballnordrhein.get_djk_saarn_erste_herren()

    @rx.event
    def add_to_calendar(self, game: handballnordrhein.HandballGame):
        if game.spielfrei is True:
            yield rx.toast("Spiel ist spielfrei", level="error")
            return

        game_date = datetime.strptime(
            game.game_date_formatted.split(" ")[1], "%d.%m.%Y"
        ).date()
        game_time = datetime.combine(
            game_date, datetime.strptime(game.time, "%H:%M").time()
        )
        start = game_time
        end = game_time + timedelta(hours=1.5)
        try:
            create_appointment_if_not_exists(
                event=Event(
                    summary=game.home_team + " vs " + game.away_team,
                    start=start,
                    end=end,
                ),
                calendar_id=config.google.calendars["Mattis"],
            )
            yield rx.toast("Termin hinzugefügt", level="success")
        except ValueError:
            yield rx.toast("Termin bereits vorhanden", level="error")


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
                    href=handballnordrhein.BASE_URL + game.link_to_spielbericht,
                    is_external=True,
                ),
                rx.text(game.result),
            ),
            align="center",
        ),
        rx.table.cell(
            rx.cond(
                game.spielfrei == False,
                rx.button(
                    "Zum Kalender hinzufügen",
                    on_click=State.add_to_calendar(game),
                ),
                None,
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
            rx.table.column_header_cell("Zum Kalender hinzufügen", align="center"),
        ),
    )


def show_d_jugend() -> rx.Component:
    return rx.vstack(
        rx.heading("DJK Saarn D-Jugend"),
        rx.link(
            "Zum Handballverband",
            href=handballnordrhein.get_d_jugend_url(),
            is_external=True,
        ),
        rx.table.root(
            show_table_header(),
            rx.table.body(
                rx.foreach(State.d_jugend, show_game),
            ),
            on_mount=State.update_termine_d_jugend,
            variant="surface",
            size="3",
        ),
        width="100%",
    )


def show_erste_herren() -> rx.Component:
    return rx.vstack(
        rx.heading("DJK Saarn 1. Herren"),
        rx.link(
            "Zum Handballverband",
            href=handballnordrhein.get_erste_herren(),
            is_external=True,
        ),
        rx.table.root(
            show_table_header(),
            rx.table.body(
                rx.foreach(State.erste_herren, show_game),
            ),
            on_mount=State.update_termine_erste_herren,
            variant="surface",
            size="3",
        ),
        width="100%",
    )


@template(route="/handball", title="DJK Saarn", icon="trophy")
def handball() -> rx.Component:
    return rx.tabs.root(
        rx.tabs.list(
            rx.tabs.trigger(
                "D-Jugend",
                value="d_jugend",
            ),
            rx.tabs.trigger(
                "1. Herren",
                value="herren",
            ),
        ),
        rx.tabs.content(
            show_d_jugend(),
            value="d_jugend",
        ),
        rx.tabs.content(
            show_erste_herren(),
            value="herren",
        ),
        default_value="d_jugend",
    )
