import reflex as rx

from murkelhausen_app_v2 import styles
from murkelhausen_app_v2.pages import *

app = rx.App(
    style=styles.base_style,
    stylesheets=styles.base_stylesheets,
    title="Murkelhausen App",
)
