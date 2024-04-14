from typing import Any, Callable, Dict, List
import uuid


class CancelService:
    subscriptions: List[Dict] = []

    def subscribe_to_cancel_event(self, cancel_callback: Callable[..., None], *args, self_reference:Any = None):
        map_uuid = uuid.uuid4()
        self.subscriptions.append({ "callback": cancel_callback, "uuid": map_uuid, "self_reference": self_reference, "args": args})
        return map_uuid

    def unsubscribe_from_cancel_event(self, map_uuid: uuid.UUID):
        self.subscriptions = [x for x in self.subscriptions if x["uuid"] != map_uuid]

    def cancel(self, reason: str):
        for callback in self.subscriptions:
            fun: Callable[..., None] = callback["callback"]
            if fun is None:
                continue
            self_reference = callback["self_reference"]
            if self_reference:
                if callback["args"]:
                    fun(self_reference, reason, *callback["args"])
                fun(self_reference, reason)
            if callback["args"]:
                fun(reason, *callback["args"])
            fun(reason)
        self.subscriptions = []
