"""Sidebar component for the app."""

import reflex as rx

from murkelhausen_app_v2 import styles


class State(rx.State):
    version: str

    def load_pyproject_toml(self):
        with open("pyproject.toml") as f:
            lines = f.readlines()
            try:
                self.version = lines[2].split("=")[1].strip().replace('"', "")
            except (IndexError, TypeError):
                self.version = "unknown"


def sidebar_header() -> rx.Component:
    return rx.hstack(
        rx.spacer(),
        align="center",
        width="100%",
        padding="0.35em",
        margin_bottom="1em",
    )


def sidebar_footer() -> rx.Component:
    return rx.hstack(
        rx.color_mode.button(style={"opacity": "0.8", "scale": "0.95"}),
        rx.spacer(),
        rx.text(f"version {State.version}"),
        justify="start",
        align="center",
        width="100%",
        padding="0.35em",
        on_mount=State.load_pyproject_toml,
    )


def sidebar_item(text: str, url: str, icon: str) -> rx.Component:
    active = (rx.State.router.page.path == url.lower()) | (
        (rx.State.router.page.path == "/") & text == "Overview"
    )
    if icon is None:
        icon = "layout-dashboard"

    return rx.link(
        rx.hstack(
            rx.icon(icon, size=18),
            rx.text(text, size="3", weight="regular"),
            color=rx.cond(
                active,
                styles.accent_text_color,
                styles.text_color,
            ),
            style={
                "_hover": {
                    "background_color": rx.cond(
                        active,
                        styles.accent_bg_color,
                        styles.gray_bg_color,
                    ),
                    "color": rx.cond(
                        active,
                        styles.accent_text_color,
                        styles.text_color,
                    ),
                    "opacity": "1",
                },
                "opacity": rx.cond(
                    active,
                    "1",
                    "0.95",
                ),
            },
            align="center",
            border_radius=styles.border_radius,
            width="100%",
            spacing="2",
            padding="0.35em",
        ),
        underline="none",
        href=url,
        width="100%",
    )


def sidebar() -> rx.Component:
    from reflex.page import get_decorated_pages

    # The ordered page routes.
    ordered_page_routes = [
        "/",
        "/table",
        "/about",
        "/profile",
        "/settings",
    ]

    # Get the decorated pages.
    pages = get_decorated_pages()

    # Include all pages even if they are not in the ordered_page_routes.
    ordered_pages = sorted(
        pages,
        key=lambda page: (
            ordered_page_routes.index(page["route"])
            if page["route"] in ordered_page_routes
            else len(ordered_page_routes)
        ),
    )

    return rx.flex(
        rx.vstack(
            sidebar_header(),
            rx.vstack(
                *[
                    sidebar_item(
                        text=page.get("title", page["route"].strip("/").capitalize()),
                        icon=page.get("meta")[0].get("icon"),
                        url=page["route"],
                    )
                    for page in ordered_pages
                ],
                spacing="1",
                width="100%",
            ),
            rx.spacer(),
            sidebar_footer(),
            justify="end",
            align="end",
            width=styles.sidebar_content_width,
            height="100dvh",
            padding="1em",
        ),
        # display=["none", "none", "none", "none", "none", "flex"],
        max_width=styles.sidebar_width,
        width="auto",
        height="100%",
        position="sticky",
        justify="end",
        top="0px",
        left="0px",
        flex="1",
        bg=rx.color("gray", 2),
    )
