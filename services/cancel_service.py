
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
        for subscription in self.subscriptions:
            fun = subscription["callback"]
            if not callable(fun):
                continue
            if fun is None:
                continue
            self_reference = subscription["self_reference"]
            args = subscription["args"]
            if self_reference is not None:
                if args and isinstance(args, tuple):
                    fun(self_reference, reason, *args)
                fun(self_reference, reason)
            if args and isinstance(args, tuple):
                fun(reason, *args)
            fun(reason)
        self.subscriptions = []
