import os

from pydantic import BaseModel, SecretStr


class Mheg(BaseModel):
    alert_days: int
    request_timeout: int


class GymBroich(BaseModel):
    class_suffix_mattis: str
    year_started_mattis: int
    request_timeout: int


class HandballNordrhein(BaseModel):
    request_timeout: int


class FussballDE(BaseModel):
    request_timeout: int


class Ruhrbahn(BaseModel):
    request_timeout: int


class PiHole(BaseModel):
    request_timeout: int
    token: SecretStr
    disable_for_in_seconds: int
    pihole_urls: list[str]


class OWM(BaseModel):
    request_timeout: int
    api_key: SecretStr


class Google(BaseModel):
    api_key: str
    private_key_id: str
    project_id: str
    client_email: str
    client_id: str
    client_x509_cert_url: str
    calendars: dict[str, str]


class Pushover(BaseModel):
    user_key: SecretStr
    token: SecretStr


class BuergeramtTask(BaseModel):
    active: bool
    schedule_minutes: int
    search_timeframe_days: int


class Tasks(BaseModel):
    buergeramt_task: BuergeramtTask


class Config(BaseModel):
    mheg: Mheg
    gym_broich: GymBroich
    handball_nordrhein: HandballNordrhein
    fussball_de: FussballDE
    ruhrbahn: Ruhrbahn
    pihole: PiHole
    owm: OWM
    google: Google
    pushover: Pushover
    tasks: Tasks


config = Config(
    mheg=Mheg(
        alert_days=5,
        request_timeout=2,
    ),
    gym_broich=GymBroich(
        class_suffix_mattis="B",
        year_started_mattis=2023,
        request_timeout=5,
    ),
    handball_nordrhein=HandballNordrhein(
        request_timeout=2,
    ),
    fussball_de=FussballDE(
        request_timeout=2,
    ),
    ruhrbahn=Ruhrbahn(
        request_timeout=2,
    ),
    pihole=PiHole(
        request_timeout=2,
        token=os.environ.get("PI_HOLE_TOKEN", "placeholder"),
        disable_for_in_seconds=300,
        pihole_urls=[
            "http://192.168.1.18/admin/api.php",  # rasp1.local
            "http://192.168.1.28/admin/api.php",  # rasp2.local
        ],
    ),
    owm=OWM(
        request_timeout=2,
        api_key=os.environ.get("OPENWEATHERMAP_API_KEY", "placeholder"),
    ),
    google=Google(
        api_key=os.environ.get("GOOGLE_PRIVATE_KEY", "placeholder"),
        private_key_id="3824b92878cacd7dbdca0ad9000a0d76962f697f",
        project_id="murkelhausen",
        client_email=os.environ.get("GOOGLE_CLIENT_EMAIL", "placeholder"),
        client_id="100602016701161296682",
        client_x509_cert_url="https://www.googleapis.com/robot/v1/metadata/x509/murkelhausen2%40murkelhausen.iam.gserviceaccount.com",
        calendars={
            "Arkadius": os.environ.get("GOOGLE_CALENDAR_ARKADIUS", "placeholder"),
            # "Familie": os.environ.get("GOOGLE_CALENDAR_FAMILIE", "placeholder"),
            "Erik": os.environ.get("GOOGLE_CALENDAR_ERIK", "placeholder"),
            "Mattis": os.environ.get("GOOGLE_CALENDAR_MATTIS", "placeholder"),
            "Andrea": os.environ.get("GOOGLE_CALENDAR_ANDREA", "placeholder"),
            "Geburtstage": os.environ.get("GOOGLE_CALENDAR_GEBURTSTAGE", "placeholder"),
        },
    ),
    pushover=Pushover(
        user_key=os.environ.get("PUSHOVER_USER_KEY", "placeholder"),
        token=os.environ.get("PUSHOVER_TOKEN", "placeholder"),
    ),
    tasks=Tasks(
        buergeramt_task=BuergeramtTask(
            active=False,
            schedule_minutes=3,
            search_timeframe_days=1,
        ),
    ),
)
