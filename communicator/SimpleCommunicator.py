from typing import Tuple

from messages.SimpleMessage import Message2 as Message


class SimpleCommunicator:

    def __init__(self, proc_id, proc_am, ms, prc_snd0=0, prc_snd1=0.0000003, prc_rcv0=0, prc_rcv1=0):
        self.proc_id = proc_id
        self.proc_am = proc_am
        self.prc_snd0 = prc_snd0
        self.prc_snd1 = prc_snd1
        self.prc_rcv0 = prc_rcv0
        self.prc_rcv1 = prc_rcv1
        self.ms = ms

    def send(self, receiver, message) -> Tuple[str, float]:
        time = self.prc_snd0 + self.prc_snd1 * len(str(message))
        self.ms.put_message(receiver, message)
        return "sent", time

    def receive_one(self) -> Tuple[str, Message, float]:
        message = self.ms.get_one_message(self.proc_id)
        time = self.prc_rcv0 + self.prc_rcv1 * len(str(message))
        if message is not None:
            return "put_message", message, time
        else:
            return "continue", Message(0, 0, None, None, 0), 0

    def get_mes_amount(self, receiver: int, ms) -> int:
        return ms.get_mes_amount(receiver=receiver)
