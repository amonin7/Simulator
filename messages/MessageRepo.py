from collections import defaultdict
import heapq as hq


class MessageRepo:

    def __init__(self):
        self.message_queue = defaultdict(list)

    def put_message(self, receiver: int, message) -> None:
        hq.heappush(self.message_queue[receiver], message)

    def get_messages(self, receiver: int):
        messages = self.message_queue[receiver]
        self.message_queue[receiver] = []
        return messages

    def get_one_message(self, receiver: int):
        if len(self.message_queue[receiver]) == 0:
            return None
        else:
            message = hq.heappop(self.message_queue[receiver])
            return message

    def get_mes_amount(self, receiver: int) -> int:
        return len(self.message_queue[receiver])
