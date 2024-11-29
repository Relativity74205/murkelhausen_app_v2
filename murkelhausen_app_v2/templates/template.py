"""Common templates used between pages in the app."""

from __future__ import annotations
from typing import Callable

from murkelhausen_app_v2.components.navbar import navbar
from murkelhausen_app_v2 import styles
from murkelhausen_app_v2.components.sidebar import sidebar

import reflex as rx


def menu_item_link(text, href):
    return rx.menu.item(
        rx.link(
            text,
            href=href,
            width="100%",
            color="inherit",
        ),
        _hover={
            "color": styles.accent_color,
            "background_color": styles.accent_text_color,
        },
    )


class ThemeState(rx.State):
    """The state for the theme of the app."""

    accent_color: str = "crimson"

    gray_color: str = "gray"

    radius: str = "large"

    scaling: str = "100%"


def template(
    route: str | None = None,
    title: str | None = None,
    description: str | None = None,
    meta: str | None = None,
    icon: str | None = None,
    script_tags: list[rx.Component] | None = None,
    on_load: rx.event.EventHandler | list[rx.event.EventHandler] | None = None,
) -> Callable[[Callable[[], rx.Component]], rx.Component]:
    """The template for each page of the app.

    Args:
        route: The route to reach the page.
        title: The title of the page.
        description: The description of the page.
        meta: Additional meta to add to the page.
        icon: TODO
        on_load: The event handler(s) called when the page load.
        script_tags: Scripts to attach to the page.

    Returns:
        The template with the page content.
    """

    def decorator(page_content: Callable[[], rx.Component]) -> rx.Component:
        """The template for each page of the app.

        Args:
            page_content: The content of the page.

        Returns:
            The template with the page content.
        """
        # Get the meta tags for the page.
        default_meta = [
            {
                "name": "viewport",
                "content": "width=device-width, shrink-to-fit=no, initial-scale=1",
            },
        ]
        all_meta = default_meta
        if icon:
            all_meta[0]["icon"] = icon

        def templated_page():
            return rx.flex(
                sidebar(),
                rx.flex(
                    rx.vstack(
                        navbar(),
                        page_content(),
                        width="100%",
                        **styles.template_content_style,
                    ),
                    width="100%",
                    **styles.template_page_style,
                    max_width=[
                        "100%",
                        "100%",
                        styles.max_width,
                    ],
                ),
                width="100%",
                margin="auto",
                position="relative",
            )

        @rx.page(
            route=route,
            title=title,
            description=description,
            meta=all_meta,
            script_tags=script_tags,
            on_load=on_load,
        )
        def theme_wrap():
            return rx.theme(
                templated_page(),
                has_background=True,
                accent_color=ThemeState.accent_color,
                gray_color=ThemeState.gray_color,
                radius=ThemeState.radius,
                scaling=ThemeState.scaling,
            )

        return theme_wrap

    return decorator
