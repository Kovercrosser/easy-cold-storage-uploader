

class Service:
    def __init__(self) -> None:
        self.compressionService = None
        self.encryptionService = None
        self.filetypeService = None
        self.transferService = None

    def setService(self, serviceRef: any, serviceName: str):
        if serviceRef is None:
            raise ValueError("Service reference cannot be None.")
        setattr(self, serviceName, serviceRef)

    def getService(self, serviceName: str):
        val = getattr(self, serviceName)
        if val is None:
            raise ValueError(f"Service {serviceName} not set.")
        return val
