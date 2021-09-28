import balancer.SimpleBalancer as sb


class MasterBalancer(sb.SimpleBalancer):
    def __init__(self, state, max_depth, proc_am, prc_blnc, alive_proc_am, T, S, m, M):
        super().__init__(state, max_depth, proc_am, prc_blnc)
        self.alive_proc_am = alive_proc_am
        self.T = T
        self.S = S
        self.M = M
        self.m = m

    def balance(self, state, subs_amount, add_args=None):
        self.state = state
        if state == "starting":
            return "solve", [self.proc_am * 2], self.prc_blnc
        elif state == "solved" or state == "nothing_to_receive":
            return "receive", [], self.prc_blnc
        elif state == "received_get_request":
            if isinstance(add_args, list) and len(add_args) == 3\
                    and isinstance(add_args[0], list) and len(add_args[0]) == 2:
                info = add_args[0]
                get_amount, sender = info[0], info[1]
                if subs_amount == 0:
                    self.alive_proc_am -= 1
                    return "send_exit", [sender], self.prc_blnc
                elif subs_amount >= get_amount:
                    return "send_subs", [sender, get_amount], self.prc_blnc
                elif subs_amount < get_amount:
                    return "send_subs", [sender, subs_amount], self.prc_blnc
            return "send_subs", [-1, -1], self.prc_blnc
        elif state == "received" or state == "received_put_subs_and_rec":
            self.state = "receive"
            return "receive", [], self.prc_blnc
        elif state == "sent_subs" or state == "sent_get_request" or state == "sent_exit":
            if self.alive_proc_am == 0:
                self.state = "exit"
                return "exit", [], self.prc_blnc
            else:
                self.state = "receive"
                return "receive", [], self.prc_blnc


class SlaveBalancer(sb.SimpleBalancer):

    def __init__(self, state, max_depth, proc_am, prc_blnc, T, S, m, M):
        super().__init__(state, max_depth, proc_am, prc_blnc)
        self.T = T
        self.S = S
        self.M = M
        self.m = m

    def balance(self, state, subs_amount, add_args=None):
        self.state = state
        if self.state == "starting" or self.state == "receiving" or self.state == "sent_get_request":
            return "receive", [], self.prc_blnc
        elif self.state == "nothing_to_receive":
            if isinstance(add_args, list) and len(add_args) == 3\
                    and isinstance(add_args[1], list) and isinstance(add_args[2], int):
                proc_ind = add_args[2]
                isSentGR = add_args[1][proc_ind]
                if not isSentGR:
                    add_args[1][proc_ind] = True
                    return "send_get_request", [0, 1], self.prc_blnc
                else:
                    self.state = "receive"
                    return "receive", [], self.prc_blnc
        elif state == "received_put_subs_and_rec":
            if isinstance(add_args, list) and len(add_args) == 3\
                    and isinstance(add_args[1], list) and isinstance(add_args[2], int):
                proc_ind = add_args[2]
                add_args[1][proc_ind] = False
            return "solve", [self.T], self.prc_blnc
        elif self.state == "solved":
            if subs_amount > 0:
                if subs_amount > self.S:
                    return "send_subs", [0, self.S], self.prc_blnc
                else:
                    return "solve", [self.T], self.prc_blnc
            else:
                if isinstance(add_args, list) and len(add_args) == 3 \
                        and isinstance(add_args[1], list) and isinstance(add_args[2], int):
                    proc_ind = add_args[2]
                    isSentGR = add_args[1][proc_ind]
                    if not isSentGR:
                        add_args[1][proc_ind] = True
                        return "send_get_request", [0, 1], self.prc_blnc
                    else:
                        self.state = "receive"
                        return "receive", [], self.prc_blnc
        elif self.state == "sent":
            self.state = "receive"
            return "receive", [], self.prc_blnc
        elif state == "got_exit_command":
            return "exit", [], self.prc_blnc
