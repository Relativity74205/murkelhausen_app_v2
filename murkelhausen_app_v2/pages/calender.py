import reflex as rx

from murkelhausen_app_v2.templates.template import template


@template(
    route="/cal", title="Kalender", icon="calendar"
)
def calender() -> rx.Component:
    return rx.vstack(
        rx.html(
            """<iframe src="https://calendar.google.com/calendar/embed?src=arkadius.schuchhardt%40gmail.com&ctz=Europe%2FBerlin" style="border: 0" width="800" height="600" frameborder="0" scrolling="no"></iframe>"""
        ),
    )
