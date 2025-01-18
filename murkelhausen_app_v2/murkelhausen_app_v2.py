from contextlib import asynccontextmanager

import reflex as rx

from murkelhausen_app_v2 import styles
from murkelhausen_app_v2.tasks import scheduler


@asynccontextmanager
async def lifespan(app):
    print("Starting scheduler")
    scheduler.start()
    print("Scheduler started")
    yield
    print("Shutting down scheduler")
    scheduler.shutdown()
    print("Scheduler shut down")


app = rx.App(
    style=styles.base_style,
    stylesheets=styles.base_stylesheets,
)
app.register_lifespan_task(lifespan)
