import requests

from murkelhausen_app_v2.config import config


def _deactivate_pihole(base_url: str, pi_hole_number: int) -> tuple[str, bool]:
    """
    Deactivate Pi Hole for 5 minutes.

    Returns a string and an indicator if the deactivation attempt was an error.
    """
    params = {
        "auth": config.pihole.token.get_secret_value(),
        "disable": config.pihole.disable_for_in_seconds,
    }
    try:
        r = requests.get(base_url, params=params)
    except requests.exceptions.ConnectionError:
        return f"Failed to deactivate Pi Hole {pi_hole_number} due to a connection error. Contact Arkadius. ;)", True
    else:
        if "disabled" in r.text:
            return f"Pi Hole {pi_hole_number} has been deactivated for 5 minutes.", False
        else:
            return f"Failed to deactivate Pi Hole {pi_hole_number}. Contact Arkadius. ;)\n{r.text=}; {r.status_code=}", True


def pihole_deactivate() -> tuple[list[str], bool]:
    error = False
    messages = []
    for i, base_url in enumerate(config.pihole.pihole_urls, start=1):
        message, local_error = _deactivate_pihole(base_url, i)
        messages.append(message)
        error = error or local_error

    return messages, error


if __name__ == "__main__":
    print(pihole_deactivate())