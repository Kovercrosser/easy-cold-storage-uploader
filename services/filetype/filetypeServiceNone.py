from services.filetype.filetypeBase import FiletypeBase

class FiletypeServiceNone(FiletypeBase):
    def pack(self, files: list[str], chunkSize:int):
        return

    def unpack(self, data):
        return data
