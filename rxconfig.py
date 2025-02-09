import logging
import os

import reflex as rx

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s - %(name)s - %(message)s"
)
log = logging.getLogger(__name__)

log.info("Starting app")

murkelhausen_datastore_username = os.environ.get("MURKELHAUSEN_DATASTORE_USERNAME", "")
murkelhausen_datastore_password = os.environ.get("MURKELHAUSEN_DATASTORE_PASSWORD", "")
config = rx.Config(
    app_name="murkelhausen_app_v2",
    db_url=f"postgresql+psycopg://{murkelhausen_datastore_username}:{murkelhausen_datastore_password}@192.168.1.69:5432/murkelhausen_datastore",
    backend_port=8333,
)
