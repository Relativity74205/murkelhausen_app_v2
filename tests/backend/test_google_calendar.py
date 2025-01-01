from datetime import date, datetime

import pytest
import pytz

from murkelhausen_app_v2.backend.google_calendar import (
    AppointmentRecurrenceType,
    AppointmentRecurrence,
)


@pytest.mark.parametrize(
    "recurrence_string, expected",
    [
        (
            "RRULE:FREQ=WEEKLY;BYDAY=TH",
            AppointmentRecurrence(AppointmentRecurrenceType.WEEKLY, 1, None, None),
        ),
        (
            "RRULE:FREQ=WEEKLY;WKST=MO;INTERVAL=2;BYDAY=WE",
            AppointmentRecurrence(AppointmentRecurrenceType.WEEKLY, 2, None, None),
        ),
        (
            "RRULE:FREQ=MONTHLY;UNTIL=20250404T215959Z;INTERVAL=3",
            AppointmentRecurrence(
                AppointmentRecurrenceType.MONTHLY, 3, date(2025, 4, 4), None
            ),
        ),
        (
            "RRULE:FREQ=DAILY;COUNT=13;INTERVAL=2",
            AppointmentRecurrence(AppointmentRecurrenceType.DAILY, 2, None, 13),
        ),
    ],
)
def test_parse_recurrence_string(recurrence_string, expected):
    assert AppointmentRecurrence.from_string(recurrence_string) == expected


@pytest.mark.parametrize(
    "recurrence, event_timestamp, time_min, time_max, expected",
    [
        (
            AppointmentRecurrence(AppointmentRecurrenceType.DAILY, 1, None, None),
            datetime(2023, 10, 1, 12, tzinfo=pytz.UTC),
            date(2023, 10, 1),
            date(2023, 10, 5),
            [
                datetime(2023, 10, 1, 12, tzinfo=pytz.UTC),
                datetime(2023, 10, 2, 12, tzinfo=pytz.UTC),
                datetime(2023, 10, 3, 12, tzinfo=pytz.UTC),
                datetime(2023, 10, 4, 12, tzinfo=pytz.UTC),
            ],
        ),
        (
            AppointmentRecurrence(AppointmentRecurrenceType.DAILY, 2, None, None),
            datetime(2023, 10, 1, 12, tzinfo=pytz.UTC),
            date(2023, 10, 1),
            date(2023, 10, 5),
            [
                datetime(2023, 10, 1, 12, tzinfo=pytz.UTC),
                datetime(2023, 10, 3, 12, tzinfo=pytz.UTC),
            ],
        ),
        (  # Test with event_timestamp in the past
            AppointmentRecurrence(AppointmentRecurrenceType.DAILY, 1, None, None),
            datetime(2023, 9, 1, 12, tzinfo=pytz.UTC),
            date(2023, 10, 1),
            date(2023, 10, 5),
            [
                datetime(2023, 10, 1, 12, tzinfo=pytz.UTC),
                datetime(2023, 10, 2, 12, tzinfo=pytz.UTC),
                datetime(2023, 10, 3, 12, tzinfo=pytz.UTC),
                datetime(2023, 10, 4, 12, tzinfo=pytz.UTC),
            ],
        ),
        (
            AppointmentRecurrence(AppointmentRecurrenceType.WEEKLY, 1, None, None),
            datetime(2023, 10, 1, tzinfo=pytz.UTC),
            date(2023, 10, 1),
            date(2023, 10, 29),
            [
                datetime(2023, 10, 1, tzinfo=pytz.UTC),
                datetime(2023, 10, 8, tzinfo=pytz.UTC),
                datetime(2023, 10, 15, tzinfo=pytz.UTC),
                datetime(2023, 10, 22, tzinfo=pytz.UTC),
                # datetime(2023, 10, 29, tzinfo=pytz.UTC), is not included in the list, because the event_timestamp is in UTC (from google API)
            ],
        ),
        (
            AppointmentRecurrence(AppointmentRecurrenceType.MONTHLY, 1, None, None),
            datetime(2023, 1, 1, tzinfo=pytz.UTC),
            date(2023, 1, 1),
            date(2023, 5, 1),
            [
                datetime(2023, 1, 1, tzinfo=pytz.UTC),
                datetime(2023, 2, 1, tzinfo=pytz.UTC),
                datetime(2023, 3, 1, tzinfo=pytz.UTC),
                datetime(2023, 4, 1, tzinfo=pytz.UTC),
            ],
        ),
        (  # Test with end_date
            AppointmentRecurrence(
                AppointmentRecurrenceType.MONTHLY, 1, date(2023, 2, 1), None
            ),
            datetime(2023, 1, 1, tzinfo=pytz.UTC),
            date(2023, 1, 1),
            date(2023, 5, 1),
            [
                datetime(2023, 1, 1, tzinfo=pytz.UTC),
            ],
        ),
        (  # Test with count
            AppointmentRecurrence(AppointmentRecurrenceType.DAILY, 1, None, 3),
            datetime(2023, 10, 1, 12, tzinfo=pytz.UTC),
            date(2023, 10, 1),
            date(2023, 10, 5),
            [
                datetime(2023, 10, 1, 12, tzinfo=pytz.UTC),
                datetime(2023, 10, 2, 12, tzinfo=pytz.UTC),
                datetime(2023, 10, 3, 12, tzinfo=pytz.UTC),
            ],
        ),
    ],
)
def test_get_event_timestamps(
    recurrence, event_timestamp, time_min, time_max, expected
):
    assert (
        recurrence.get_event_timestamps(event_timestamp, time_min, time_max) == expected
    )
