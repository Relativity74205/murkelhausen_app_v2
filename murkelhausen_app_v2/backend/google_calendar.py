import os
from datetime import date, datetime

import reflex as rx

from gcsa.google_calendar import GoogleCalendar
from google.oauth2 import service_account


class Termin(rx.Base):
    event_name: str
    start_timestamp: datetime
    start_day: date
    start_time: str
    end_timestamp: datetime
    end_day: date
    end_time: str


SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_KEY_FILE = "/home/arkadius/.credentials/murkelhausen-3824b92878ca.json"


def get_google_calendar_client() -> GoogleCalendar:
    # TODO: move to config
    private_key = os.environ.get("GOOGLE_PRIVATE_KEY").replace("\\n", "\n")
    info = {
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "client_email": "murkelhausen2@murkelhausen.iam.gserviceaccount.com",
        "client_id": "100602016701161296682",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/murkelhausen2%40murkelhausen.iam.gserviceaccount.com",
        "private_key": private_key,
        "private_key_id": "3824b92878cacd7dbdca0ad9000a0d76962f697f",
        "project_id": "murkelhausen",
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


def get_list_of_appointments() -> list[Termin]:
    gc = get_google_calendar_client()
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
                end_time=str(event.end.time()),
            )
        )

    return events


if __name__ == "__main__":
    print(get_list_of_appointments())
