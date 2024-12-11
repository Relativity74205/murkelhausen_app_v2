import os

from pydantic import BaseModel


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
    token: str
    disable_for_in_seconds: int
    pihole_urls: list[str]


class Config(BaseModel):
    mheg: Mheg
    gym_broich: GymBroich
    handball_nordrhein: HandballNordrhein
    fussball_de: FussballDE
    ruhrbahn: Ruhrbahn
    pihole: PiHole


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
)
