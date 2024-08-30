import uuid

class Uuid:
    @staticmethod
    def generate() -> str:
        return str(uuid.uuid4())
