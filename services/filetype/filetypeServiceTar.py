from services.filetype.filetypeBase import FiletypeBase

class FiletypeServiceTar(FiletypeBase):
    def pack(self, files: list[str], chunkSize:int):
        if chunkSize < 512:
            raise ValueError("chunkSize must be at least 512")
        print(f"Files to be added to the tarfile: {files}")

    def unpack(self, data):
        return data
