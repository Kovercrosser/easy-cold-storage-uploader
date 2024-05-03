import datetime
import multiprocessing as mp
import time
import uuid
from threading import Event
from typing import Literal

from rich.table import Table

from dependency_injection.service import Service
from services.cancel_service import CancelService
from utils.console_utils import console


class Reporting():
    def __init__(self, worker_type: Literal["transferer" , "crypter" , "packer" , "compressor"],
                worker_id: uuid.UUID,
                status: Literal["waiting", "working", "finished", "failed", "cancelled"],
                status_message: str | None = None,
                log_message: str | None = None
                ) -> None:
        self.worker_type = worker_type
        self.worker_id = worker_id
        self.status = status
        self.status_message = status_message
        self.log_message = log_message

class ReportManager():
    reports: "mp.Queue[Reporting | Literal['stop']]" = mp.Queue()
    stop_event: Event
    printer_process: mp.Process
    cancel_service: CancelService
    cancel_uuid: uuid.UUID

    def __init__(self, service: Service) -> None:
        self.printer_process = mp.Process(target=self.__report_printer, args=(self.reports,))
        self.printer_process.start()
        self.cancel_service: CancelService = service.get_service("cancel_service")
        self.cancel_uuid = self.cancel_service.subscribe_to_cancel_event(self.stop_reporting, self_reference=self)

    def __del__(self) -> None:
        self.stop_reporting()

    def add_report(self, report: Reporting) -> None:
        self.reports.put(report)

    def stop_reporting(self) -> None:
        self.reports.put("stop")
        self.cancel_service.unsubscribe_from_cancel_event(self.cancel_uuid)
        self.printer_process.join()

    def __get_queue_element_if_exists(self, queue: "mp.Queue[Reporting | Literal['stop']]") -> Reporting | Literal['stop'] | None:
        if queue.qsize() == 0:
            return None
        return queue.get()

    def __report_printer(self, queue: "mp.Queue[Reporting | Literal['stop']]") -> None:
        con_message: dict[str, dict[Literal["name", "type", "status", "log_message", "status_message"], str | None]] = {}
        with console.status("") as status:
            while True:
                report = self.__get_queue_element_if_exists(queue)
                if report == "stop":
                    break
                if report is None:
                    time.sleep(0.1)
                    continue
                reporter_status: dict[Literal["name","type", "status", "log_message", "status_message"], str | None] = {}
                worker_name: str
                if str(report.worker_id) not in con_message:
                    worker_name = str(len(con_message) + 1)
                else:
                    n = con_message[str(report.worker_id)]["name"]
                    assert n is not None
                    worker_name = n
                reporter_status = {"name": worker_name, "type": report.worker_type, "status": report.status, "status_message": report.status_message, "log_message": report.log_message}
                con_message[str(report.worker_id)] = reporter_status
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Worker", justify="center")
                table.add_column("Job", justify="center")
                table.add_column("Status", justify="center")
                table.add_column("Message", justify="center")
                for key, value in con_message.items():
                    table.add_row(value["name"], value["type"], value["status"], value["status_message"], style="bold green")
                    if value["log_message"]:
                        console.print(f"[purple][{datetime.datetime.now().strftime('%H:%M:%S ')}][/purple] {key} {value['log_message']}")
                        value["log_message"] = None # Set log message to None after printing so that it doesn't print again
                status.update(table)
