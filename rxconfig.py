import logging

import reflex as rx

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

log.info("Starting app")
config = rx.Config(
    app_name="murkelhausen_app_v2",
    backend_port=8333,
)
