from datetime import date, datetime
import logging

import reflex as rx
import requests
from babel.dates import format_date
from cachetools import TTLCache, cached

from murkelhausen_app_v2.config import config

logger = logging.getLogger(__name__)


class VertretungsplanEvent(rx.Base):
    classes: str
    lessons: str
    previousSubject: str | None
    subject: str | None
    previousRoom: str | None
    room: str | None
    previousTeacher: str | None
    teacher: str | None
    comment: str
    canceled: str


class Vertretungsplan(rx.Base):
    datum: str
    timestamp_aktualisiert: str
    infos: list[str]
    infos_present: bool
    events: list[VertretungsplanEvent]
    events_present: bool


@cached(cache=TTLCache(maxsize=1, ttl=60))  # 1 minute
def get_vertretungsplan_dates() -> tuple[date, ...]:
    url = "https://assets.gymnasium-broich.de/vplan/api/dates"
    data = requests.get(url, timeout=config.gym_broich.request_timeout).json()
    logger.info(
        f"Retrieved {len(data)} dates of the Vertretungsplan API for which Vertretungsplaene exist."
    )

    return tuple(date.fromisoformat(d) for d in data)


def replace_empty_str_with_none(v: str) -> str | None:
    if v == "":
        return None
    return v


@cached(cache=TTLCache(maxsize=1, ttl=60))  # 1 minute
def get_vertretungsplan(vertretungsplan_date: date) -> Vertretungsplan:
    base_url = "https://assets.gymnasium-broich.de/vplan/api/"
    data: dict = requests.get(base_url + vertretungsplan_date.isoformat()).json()
    logger.info(f"Retrieved Vertretungsplan for {vertretungsplan_date}.")

    events = []
    for event in data["events"]:
        text, canceled_string = event["texts"]
        canceled = True if canceled_string.strip() == "x" else False
        event = VertretungsplanEvent(
            classes=", ".join([ele.strip() for ele in event["classes"]]),
            lessons=", ".join([str(ele) for ele in event["lessons"]]),
            previousRoom=replace_empty_str_with_none(event["previousRoom"]),
            previousSubject=replace_empty_str_with_none(event["previousSubject"]),
            previousTeacher=replace_empty_str_with_none(event["previousTeacher"]),
            room=replace_empty_str_with_none(event["room"]),
            subject=replace_empty_str_with_none(event["subject"]),
            teacher=replace_empty_str_with_none(event["teacher"]),
            comment=text,
            canceled="true" if canceled else "no",
        )
        events.append(event)

    events_parsed = []
    event_index = 0
    while event_index < len(events):
        if event_index == len(events) - 1:
            events_parsed.append(events[event_index])
            event_index += 1
            continue

        this_event = events[event_index]
        next_event = events[event_index + 1]
        if next_event.lessons == "0":
            this_event.comment += " " + next_event.comment
            event_index += 1

        events_parsed.append(this_event)
        event_index += 1

    return Vertretungsplan(
        datum=format_date(
            date.fromisoformat(data["date"]), format="EEE, d.M.yyyy", locale="de_DE"
        ),
        timestamp_aktualisiert=datetime.fromisoformat(data["version"]).strftime(
            "%d.%m.%Y %H:%M:%S"
        ),
        infos=data["infos"],
        infos_present=len(data["infos"]) > 0,
        events=events_parsed,
        events_present=len(events_parsed) > 0,
    )


def get_full_class_of_mattis() -> str:
    current_year = datetime.now().year
    current_month = datetime.now().month
    if current_month < 7:
        current_year -= 1

    current_jahrgang = current_year - config.gym_broich.year_started_mattis + 5
    return f"{current_jahrgang}{config.gym_broich.class_suffix_mattis}"


def get_vertretungsplan_mattis(vertretungsplan_date: date) -> Vertretungsplan:
    vertretungsplan = get_vertretungsplan(vertretungsplan_date)
    filtered_events = [
        event
        for event in vertretungsplan.events
        if get_full_class_of_mattis() in event.classes
    ]
    return Vertretungsplan(
        datum=vertretungsplan.datum,
        timestamp_aktualisiert=vertretungsplan.timestamp_aktualisiert,
        infos=vertretungsplan.infos,
        infos_present=vertretungsplan.infos_present,
        events=filtered_events,
        events_present=len(filtered_events) > 0,
    )
