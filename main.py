
import argparse
import sys
from rich import print as printx
import rich
import rich.traceback
from dependency_injection.main_factory import setup_factory_from_parameters
from dependency_injection.service import Service
from download_executer import download
from profile_setup import setup
from services.cancel_service import CancelService
from upload_executer import upload
from utils.storage_utils import read_settings
from utils.console_utils import clear_console

def guided_execution() -> None:
    if read_settings("global", "setup") is None:
        setup()

    while True:
        clear_console()
        printx("\n----------------------------------------")
        printx("-------------Glacier Backup-------------")
        printx("----------------------------------------\n\n")
        printx("---------------commands:----------------")
        printx("1: upload")
        printx("2: download")
        printx("3: delete")
        printx("\n---------------inventory:---------------")
        printx("4: list all files (from local Database)")
        printx("\n---------------setup:-------------------")
        printx("9: setup")
        printx("\n----------------------------------------\n")
        printx("Press Ctrl+C to exit.\n")

        choice = input("\nEnter your choice: ")

        # pylint: disable=no-else-raise
        if choice in ("upload", "1"):
            raise NotImplementedError("Upload is not implemented yet.")
        elif choice in ("download", "2"):
            raise NotImplementedError("Download is not implemented yet.")
        elif choice in ("delete", "3"):
            raise NotImplementedError("Delete is not implemented yet.")
        elif choice in ("list all files", "4"):
            raise NotImplementedError("List all Files is not implemented yet.")
        elif choice in ("setup", "9"):
            setup()
        else:
            clear_console()
            printx("Invalid choice. Please try again.")


service = Service()
def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    parser_upload = subparsers.add_parser('upload', help='Upload help')
    parser_upload.add_argument('--profile', default='default', help='Profile to use')
    parser_upload.add_argument('--paths', '-p', nargs='+', help='Paths of the Files and Folders to upload')

    parser_download = subparsers.add_parser('download', help='Download help')
    parser_download.add_argument('--profile', default='default', help='Profile to use')
    parser_download.add_argument('--location', default='.', help='Location to download to')

    subparsers.add_parser('setup', help='Initial Setup')
    subparsers.add_parser('guided', help='Uses Guided Execution')

    args = parser.parse_args()

    # setupFactoryFromStorage(service)
    setup_factory_from_parameters(service, "None", "aes", "zip", True)

    # Handle commands
    if args.command == 'upload':
        upload(service, args.profile, args.paths)
    if args.command == 'download':
        download(service,  args.profile, args.location, "2024-04-25.zip.aes")

    elif args.command == 'setup':
        setup()
    elif args.command == 'guided' or args.command is None:
        guided_execution()
    else:
        printx("Invalid command. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        printx("\n\nProgram terminated by user. Exiting...", flush=True)
        try:
            cancel_service: CancelService = service.get_service("cancel_service")
        except ValueError:
            pass
        new_console = rich.console.Console()
        new_console.clear()
        with new_console.status("[bold red]Program terminated by user. Exiting...[/bold red]"):
            if cancel_service:
                cancel_service.cancel("user termination")
    except Exception as exception:
        printx(f"Unexpected error: {exception}")
        sys.exit(1)
