import logging

import reflex as rx

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s - %(name)s - %(message)s"
)
log = logging.getLogger(__name__)

log.info("Starting app")
config = rx.Config(
    app_name="murkelhausen_app_v2",
    backend_port=8333,
)
