from datetime import date

from gcsa.google_calendar import GoogleCalendar

gc = GoogleCalendar('arkadius.schuchhardt@gmail.com')
events = gc.get_events(time_min=date(2024, 11, 18))
for event in events:
    print(f"{event.start} - {event.end}: {event.summary}")


# start = datetime(2024, 12, 1)
# end = start + timedelta(hours=2)
# event = Event('Mattis Spiel',
#               start=start,
#               end=end)
#
# gc.add_event(event)