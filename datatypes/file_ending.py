from enum import Enum
class FileEndingCompression(Enum):
    BZIP2 = '.bz2'
    LZMA = '.xz'
    NONE = ''

class FileEndingEncryption(Enum):
    AES = '.aes'
    RSA = '.rsa'
    NONE = ''

class FileEndingFiletype(Enum):
    TAR = '.tar'
    ZIP = '.zip'
    NONE = ''