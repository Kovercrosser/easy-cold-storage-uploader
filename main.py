
import argparse
import sys
import traceback
from dependencyInjection.main_factory import setup_factory_from_parameters
from dependencyInjection.service import Service
from profile_setup import setup
from upload_executer import upload
from utils.storage_utils import read_settings
from utils.console_utils import clear_console

def guided_execution():
    if read_settings("global", "setup") is None:
        setup()

    while True:
        clear_console()
        print("\n----------------------------------------")
        print("-------------Glacier Backup-------------")
        print("----------------------------------------\n\n")
        print("---------------commands:----------------")
        print("1: upload")
        print("2: download")
        print("3: delete")
        print("\n---------------inventory:---------------")
        print("4: list all files (from local Database)")
        print("\n---------------setup:-------------------")
        print("9: setup")
        print("\n----------------------------------------\n")
        print("Press Ctrl+C to exit.\n")

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
            print("Invalid choice. Please try again.")


service = Service()
def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    parser_upload = subparsers.add_parser('upload', help='Upload help')
    parser_upload.add_argument('--profile', default='default', help='Profile to use')
    parser_upload.add_argument('--paths', '-p', nargs='+', help='Paths of the Files and Folders to upload')

    subparsers.add_parser('setup', help='Initial Setup')
    subparsers.add_parser('guided', help='Uses Guided Execution')

    args = parser.parse_args()

    # setupFactoryFromStorage(service)
    setup_factory_from_parameters(service, "None", "None", "zip", False)

    # Handle commands
    if args.command == 'upload':
        print(f"Trying to upload {len(args.paths)} path(s) using profile: {args.profile}")
        upload(service, args.profile, args.paths)

    elif args.command == 'setup':
        setup()
    elif args.command == 'guided' or args.command is None:
        guided_execution()
    else:
        print("Invalid command. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram terminated by user. Exiting...", flush=True)
        sys.exit(0)
    except Exception as exception:
        print("Stacktrace:")
        traceback.print_exc()
        print("\n")
        print(f"Unexpected error: {exception}")
        sys.exit(1)
