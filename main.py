import sys
from traceback import print_exception

from dependency_injection.main_factory import setup_factory_from_parameters
from dependency_injection.service import Service
from executer.download_executer import download
from executer.setup_executer import guided_execution, setup
from executer.upload_executer import upload
from services.cancel_service import CancelService
from services.db_service import DbService
from services.setting_service import SettingService
from utils.console_utils import (console, handle_console_exit, print_error)
from utils.cmd_parser import argument_parser

service = Service()
service.set_service(DbService("settings.json"), "settings_db_service")
service.set_service(SettingService(service), "setting_service")

def main() -> None:
    args = argument_parser()
    console.set_alt_screen()

    if args.command == 'upload':
        setup_factory_from_parameters(
            service,
            args.compression_method,
            args.encryption_method,
            args.filetype,
            args.transfer_method,
            args.transfer_chunk_size,
            args.dryrun,
            args.compression_level,
            args.password,
            args.password_file
        )
        upload(service, args.profile, args.paths)
    elif args.command == 'download':
        setup_factory_from_parameters(
            service,
            "none",
            "none",
            "none",
            "none",
            dryrun=False,
            password=args.password,
            password_file=args.password_file
        )
        download(service,  args.profile, args.location, args.id, args.password, args.password_file)
    elif args.command == 'setup':
        setup(service)
    elif args.command == 'guided' or args.command is None:
        guided_execution(service)
    else:
        print_error("Invalid command. Please try again.")
    handle_console_exit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        CANCEL_SERVICE: CancelService | None = None
        try:
            CANCEL_SERVICE = service.get_service("cancel_service")
        except ValueError:
            pass
        with console.status("[bold red]Program terminated by user. Exiting...[/bold red]"):
            if CANCEL_SERVICE:
                CANCEL_SERVICE.cancel("user termination")
        handle_console_exit()
        print("Program terminated by user")
    except Exception as exception:
        handle_console_exit()
        print_exception(exception)
        sys.exit(1)
