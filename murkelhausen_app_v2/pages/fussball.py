from datetime import date, datetime, timedelta
from functools import partial
import logging

import reflex as rx
from babel.dates import format_date
from gcsa.event import Event

from murkelhausen_app_v2.backend import fussballde
from murkelhausen_app_v2.backend.google_calendar import create_appointment_if_not_exists
from murkelhausen_app_v2.config import config
from murkelhausen_app_v2.templates.template import template

log = logging.getLogger(__name__)


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
    speldorf: list[FussballGame]

    def update_termine(self):
        self.f1_junioren = [
            FussballGame.from_dict(game)
            for game in fussballde.get_erik_f1_junioren_next_games()
        ]
        self.speldorf = [
            FussballGame.from_dict(game)
            for game in fussballde.get_speldorf_next_home_games()
        ]

    @rx.event
    def add_to_calendar(self, game: FussballGame):
        game_time = datetime.combine(
            game.game_date, datetime.strptime(game.time.split(" ")[0], "%H:%M").time()
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
                calendar_id=config.google.calendars["Erik"],
            )
            yield rx.toast(
                f"Termin hinzugefügt: {game.home_team} vs {game.away_team} am {game.game_date} um {game.time}"
            )
            return
        except ValueError:
            yield rx.toast("Termin bereits vorhanden", level="error")
            return


def show_game_without_calendar_col(game: FussballGame) -> rx.Component:
    return show_game(game, show_calendar_col=False)


def show_game_with_calendar_col(game: FussballGame) -> rx.Component:
    return show_game(game, show_calendar_col=True)


def show_game(game: FussballGame, show_calendar_col: bool) -> rx.Component:
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
        rx.cond(
            show_calendar_col,
            rx.table.cell(
                rx.button(
                    "Zum Kalender hinzufügen",
                    on_click=State.add_to_calendar(game),
                )
            ),
            None,
        ),
        bg=color,
        style={"_hover": {"bg": color, "opacity": 0.5}},
        align="center",
    )


def show_table_header(show_calendar_col: bool) -> rx.Component:
    return rx.table.header(
        rx.table.row(
            rx.table.column_header_cell("Tag"),
            rx.table.column_header_cell("Zeit"),
            rx.table.column_header_cell("Spieltyp"),
            rx.table.column_header_cell("Heim"),
            rx.table.column_header_cell("Gast"),
            rx.table.column_header_cell("Info"),
            rx.cond(
                show_calendar_col,
                rx.table.column_header_cell("Zum Kalender hinzufügen"),
                None,
            ),
        ),
    )


@template(
    route="/fussball", title="VFB Speldorf", icon="trophy", on_load=State.update_termine
)
def fussball() -> rx.Component:
    return rx.vstack(
        rx.heading("VFB Speldorf F1-Junioren"),
        rx.link(
            "Link",
            href="https://www.fussball.de/mannschaft/vfb-speldorf-vfb-speldorf-niederrhein/-/saison/2425/team-id/011MI9USJ8000000VTVG0001VTR8C1K7#!/",
            is_external=True,
        ),
        rx.table.root(
            show_table_header(show_calendar_col=True),
            rx.table.body(
                rx.foreach(State.f1_junioren, show_game_with_calendar_col),
            ),
            variant="surface",
            size="3",
        ),
        rx.heading("VFB Speldorf Heimspiele"),
        rx.link(
            "Link",
            href="https://www.fussball.de/verein/vfb-speldorf-niederrhein/-/id/00ES8GN8VS000030VV0AG08LVUPGND5I#!/",
            is_external=True,
        ),
        rx.table.root(
            show_table_header(show_calendar_col=False),
            rx.table.body(
                rx.foreach(State.speldorf, show_game_without_calendar_col),
            ),
            variant="surface",
            size="3",
        ),
        width="100%",
    )
