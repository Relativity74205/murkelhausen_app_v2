import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from murkelhausen_app_v2.config import config
from murkelhausen_app_v2.tasks.buergeramt import (
    get_next_free_appointment_from_buergeramt_cars,
)

log = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

if config.tasks.buergeramt_task.active:
    log.info("Adding buergeramt task")
    trigger = IntervalTrigger(minutes=config.tasks.buergeramt_task.schedule_minutes)
    scheduler.add_job(get_next_free_appointment_from_buergeramt_cars, trigger)
    log.info("Buergeramt task added")
else:
    log.info("Buergeramt task is deactivated")

__all__ = ["scheduler"]
