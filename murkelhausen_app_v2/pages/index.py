import reflex as rx

from murkelhausen_app_v2 import styles
from murkelhausen_app_v2.templates.template import template


@template(route="/", title="Startpage")
def index() -> rx.Component:
    return rx.vstack(
        rx.heading("Murkelhausen V2"),
        rx.card(
            rx.text("Today"),
            box_shadow=styles.box_shadow_style,
            size="3",
            width="100%",
        ),
        rx.card(
            rx.text("Tomorrow"),
            rx.card(
                rx.text("Morning"),
                size="3",
                width="100%",
            ),
            box_shadow=styles.box_shadow_style,
            size="3",
            width="100%",
        ),
        rx.card(
            rx.text("This week"),
            rx.card(
                rx.text("Morning"),
                size="3",
                width="100%",
            ),
            box_shadow=styles.box_shadow_style,
            size="3",
            width="100%",
        ),
        width="100%",
    )
