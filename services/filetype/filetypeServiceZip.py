from services.filetype.filetypeBase import FiletypeBase

class FiletypeServiceZip(FiletypeBase):
    def pack(self, data):
        return data

    def unpack(self, data):
        return data
