class SimpleCommunicator:

    def __init__(self, state, proc_id, proc_am, prc_snd=0, prc_rcv=0):
        self._state = state
        self.proc_id = proc_id
        self.proc_am = proc_am
        self.prc_snd = prc_snd
        self.prc_rcv = prc_rcv

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    def send(self, receiver, message, ms):
        time = self.prc_snd
        ms.put_message(receiver, message)
        return "sent", [], time

    def receive(self, receiver, ms):
        message = ms.get_messages(receiver)
        time = len(message) * self.prc_rcv
        if len(message) != 0:
            return "put_messages", message, time
        else:
            return "continue", [], time

    def receive_one(self, receiver, ms):
        message = ms.get_one_message(receiver)
        time = self.prc_rcv
        if message is not None:
            return "put_message", message, time
        else:
            return "continue", None, time

    def get_mes_amount(self, receiver: int, ms) -> int:
        return ms.get_mes_amount(receiver=receiver)
