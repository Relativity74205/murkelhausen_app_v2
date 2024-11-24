from pydantic import BaseModel


class Mheg(BaseModel):
    alert_days: int


class GymBroich(BaseModel):
    class_of_mattis: str


class Config(BaseModel):
    mheg: Mheg
    gym_broich: GymBroich


config = Config(
    mheg=Mheg(alert_days=5),
    gym_broich=GymBroich(class_of_mattis="6A"),
)
