

class ValidationError(Exception):
    def __init__(self, dados: dict):
        super().__init__()
        self.msg = f"Os dados não podem ser nulos: {dados}"

    def __repr__(self):
        return self.msg