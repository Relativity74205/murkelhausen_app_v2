import reflex as rx

from murkelhausen_app_v2.templates.template import template


@template(route="/", title="Startpage")
def index() -> rx.Component:
    return rx.text("Welcome")
