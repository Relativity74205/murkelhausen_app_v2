import logging

import requests

from murkelhausen_app_v2.config import config

log = logging.getLogger(__name__)


def sent_pushover_message(title: str, message: str):
    data = {
        "token": config.pushover.token.get_secret_value(),
        "user": config.pushover.user_key.get_secret_value(),
        "device": "fp4",
        "title": title,
        "message": message,
        # "priority": 2,
        # "expire": 1800,
        # "retry": 60,
    }
    r = requests.post(
        "https://api.pushover.net/1/messages.json",
        data=data,
        timeout=10,
    )
    log.info(f"Pushover response: {r.text}; {r.status_code=}")
    if r.status_code != 200:
        raise RuntimeError(f"Pushover request failed with status code {r.status_code}")
