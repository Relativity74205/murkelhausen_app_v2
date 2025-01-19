import logging
from contextlib import asynccontextmanager

import reflex as rx

from murkelhausen_app_v2 import styles
from murkelhausen_app_v2.pages import *  # noqa
from murkelhausen_app_v2.tasks import scheduler

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app):
    log.info("Starting scheduler")
    scheduler.start()
    log.info("Scheduler started")
    yield
    log.info("Shutting down scheduler")
    scheduler.shutdown()
    log.info("Scheduler shut down")


app = rx.App(
    style=styles.base_style,
    stylesheets=styles.base_stylesheets,
)
app.register_lifespan_task(lifespan)
