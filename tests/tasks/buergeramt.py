import pytest
from freezegun import freeze_time

from murkelhausen_app_v2.tasks.buergeramt import check_if_date_is_within_x_days


@pytest.mark.parametrize(
    "date_str, x, result",
    [
        ("19.01.2025", 7, True),
        ("26.01.2025", 7, False),
    ],
)
@freeze_time("2025-01-18")
def test_check_if_date_is_within_x_days(date_str, x, result):
    assert check_if_date_is_within_x_days(date_str, x) == result
