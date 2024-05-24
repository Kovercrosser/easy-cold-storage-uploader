
import inspect
import uuid
from typing import Any, Callable, Dict, List, Tuple

from services.service_base import ServiceBase
from utils.console_utils import print_error


def check_parameter(func, param_name):
    try:
        signature = inspect.signature(func)
        return param_name in signature.parameters
    except ValueError:
        return False

class CancelService(ServiceBase):
    CallbackType = Callable[..., Any]
    subscriptions: List[Tuple[uuid.UUID, CallbackType, Dict]] = []

    def subscribe_to_cancel_event(self, cancel_callback: CallbackType, **kwargs: Any) -> uuid.UUID:
        map_uuid = uuid.uuid4()
        self.subscriptions.append((map_uuid, cancel_callback, kwargs))
        return map_uuid

    def unsubscribe_from_cancel_event(self, map_uuid: uuid.UUID) -> None:
        self.subscriptions = [x for x in self.subscriptions if x[0] != map_uuid]

    def cancel(self, reason: str) -> None:
        for subscription in self.subscriptions:
            try:
                if check_parameter(subscription[1], "reason") and "reason" not in subscription[2]:
                    subscription[1](reason=reason, **subscription[2])
                else:
                    subscription[1](**subscription[2])
            except Exception as e:
                print_error(f"Error in cancel callback: {e}\n\nwhen calling: {subscription}")
        self.subscriptions = []
