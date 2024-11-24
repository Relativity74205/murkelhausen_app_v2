from pydantic import BaseModel


class Mheg(BaseModel):
    alert_days: int
    request_timeout: int


class GymBroich(BaseModel):
    class_of_mattis: str
    request_timeout: int


class HandballNordrhein(BaseModel):
    request_timeout: int


class FussballDE(BaseModel):
    request_timeout: int


class Config(BaseModel):
    mheg: Mheg
    gym_broich: GymBroich
    handball_nordrhein: HandballNordrhein
    fussball_de: FussballDE


config = Config(
    mheg=Mheg(
        alert_days=5,
        request_timeout=2,
    ),
    gym_broich=GymBroich(
        class_of_mattis="6A",
        request_timeout=2,
    ),
    handball_nordrhein=HandballNordrhein(
        request_timeout=2,
    ),
    fussball_de=FussballDE(
        request_timeout=2,
    ),
)
