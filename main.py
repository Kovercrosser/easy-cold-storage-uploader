
import argparse
import sys
from traceback import print_exception

from dependency_injection.main_factory import setup_factory_from_parameters
from dependency_injection.service import Service
from executer.download_executer import download
from executer.setup_executer import guided_execution, setup
from executer.upload_executer import upload
from services.cancel_service import CancelService
from utils.console_utils import (console, handle_console_exit, print_error)

def upload_argument_parser(parser_upload: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser_upload.add_argument('--profile', default='default', help='Profile to use')
    # Compression
    parser_upload.add_argument('--compression-method', '-c', choices=["none", "lzma"], default="none", help='The compression-method to use.', required='--profile' not in sys.argv)
    parser_upload.add_argument('--compression-level', '-l',type=int, choices=range(1, 10), default=7, help='The compression level to use. 1 is lowest, 9 is highest', required='--compression-method' in sys.argv and sys.argv[sys.argv.index('--compression-method') + 1] != 'none')
    # Encryption
    parser_upload.add_argument('--encryption-method', '-e',choices=["none", "aes"], default="none", help='The encryption-method to use.', required='--profile' not in sys.argv)
    parser_upload.add_argument('--password', default="", help='The password to use for encryption. This should not be used as it can leak your password', required='--encryption-method' in sys.argv)
    parser_upload.add_argument('--password-file', default="", help='The path to the password-file for encryption', required='--encryption-method' in sys.argv and '--encryption-password' not in sys.argv)
    # Filetype
    parser_upload.add_argument('--filetype','-f', choices=["zip"], default="zip", help='The filetype to use.', required='--profile' not in sys.argv)
    # Transfer
    parser_upload.add_argument('--transfer-method', '-t', choices=["save", "glacier"], help='The transfer-method to use.', required='--profile' not in sys.argv)
    parser_upload.add_argument('--transfer-chunk-size', '-s', default=64, type=int, help='The chunk-size to use for the transfer-method', required='--transfer-method' in sys.argv and sys.argv[sys.argv.index('--transfer-method') + 1] == 'glacier')
    # Dryrun
    parser_upload.add_argument('--dryrun', action='store_true', help='If set, the files will not be uploaded')
    # Upload-Paths
    parser_upload.add_argument('--paths', '-p', nargs='+', help='Paths of the Files and Folders to upload')
    return parser_upload

def download_argument_parser(parser_download: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser_download.add_argument('--id', help='Id of Element to download')
    parser_download.add_argument('--location', default='.', help='Location to download to')
    parser_download.add_argument('--unpack', action='store_true', help='Set if the file should be unpacked')
    parser_download.add_argument('--password', help='The password to use for encryption. This should not be used as it can leak your password', required='--encryption-method' in sys.argv)
    parser_download.add_argument('--password-file', help='The path to the password-file for encryption', required='--encryption-method' in sys.argv and '--encryption-password' not in sys.argv)
    return parser_download

service = Service()
def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    parser_upload = subparsers.add_parser('upload', help='Upload help')
    parser_upload = upload_argument_parser(parser_upload)

    parser_download = subparsers.add_parser('download', help='Download help')
    parser_download = download_argument_parser(parser_download)

    subparsers.add_parser('setup', help='Initial Setup')
    subparsers.add_parser('guided', help='Uses Guided Execution')

    args = parser.parse_args()
    console.set_alt_screen()

    if args.command == 'upload':
        setup_factory_from_parameters(service, args.compression_method, args.encryption_method, args.filetype, args.transfer_method, args.transfer_chunk_size, args.dryrun, args.compression_level, args.password, args.password_file)
        upload(service, args.profile, args.paths)
    elif args.command == 'download':
        setup_factory_from_parameters(service, "none", "none", "none", "none", dryrun=False, password=args.password, password_file=args.password_file)
        download(service,  args.profile, args.location, args.id, args.unpack)
    elif args.command == 'setup':
        setup()
    elif args.command == 'guided' or args.command is None:
        guided_execution()
    else:
        print_error("Invalid command. Please try again.")
    handle_console_exit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        try:
            cancel_service: CancelService = service.get_service("cancel_service")
        except ValueError:
            pass
        with console.status("[bold red]Program terminated by user. Exiting...[/bold red]"):
            if cancel_service:
                cancel_service.cancel("user termination")
        handle_console_exit()
        print("Program terminated by user")
    except Exception as exception:
        handle_console_exit()
        print_exception(exception)
        sys.exit(1)
