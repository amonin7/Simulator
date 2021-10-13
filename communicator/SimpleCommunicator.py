class SimpleCommunicator:

    def __init__(self, state, proc_id, proc_am, prc_snd0=0, prc_snd1=0.0000003, prc_rcv0=0.007654, prc_rcv1=-1.51795035e-05):
        self._state = state
        self.proc_id = proc_id
        self.proc_am = proc_am
        self.prc_snd0 = prc_snd0
        self.prc_snd1 = prc_snd1
        self.prc_rcv0 = prc_rcv0
        self.prc_rcv1 = prc_rcv1

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    def send(self, receiver, message, ms):
        time = self.prc_snd0 + self.prc_snd1 * len(str(message))
        ms.put_message(receiver, message)
        return "sent", [], time

    def receive(self, receiver, ms):
        message = ms.get_messages(receiver)
        time = self.prc_rcv0 + self.prc_rcv1 * len(str(message))
        if len(message) != 0:
            return "put_messages", message, time
        else:
            return "continue", [], time

    def receive_one(self, receiver, ms):
        message = ms.get_one_message(receiver)
        time = self.prc_rcv0 + self.prc_rcv1 * len(str(message))
        if message is not None:
            return "put_message", message, time
        else:
            return "continue", None, 0

    def get_mes_amount(self, receiver: int, ms) -> int:
        return ms.get_mes_amount(receiver=receiver)
