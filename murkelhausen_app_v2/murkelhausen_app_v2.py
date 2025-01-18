from contextlib import asynccontextmanager

import reflex as rx

from murkelhausen_app_v2 import styles
from murkelhausen_app_v2.tasks import scheduler


@asynccontextmanager
async def lifespan(app):
    scheduler.start()
    yield
    scheduler.shutdown()


app = rx.App(
    style=styles.base_style,
    stylesheets=styles.base_stylesheets,
)
app.register_lifespan_task(lifespan)
