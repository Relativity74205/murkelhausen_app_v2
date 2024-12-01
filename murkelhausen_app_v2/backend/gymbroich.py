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
    events: list[VertretungsplanEvent]


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
def get_vertretungsplan(datum: date) -> Vertretungsplan:
    base_url = "https://assets.gymnasium-broich.de/vplan/api/"
    data: dict = requests.get(base_url + datum.isoformat()).json()
    logger.info(f"Retrieved Vertretungsplan for {datum}.")

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
        events=events_parsed,
    )


def get_vertretungsplan_mattis(datum: date) -> Vertretungsplan:
    vertretungsplan = get_vertretungsplan(datum)
    filtered_events = [
        event
        for event in vertretungsplan.events
        if config.gym_broich.class_of_mattis in event.classes
    ]
    return Vertretungsplan(
        datum=vertretungsplan.datum,
        timestamp_aktualisiert=vertretungsplan.timestamp_aktualisiert,
        infos=vertretungsplan.infos,
        events=filtered_events,
    )
