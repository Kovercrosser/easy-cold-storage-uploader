
from typing import Any, Callable, Dict, List, Optional, Union
import uuid

from services.service_base import ServiceBase


class CancelService(ServiceBase):
    subscriptions: List[Dict[str, Union[Callable[..., None], uuid.UUID, Optional[Any], tuple[Any, ...]]]] = []

    def subscribe_to_cancel_event(self, cancel_callback: Callable[..., None], *args: Any, self_reference: Optional[Any] = None) -> uuid.UUID:
        map_uuid = uuid.uuid4()
        self.subscriptions.append({ "callback": cancel_callback, "uuid": map_uuid, "self_reference": self_reference, "args": args})
        return map_uuid

    def unsubscribe_from_cancel_event(self, map_uuid: uuid.UUID) -> None:
        self.subscriptions = [x for x in self.subscriptions if x["uuid"] != map_uuid]

    def cancel(self, reason: str) -> None:
        for callback in self.subscriptions:
            fun = callback["callback"]
            if not callable(fun):
                continue
            if fun is None:
                continue
            self_reference = callback["self_reference"]
            if self_reference and callable(self_reference):
                if callback["args"] and isinstance(callback["args"], tuple):
                    fun(self_reference, reason, *callback["args"])
                fun(self_reference, reason)
            if callback["args"] and isinstance(callback["args"], tuple):
                fun(reason, *callback["args"])
            fun(reason)
        self.subscriptions = []
