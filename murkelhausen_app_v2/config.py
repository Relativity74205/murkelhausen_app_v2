from pydantic import BaseModel


class Mheg(BaseModel):
    alert_days: int


class Config(BaseModel):
    mheg: Mheg


config = Config(
    mheg=Mheg(
        alert_days=5
    )
)
