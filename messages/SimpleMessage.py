class SimpleMessage:

    def __init__(self, sender, dest, text, parameters):
        self.sender = sender
        self.dest = dest
        self.text = text
        self.parameters = parameters


class Message2:

    def __init__(self, sender, dest, mes_type, payload, timestamp):
        self.sender = sender
        self.dest = dest
        self.payload = payload
        self.mes_type = mes_type
        self.timestamp = timestamp

    def __str__(self) -> str:
        return str(
            {
                'payload': self.payload,
                'message_type': self.mes_type
            }
        )

    def __repr__(self) -> str:
        return str(
            {
                'payload': self.payload,
                'message_type': self.mes_type
            }
        )

    def __eq__(self, other):
        return self.timestamp == other.timestamp

    def __gt__(self, other):
        return self.timestamp > other.timestamp

    def __ge__(self, other):
        return self.timestamp >= other.timestamp
