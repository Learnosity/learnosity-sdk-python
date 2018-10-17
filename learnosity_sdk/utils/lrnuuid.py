import uuid

class Uuid:
    @staticmethod
    def generate():
        return str(uuid.uuid4())
