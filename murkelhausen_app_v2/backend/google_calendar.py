from datetime import date, datetime

import reflex as rx

from gcsa.google_calendar import GoogleCalendar


class Termin(rx.Base):
    event_name: str
    start_timestamp: datetime
    start_day: date
    start_time: str
    end_timestamp: datetime
    end_day: date
    end_time: str


def get_list_of_appointments() -> list[Termin]:
    gc = GoogleCalendar('arkadius.schuchhardt@gmail.com')
    raw_events = gc.get_events(time_min=date(2024, 11, 18), time_max=date(2024, 12, 19))

    events = []
    for event in raw_events:
        events.append(
            Termin(
                event_name=event.summary,
                start_timestamp=event.start,
                start_day=event.start.date(),
                start_time=str(event.start.time()),
                end_timestamp=event.end,
                end_day=event.end.date(),
                end_time=str(event.end.time())
            )
        )

    return events

