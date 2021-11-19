class GenericBalancer:

    def __init__(self, max_depth, proc_am, prc_blnc=0):
        self.max_depth = max_depth
        self.prc_blnc = prc_blnc
        self.proc_am = proc_am

    def balance(self, state, subs_amount, add_args=None):
        print("Balancing")


class MasterBalancer(GenericBalancer):

    def __init__(self, max_depth, proc_am, prc_blnc, arg=5):
        super().__init__(max_depth, proc_am, prc_blnc)
        self.arg = arg

    '''
    :returns status, where to send, how many to send
    where to send -- either list of proc numbers or -1 (means all others)
    how many to send -- either list of amounts of tasks to each process to send
    or -1 (means all tasks should be separated into equal groups and send to all processes)
    '''

    def balance(self, state, subs_amount, add_args=None):
        if state == "starting":
            return "solve", [self.proc_am * self.arg], self.prc_blnc
        if state == "solved":
            return "send_all", [[-1], [-1]], self.prc_blnc
        if state == "sent_subproblems":
            return "exit", [], self.prc_blnc


class SlaveBalancer(GenericBalancer):
    def __init__(self, max_depth, proc_am, prc_blnc, arg=5):
        super().__init__(max_depth, proc_am, prc_blnc)
        self.arg = arg

    def balance(self, state, subs_amount, add_args=None):
        if state == "starting":
            return "receive", [], self.prc_blnc
        elif state == "received_subproblems":
            return "solve", [-1], self.prc_blnc
        elif state == "solved":
            return "exit", [], self.prc_blnc
        else:
            return "bound", [], self.prc_blnc
