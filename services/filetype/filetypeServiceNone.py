from services.filetype.filetypeBase import FiletypeBase

class FiletypeServiceNone(FiletypeBase):
    def pack(self, files: list[str]):
        raise NotImplementedError("The Upload of individual Files isnt currently supported.")

    def unpack(self, data):
        raise NotImplementedError("Unsupported")

    def getExtension(self) -> str:
        return ""
