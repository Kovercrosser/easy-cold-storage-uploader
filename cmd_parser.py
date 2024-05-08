
import argparse
import sys


def upload_argument_parser(parser_upload: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser_upload.add_argument('--profile', default='default', help='Profile to use')
    # Compression
    parser_upload.add_argument(
        '-c',
        '--compression-method',
        choices=["none", "lzma"],
        default="none",
        help='The compression-method to use.',
    )
    parser_upload.add_argument(
        '-l',
        '--compression-level',
        type=int,
        choices=range(1, 10),
        default=7,
        help='The compression level to use. 1 is lowest, 9 is highest',
    )
    # Encryption
    parser_upload.add_argument(
        '-e',
        '--encryption-method',
        choices=["none", "aes"],
        default="none",
        help='The encryption-method to use.',
    )
    parser_upload.add_argument(
        '--password',
        help='The password to use for encryption. This should not be used as it can leak your password',
        required=('--encryption-method' in sys.argv or '-e' in sys.argv)
    )
    parser_upload.add_argument(
        '--password-file',
        help='The path to the password-file for encryption',
        required=('--encryption-method' in sys.argv or '-e' in sys.argv) and '--password' not in sys.argv
    )
    # Filetype
    parser_upload.add_argument(
        '-f',
        '--filetype',
        choices=["zip"],
        default="zip",
        help='The filetype to use.',
    )
    # Transfer
    parser_upload.add_argument(
        '-t',
        '--transfer-method',
        choices=["save", "glacier"],
        help='The transfer-method to use.',
        required='--profile' not in sys.argv
    )
    parser_upload.add_argument(
        '-s',
        '--transfer-chunk-size',
        default=64,
        type=int,
        help='The chunk-size to use for the transfer-method',
    )
    # Dryrun
    parser_upload.add_argument(
        '--dryrun',
        action='store_true',
        help='If set, the files will not be uploaded'
    )
    # Upload-Paths
    parser_upload.add_argument(
        '-p',
        '--paths',
        nargs='+',
        help='Paths of the Files and Folders to upload',
        required=True
    )
    return parser_upload

def download_argument_parser(parser_download: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser_download.add_argument(
        '--id',
        help='Id of Element to download or Glacier Archive-Id',
        required=True
    )
    parser_download.add_argument(
        '--location', 
        default='.',
        help='Location to download to'
    )
    parser_download.add_argument(
        '--password', 
        help='The password to use for decryption. Only needed if the file is encrypted. Use with caution as it can leak your password',
    )
    parser_download.add_argument(
        '--password-file', 
        help='The path to the password-file for decryption. Only needed if the file is encrypted',
    )
    return parser_download
