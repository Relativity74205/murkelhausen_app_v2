from datetime import datetime, date

import reflex as rx
import sqlmodel

from murkelhausen_app_v2.templates.template import template


class User(rx.Model, table=True):
    username: str
    email: str


class Floors(rx.Model, table=True):
    metadata = sqlmodel.MetaData(schema="data")
    tstamp_start: datetime = sqlmodel.Field(primary_key=True)
    tstamp_end: datetime
    floorsAscended: int
    floorsDescended: int


class StressDaily(rx.Model, table=True):
    __tablename__ = "stress_daily"
    metadata = sqlmodel.MetaData(schema="data")
    calendar_date: date = sqlmodel.Field(primary_key=True)
    max_stress_level: int
    avg_stress_level: int


class QueryUser(rx.State):
    users: list[User]
    floors: list[Floors]
    stress_daily: list[StressDaily]

    @rx.event
    def get_data(self):
        with rx.session() as session:
            self.users = session.exec(User.select()).all()
            self.floors = session.exec(Floors.select()).all()
            self.stress_daily = session.exec(
                StressDaily.select().order_by(StressDaily.calendar_date.asc())
            ).all()


def show_row(user: User):
    return rx.table.row(
        rx.table.cell(user.username),
        rx.table.cell(user.email),
    )


def show_row_stress_daily(stress_daily: StressDaily):
    return rx.table.row(
        rx.table.cell(stress_daily.calendar_date),
        rx.table.cell(stress_daily.max_stress_level),
        rx.table.cell(stress_daily.avg_stress_level),
    )


@template(
    route="/table_test", title="TableTest", icon="table", on_load=QueryUser.get_data
)
def table_page() -> rx.Component:
    return rx.vstack(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Username"),
                    rx.table.column_header_cell("Email"),
                ),
            ),
            rx.table.body(
                rx.foreach(QueryUser.users, show_row),
            ),
            variant="surface",
            size="3",
        ),
        rx.data_table(
            data=QueryUser.stress_daily,
            columns=["calendar_date", "max_stress_level", "avg_stress_level"],
            pagination=True,
            sort=True,
        ),
        rx.recharts.line_chart(
            rx.recharts.line(
                data_key="avg_stress_level",
                type_="monotone",
            ),
            rx.recharts.x_axis(data_key="calendar_date"),
            rx.recharts.y_axis(),
            rx.recharts.graphing_tooltip(),
            data=QueryUser.stress_daily,
            width="100%",
            height=300,
        ),
        width="100%",
    )
