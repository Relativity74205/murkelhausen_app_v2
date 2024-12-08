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


class Config(BaseModel):
    mheg: Mheg
    gym_broich: GymBroich
    handball_nordrhein: HandballNordrhein
    fussball_de: FussballDE
    ruhrbahn: Ruhrbahn


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
)
