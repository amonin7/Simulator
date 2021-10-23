from typing import Tuple

import messages.SimpleMessage
from messages.SimpleMessage import Message2 as Message


class SimpleCommunicator:

    def __init__(self, proc_id, proc_am, prc_snd0=0, prc_snd1=0.0000003, prc_rcv0=0.007654, prc_rcv1=-1.51795035e-05):
        self.proc_id = proc_id
        self.proc_am = proc_am
        self.prc_snd0 = prc_snd0
        self.prc_snd1 = prc_snd1
        self.prc_rcv0 = prc_rcv0
        self.prc_rcv1 = prc_rcv1

    # TODO: make send return only 2 arguments
    def send(self, receiver, message, ms) -> Tuple[str, float]:
        time = self.prc_snd0 + self.prc_snd1 * len(str(message))
        ms.put_message(receiver, message)
        return "sent", [], time

    # TODO: leave all arguments from the method
    def receive_one(self, receiver, ms) -> Tuple[str, Message, float]:
        message = ms.get_one_message(receiver)
        time = self.prc_rcv0 + self.prc_rcv1 * len(str(message))
        if message is not None:
            return "put_message", message, time
        else:
            return "continue", Message(0, 0, None, None, 0), 0

    def get_mes_amount(self, receiver: int, ms) -> int:
        return ms.get_mes_amount(receiver=receiver)
