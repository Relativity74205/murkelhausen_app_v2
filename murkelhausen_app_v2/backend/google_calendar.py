from dataclasses import dataclass
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
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


@dataclass
class AppointmentRecurrence:
    recurrence_type: AppointmentRecurrenceType
    interval: int
    end_date: date | None
    count: int | None

    def get_event_timestamps(
        self, event_timestamp: datetime, date_min: date, date_max: date
    ) -> list[datetime]:
        """
        Get all event timestamps for the given recurrence type, interval and end date.
        """
        timestamp_min = datetime.combine(date_min, datetime.min.time()).astimezone(
            pytz.UTC
        )
        timestamp_max = datetime.combine(date_max, datetime.min.time()).astimezone(
            pytz.UTC
        )

        event_timestamps = []
        current_event_timestamp = event_timestamp
        current_count = 0
        while current_event_timestamp <= timestamp_max:
            if self.end_date is not None:
                end_timestamp = datetime.combine(
                    self.end_date, datetime.min.time()
                ).astimezone(pytz.UTC)
                if current_event_timestamp >= end_timestamp:
                    break

            if self.count is not None:
                if current_count >= self.count:
                    break

            if current_event_timestamp >= timestamp_min:
                current_count += 1
                event_timestamps.append(current_event_timestamp)

            match self.recurrence_type:
                case AppointmentRecurrenceType.DAILY:
                    current_event_timestamp += relativedelta(days=self.interval)
                case AppointmentRecurrenceType.WEEKLY:
                    current_event_timestamp += relativedelta(weeks=self.interval)
                case AppointmentRecurrenceType.MONTHLY:
                    current_event_timestamp += relativedelta(months=self.interval)
                case AppointmentRecurrenceType.YEARLY:
                    current_event_timestamp += relativedelta(years=self.interval)

        return event_timestamps

    @classmethod
    def from_string(cls, recurrence_string: str) -> "AppointmentRecurrence":
        recurrence_parts = recurrence_string.removeprefix("RRULE:").split(";")
        recurrence_dict = {}
        for part in recurrence_parts:
            key, value = part.split("=")
            recurrence_dict[key] = value

        recurrence_type = AppointmentRecurrenceType(recurrence_dict["FREQ"])
        interval = int(recurrence_dict.get("INTERVAL", 1))
        end_date_str: str | None = recurrence_dict.get("UNTIL")
        end_date: date | None = None
        if end_date_str:
            end_date = (
                datetime.strptime(end_date_str, "%Y%m%dT%H%M%SZ")
                .astimezone(pytz.timezone("Europe/Berlin"))
                .date()
            )
        count = recurrence_dict.get("COUNT", None)
        if count is not None:
            count = int(count)

        return cls(
            recurrence_type=recurrence_type,
            interval=interval,
            end_date=end_date,
            count=count,
        )


class Appointment(rx.Base):
    id: str | None
    event_name: str
    start_timestamp: datetime
    start_day_string: str
    start_time: str
    end_timestamp: datetime
    end_day_string: str
    end_time: str
    is_whole_day: bool
    is_recurring: bool


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

    time_min = today
    # TODO: make amount of weeks configurable
    time_max = today + relativedelta(weeks=2)
    raw_events = gc.get_events(
        calendar_id=calendar_id, time_min=time_min, time_max=time_max
    )

    events = []
    for event in raw_events:
        is_recurring = len(event.recurrence) > 0
        if is_recurring:
            appointment_recurrence = AppointmentRecurrence.from_string(
                recurrence_string=event.recurrence[0]
            )
            event_starts = appointment_recurrence.get_event_timestamps(
                event_timestamp=event.start, date_min=time_min, date_max=time_max
            )
            event_ends = appointment_recurrence.get_event_timestamps(
                event_timestamp=event.end, date_min=time_min, date_max=time_max
            )
        else:
            event_starts = [event.start]
            event_ends = [event.end]

        for event_start, event_end in zip(event_starts, event_ends):
            event_end = event_end - relativedelta(days=1)
            # TODO: create day_string for start and end dates
            start_day_string = format_date(
                event_start, format="dd.MM.yyyy (EEE)", locale="de_DE"
            )
            end_day_string = format_date(
                event_end, format="dd.MM.yyyy (EEE)", locale="de_DE"
            )

            if type(event_start) is date:
                start_timestamp = datetime.combine(
                    event_start, datetime.min.time()
                ).astimezone(pytz.timezone("Europe/Berlin"))
                end_timestamp = datetime.combine(
                    event_end, datetime.min.time()
                ).astimezone(pytz.timezone("Europe/Berlin"))
                is_whole_day = True
            else:
                start_timestamp = event_start
                end_timestamp = event_end
                is_whole_day = False

            termin = Appointment(
                id=event.id,
                event_name=event.summary,
                start_timestamp=start_timestamp,
                start_day_string=start_day_string,
                start_time=str(start_timestamp.strftime("%H:%M")),
                end_timestamp=end_timestamp,
                end_day_string=end_day_string,
                end_time=str(end_timestamp.strftime("%H:%M")),
                is_whole_day=is_whole_day,
                is_recurring=is_recurring,
            )
            events.append(termin)

    return sorted(events, key=lambda x: x.start_timestamp)


if __name__ == "__main__":
    events = [
        event for event in get_list_of_appointments(config.google.calendars["Arkadius"])
    ]
    print(len(events))
