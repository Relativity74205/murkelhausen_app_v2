from datetime import date, datetime

import reflex as rx
from babel.dates import format_date
from dateutil.relativedelta import relativedelta
from gcsa.event import Event

from gcsa.google_calendar import GoogleCalendar
from google.oauth2 import service_account

from murkelhausen_app_v2.config import config


class Termin(rx.Base):
    id: str
    event_name: str
    start_timestamp: datetime | None
    start_day: date
    start_day_string: str | None
    start_time: str | None
    end_timestamp: datetime | None
    end_day: date
    end_time: str | None
    whole_day: bool


SCOPES = [
    "https://www.googleapis.com/auth/calendar",
]


def get_google_calendar_client() -> GoogleCalendar:
    private_key = config.google.api_key.replace("\\n", "\n")
    info = {
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "client_email": config.google.client_email,
        "client_id": config.google.client_id,
        "client_x509_cert_url": config.google.client_x509_cert_url,
        "private_key": private_key,
        "private_key_id": config.google.private_key_id,
        "project_id": config.google.project_id,
        "token_uri": "https://oauth2.googleapis.com/token",
        "type": "service_account",
        "universe_domain": "googleapis.com",
    }

    credentials = service_account.Credentials.from_service_account_info(
        info, scopes=SCOPES
    )

    gc = GoogleCalendar(
        credentials=credentials, default_calendar="arkadius.schuchhardt@gmail.com"
    )
    return gc


def create_appointment(event: Event):
    gc = get_google_calendar_client()
    gc.add_event(event)


def delete_appointment(event: Event):
    gc = get_google_calendar_client()
    gc.delete_event(event)


def get_list_of_appointments() -> list[Termin]:
    gc = get_google_calendar_client()
    today = date.today()
    raw_events = gc.get_events(time_min=today, time_max=today + relativedelta(weeks=2))

    events = []
    for event in raw_events:
        start_day_string = format_date(event.start, format="dd.M.yyyy (EEE)", locale="de_DE")
        if type(event.start) is date:
            termin = Termin(
                id=event.id,
                event_name=event.summary,
                start_timestamp=None,
                start_day=event.start,
                start_day_string=start_day_string,
                start_time=None,
                end_timestamp=None,
                end_day=event.end,
                end_time=None,
                whole_day=True,
            )
        else:
            termin = Termin(
                id=event.id,
                event_name=event.summary,
                start_timestamp=event.start,
                start_day=event.start.date(),
                start_time=str(event.start.strftime("%H:%M")),
                start_day_string=start_day_string,
                end_timestamp=event.end,
                end_day=event.end.date(),
                end_time=str(event.end.strftime("%H:%M")),
                whole_day=False,
            )
        events.append(
            termin
        )

    return sorted(events, key=lambda x: (x.start_day, x.start_time is not None, x.start_time))


if __name__ == "__main__":
    for ele in get_list_of_appointments():
        print(ele.event_name, ele.start_day, ele.whole_day)
