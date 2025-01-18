from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from murkelhausen_app_v2.config import config
from murkelhausen_app_v2.tasks.buergeramt import (
    get_next_free_appointment_from_buergeramt,
)
from murkelhausen_app_v2.tasks.test import test_task

scheduler = BackgroundScheduler()

if config.tasks.buergeramt_task.active:
    trigger = IntervalTrigger(minutes=config.tasks.buergeramt_task.schedule_minutes)
    scheduler.add_job(get_next_free_appointment_from_buergeramt, trigger)

trigger = IntervalTrigger(minutes=1)
scheduler.add_job(test_task, trigger)

__all__ = ["scheduler"]
