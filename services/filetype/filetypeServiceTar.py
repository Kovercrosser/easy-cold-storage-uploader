from services.filetype.filetypeBase import FiletypeBase

class FiletypeServiceTar(FiletypeBase):
    def pack(self, data):
        return data

    def unpack(self, data):
        return data
