import logging
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta

import bs4
import requests

from murkelhausen_app_v2.config import config
from murkelhausen_app_v2.tasks.pushover import sent_pushover_message

AMOUNT_OF_DOCUMENTS = 3

log = logging.getLogger(__name__)


def get_session_cookie() -> str | None:
    r = requests.get(
        "https://terminvergabe.muelheim-ruhr.de/select2?md=4",
        timeout=10,
    )
    try:
        return r.cookies["tvo_session"]
    except KeyError:
        return None


@dataclass
class NextAppointment:
    date: str
    time: str


def get_appointment_page(session_cookie: str) -> str:
    headers = {"Cookie": f"tvo_session={session_cookie}"}
    r = requests.get(
        f"https://terminvergabe.muelheim-ruhr.de//location?mdt=128&select_cnc=1&cnc-2616=0&cnc-2491=0&cnc-2501={AMOUNT_OF_DOCUMENTS}&cnc-2503=0&cnc-2509=0&cnc-2615=0&cnc-2500=0&cnc-2502=0&cnc-2505=0&cnc-2498=0&cnc-2473=0&cnc-2474=0&cnc-2478=0&cnc-2488=0&cnc-2479=0&cnc-2483=0&cnc-2485=0&cnc-2496=0&cnc-2504=0&cnc-2486=0&cnc-2477=0&cnc-2475=0&cnc-2494=0&cnc-2481=0&cnc-2499=0&cnc-2472=0&cnc-2506=0&cnc-2490=0&cnc-2507=0&cnc-2508=0&cnc-2510=0",
        headers=headers,
        timeout=10,
    )

    soup = bs4.BeautifulSoup(r.text, "html.parser")
    suggest_location_summary = soup.find(
        "summary", id="suggest_location_summary"
    ).text.strip()
    return suggest_location_summary


def parse_appointment_page(text: str) -> NextAppointment:
    date_time_match = re.search(r"\b(\d{2}\.\d{2}\.\d{4}), (\d{2}:\d{2}) Uhr\b", text)
    if date_time_match:
        return NextAppointment(
            date=date_time_match.group(1), time=date_time_match.group(2)
        )
    return None


def check_if_date_is_within_x_days(date_str: str, x: int) -> bool:
    date_obj = datetime.strptime(date_str, "%d.%m.%Y").date()
    today = date.today()
    return today + timedelta(days=x) >= date_obj


def get_next_free_appointment_from_buergeramt():
    session_cookie = get_session_cookie()
    if session_cookie is None:
        raise ValueError("Failed to retrieve session cookie.")
    appointment_page = get_appointment_page(session_cookie)
    next_appointment = parse_appointment_page(appointment_page)

    if check_if_date_is_within_x_days(
        next_appointment.date, config.tasks.buergeramt_task.search_timeframe_days
    ):
        message = f"Nächster freier Termin für {AMOUNT_OF_DOCUMENTS} Dokumente: {next_appointment.date} at {next_appointment.time}"
        sent_pushover_message("FOO: Bürgeramt Termin Alarm:", message=message)
    else:
        log.info(
            f"No free appointment in timeframe of {config.tasks.buergeramt_task.search_timeframe_days} days found."
        )


if __name__ == "__main__":
    get_next_free_appointment_from_buergeramt()
