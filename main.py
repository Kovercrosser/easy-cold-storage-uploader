
import argparse
import sys
from setupGlacier import setup
from uploadGlacier import upload
from utils.storageUtils import readSettings
from utils.consoleUtils import clearConsole

def guidedExecution():
    if readSettings("global", "setup") is None:
        setup()

    while True:
        clearConsole()
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

        if choice == "upload" or choice == "1":
            raise NotImplementedError("Upload is not implemented yet.")
        elif choice == "download" or choice == "2":
            raise NotImplementedError("Download is not implemented yet.")
        elif choice == "delete" or choice == "3":
            raise NotImplementedError("Delete is not implemented yet.")
        elif choice == "list all files" or choice == "4":
            raise NotImplementedError("List all Files is not implemented yet.")
        elif choice == "setup" or choice == "9":
            setup()
        else:
            clearConsole()
            print("Invalid choice. Please try again.")



def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    parserUpload = subparsers.add_parser('upload', help='Upload help')
    parserUpload.add_argument('--profile', default='default', help='Profile to use')
    parserUpload.add_argument('--paths', '-p', nargs='+', help='Paths of the Files and Folders to upload')

    subparsers.add_parser('setup', help='Initial Setup')
    subparsers.add_parser('guided', help='Uses Guided Execution')

    args = parser.parse_args()

    # Handle commands
    if args.command == 'upload':
        print(f"Trying to upload {len(args.paths)} file(s) using profile: {args.profile}")
        upload(args.profile, args.paths)
    elif args.command == 'setup':
        setup()
    elif args.command == 'guided' or args.command is None:
        guidedExecution()
    else:
        print("Invalid command. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram terminated by user. Exiting...", flush=True)
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
