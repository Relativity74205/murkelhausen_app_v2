from datetime import date, datetime
from enum import Enum

import pytz
import reflex as rx
from babel.dates import format_date
from dateutil.relativedelta import relativedelta
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from google.oauth2 import service_account

from murkelhausen_app_v2.config import config


class AppointmentRecurrenceType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class AppointmentRecurrence(rx.Base):
    recurrence_type: AppointmentRecurrenceType
    recurrence_interval: int
    recurrence_end: datetime | None


class Appointment(rx.Base):
    id: str | None
    event_name: str
    start_timestamp: datetime
    start_day_string: str
    start_time: str
    end_timestamp: datetime
    end_day_string: str
    end_time: str
    whole_day: bool
    recurring: AppointmentRecurrence | None


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


def create_appointment(event: Event, calendar_id: str):
    gc = get_google_calendar_client()
    gc.add_event(event, calendar_id=calendar_id)


def update_appointment(event: Event, calendar_id: str):
    gc = get_google_calendar_client()
    gc.update_event(event, calendar_id=calendar_id)


def delete_appointment(event: Event, calendar_id: str):
    gc = get_google_calendar_client()
    gc.delete_event(event, calendar_id=calendar_id)


def get_list_of_appointments(calendar_id: str) -> list[Appointment]:
    gc = get_google_calendar_client()
    today = date.today()

    # TODO: Configure timeframe for retrieving events
    time_min = today
    time_max = today + relativedelta(weeks=2)
    raw_events = gc.get_events(
        calendar_id=calendar_id, time_min=time_min, time_max=time_max
    )

    events = []
    for event in raw_events:
        start_day_string = format_date(
            event.start, format="dd.MM.yyyy (EEE)", locale="de_DE"
        )
        end_day_string = format_date(
            event.end, format="dd.MM.yyyy (EEE)", locale="de_DE"
        )
        # TODO: add recurrence
        if type(event.start) is date:
            start_timestamp = datetime.combine(
                event.start, datetime.min.time()
            ).astimezone(pytz.timezone("Europe/Berlin"))
            end_timestamp = datetime.combine(event.end, datetime.min.time()).astimezone(
                pytz.timezone("Europe/Berlin")
            )
            whole_day = True
        else:
            start_timestamp = event.start
            end_timestamp = event.end
            whole_day = False

        termin = Appointment(
            id=event.id,
            event_name=event.summary,
            start_timestamp=start_timestamp,
            start_day_string=start_day_string,
            start_time=str(start_timestamp.strftime("%H:%M")),
            end_timestamp=end_timestamp,
            end_day_string=end_day_string,
            end_time=str(end_timestamp.strftime("%H:%M")),
            whole_day=whole_day,
            recurring=None,
        )
        events.append(termin)

    return sorted(events, key=lambda x: x.start_timestamp)


if __name__ == "__main__":
    events = [
        event for event in get_list_of_appointments(config.google.calendars["Arkadius"])
    ]
    print(len(events))
