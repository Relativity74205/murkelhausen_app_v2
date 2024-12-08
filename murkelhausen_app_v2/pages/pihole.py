from datetime import datetime

import reflex as rx

from murkelhausen_app_v2.backend.pihole import pihole_deactivate


class PiHoleState(rx.State):
    messages = []
    error = False
    deactivated: datetime | None = None
    deactivated_for_text: str | None = "foo"

    async def run_pihole_deactivate(self):
        self.messages, self.error = pihole_deactivate()
        if self.error:
            yield rx.toast("Failed to deactivate Pi Hole(s). Messages: " + "\n".join(self.messages))
        else:
            self.deactivated = datetime.now()
            yield rx.toast("Pi Hole(s) has been deactivated.")
        # await asyncio.sleep(1)
        # yield
        #
        # while True:
        #     self.deactivated_for_text = str(random.randint(0, 100))
        #     yield
        #     await asyncio.sleep(1)

    #     self.foo()
    #
    # @rx.event
    # async def foo(self):
    #     while True:
    #         yield PiHoleState.update_deactivated_for_text
    #
    # @rx.event
    # async def update_deactivated_for_text(self) -> str | None:
    #     if self.deactivated is None:
    #         yield None
    #     remaining_time = self._remaining_time()
    #     # self.deactivated_for_text = f"Deactivated for {remaining_time}"
    #     self.deactivated_for_text = str(random.randint(0, 100))
    #     yield
    #     await asyncio.sleep(1)

    # def _remaining_time(self) -> int:
    #     return config.pihole.disable_for_in_seconds - (datetime.now() - self.deactivated).seconds
