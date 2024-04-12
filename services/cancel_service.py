from typing import Callable, List, Tuple
import uuid


class CancelService:
    subscriptions: List[Tuple[Callable[[str], None], uuid.UUID ]] = []

    def subscribe_to_cancel_event(self, cancel_callback: Callable[[str], None]):
        map_uuid = uuid.uuid4()
        self.subscriptions.append((cancel_callback, map_uuid))
        return map_uuid

    def unsubscribe_from_cancel_event(self, map_uuid: uuid.UUID):
        self.subscriptions = [x for x in self.subscriptions if x[1] != map_uuid]

    def cancel(self, reason: str):
        for callback, _ in self.subscriptions:
            callback(reason)
        self.subscriptions = []
