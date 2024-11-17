from datetime import date

import reflex as rx
from babel.dates import format_date

from murkelhausen_app_v2.backend import fussballde
from murkelhausen_app_v2.templates.template import template


class FussballGame(rx.Base):
    game_date: date
    day: str
    time: str
    game_type: str
    home_team: str
    away_team: str
    result: str | None

    @classmethod
    def from_dict(cls, data: dict) -> "FussballGame":
        return cls(
            game_date=data["game_date"],
            day=format_date(data["game_date"], format="EEE, d.M.yyyy", locale="de_DE"),
            time=data["time"],
            game_type=data["game_type"],
            home_team=data["home_team"],
            away_team=data["away_team"],
            result=data["result"],
        )


class State(rx.State):
    f1_junioren: list[FussballGame]
    f3_junioren: list[FussballGame]
    speldorf: list[FussballGame]

    def update_termine(self):
        self.f1_junioren = [FussballGame.from_dict(game) for game in fussballde.get_erik_f1_junioren_next_games()]
        self.f3_junioren = [FussballGame.from_dict(game) for game in fussballde.get_erik_f3_junioren_next_games()]
        self.speldorf = [FussballGame.from_dict(game) for game in fussballde.get_speldorf_next_home_games()]


def show_game(game: FussballGame) -> rx.Component:
    color = rx.cond(
        game.game_date == date.today(),
        rx.color("yellow"),
        rx.color("gray"),
    )

    return rx.table.row(
        rx.table.cell(game.day),
        rx.table.cell(game.time),
        rx.table.cell(game.game_type),
        rx.table.cell(game.home_team),
        rx.table.cell(game.away_team),
        rx.table.cell(game.result),
        bg=color,
        style={"_hover": {"bg": color, "opacity": 0.5}},
        align="center",
    )


def show_table_header() -> rx.Component:
    return rx.table.header(
        rx.table.row(
            rx.table.column_header_cell("Tag"),
            rx.table.column_header_cell("Zeit"),
            rx.table.column_header_cell("Spieltyp"),
            rx.table.column_header_cell("Heim"),
            rx.table.column_header_cell("Gast"),
            rx.table.column_header_cell("Info"),
        ),
    )


@template(route="/fussball", title="VFB Speldorf", icon="trophy", on_load=State.update_termine)
def fussball() -> rx.Component:
    return rx.vstack(
        rx.heading("VFB Speldorf F1-Junioren"),
        rx.table.root(
            show_table_header(),
            rx.table.body(
                rx.foreach(
                    State.f1_junioren, show_game
                ),
            ),
            variant="surface",
            size="3",
        ),
        rx.heading("VFB Speldorf F3-Junioren"),
        rx.table.root(
            show_table_header(),
            rx.table.body(
                rx.foreach(
                    State.f3_junioren, show_game
                ),
            ),
            variant="surface",
            size="3",
        ),
        rx.heading("VFB Speldorf"),
        rx.table.root(
            show_table_header(),
            rx.table.body(
                rx.foreach(
                    State.speldorf, show_game
                ),
            ),
            variant="surface",
            size="3",
        ),
        width="100%",
    )
