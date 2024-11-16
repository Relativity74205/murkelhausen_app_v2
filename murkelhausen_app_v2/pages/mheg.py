from datetime import date

import reflex as rx

from murkelhausen_app_v2.backend import MuellTermine, get_muelltermine_for_this_week, get_muelltermine_for_home
from murkelhausen_app_v2.config import config
from murkelhausen_app_v2.templates.template import template


class Termin(rx.Base):
    art: str
    datum: str
    delta_days: int

    @classmethod
    def from_muelltermine(cls, muelltermine: MuellTermine) -> "Termin":
        return cls(
            art=muelltermine.art,
            datum=muelltermine.day,
            delta_days=muelltermine.delta_days,
        )


def get_termine():
    termine = get_muelltermine_for_home()
    return [Termin.from_muelltermine(termin) for termin in termine]


class State(rx.State):
    termine: list[Termin] = get_termine()


def show_termin(termin: Termin):
    """Show a user in a table row."""
    color = rx.cond(
        termin.delta_days <= config.mheg.alert_days,
        rx.color("yellow"),
        rx.color("gray"),
    )

    return rx.table.row(
        rx.table.cell(termin.art),
        rx.table.cell(termin.datum),
        rx.table.cell(termin.delta_days),
        bg=color,
        style={"_hover": {"bg": color, "opacity": 0.5}},
        align="center",
    )


@template(route="/mheg", title="MHEG", icon="calendar")
def mheg() -> rx.Component:
    return rx.vstack(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Tonne"),
                    rx.table.column_header_cell("Datum"),
                    rx.table.column_header_cell("Tage"),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    State.termine, show_termin
                ),
            ),
            variant="surface",
            size="3",
            # width="100%",
        ),
        align="center",
        width="100%",
    )