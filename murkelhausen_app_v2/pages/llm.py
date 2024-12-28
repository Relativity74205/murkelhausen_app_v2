
import reflex as rx

from murkelhausen_app_v2.templates.template import template


@template(
    route="/llm",
    title="Chat",
    icon="message-square",
)
def llm_page() -> rx.Component:
    return rx.vstack(
        rx.heading("ChatGPT"),
        rx.el.Iframe(
            src="http://192.168.1.69:3000/",
            width="100%", height=600, style={"border": "0"}, frameborder="0", scrolling="yes"
        ),
        width="100%",
    )
