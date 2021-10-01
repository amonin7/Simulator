import balancer.SimpleBalancer as sb


class MasterBalancer(sb.SimpleBalancer):
    def __init__(self, state, max_depth, proc_am, prc_blnc, alive_proc_am=0, T=0, S=0, m=100, M=150, arg=10):
        super().__init__(state, max_depth, proc_am, prc_blnc)
        if alive_proc_am == 0:
            self.alive_proc_am = proc_am - 1
        else:
            self.alive_proc_am = alive_proc_am
        self.T = T
        self.S = S
        self.M = M
        self.m = m
        self.arg = arg
        self.last_t = T
        self.s_am = []

    def balance(self, state, subs_amount, add_args=None):
        self.state = state
        if state == "starting":
            return "solve", [self.proc_am * self.arg], self.prc_blnc
        elif state == "solved" or state == "nothing_to_receive":
            return "receive", [], self.prc_blnc
        elif state == "received_get_request":
            if isinstance(add_args, list) and len(add_args) == 3 \
                    and isinstance(add_args[0], list) and len(add_args[0]) == 2:
                info = add_args[0]
                get_amount, sender = info[0], info[1]
                if subs_amount == 0:
                    self.alive_proc_am -= 1
                    return "send_exit_command", [sender], self.prc_blnc
                elif subs_amount >= get_amount:
                    return "send_subproblems", [sender, get_amount], self.prc_blnc
                elif subs_amount < get_amount:
                    return "send_subproblems", [sender, subs_amount], self.prc_blnc
            else:
                raise Exception(f"Wrong args list format: {add_args}")
        elif state == "received" or state == "received_subproblems":
            sender = add_args[0][1]
            self.s_am.append(subs_amount)
            # TODO: звучит как проблема то, что не понятно, что тогда делать в случае, когда self.m < subs_am < self.M
            if subs_amount > self.M:
                return "send_S", [0, sender], self.prc_blnc
            # elif subs_amount > self.m:
            #     return "send_S", [self.S // 2, sender]
            else:
                return "send_S", [self.S, sender], self.prc_blnc
        elif state == "sent_subproblems" or state == "sent_get_request"\
                or state == "sent_exit_command" or state == "sent_S":
            if self.alive_proc_am == 0:
                self.state = "exit"
                return "exit", [], self.prc_blnc
            else:
                self.state = "receive"
                return "receive", [], self.prc_blnc
        else:
            raise Exception(f"Wrong state={state}")


class SlaveBalancer(sb.SimpleBalancer):

    def __init__(self, state, max_depth, proc_am, prc_blnc, alive_proc_am=0, T=200, S=10, m=0, M=0, arg=5):
        super().__init__(state, max_depth, proc_am, prc_blnc)
        self.alive_proc_am = alive_proc_am
        self.T = T
        self.S = S
        self.M = M
        self.m = m
        self.arg = arg

    def balance(self, state, subs_amount, add_args=None):
        self.state = state
        if self.state == "starting" or self.state == "sent_get_request" or self.state == "sent" or self.state == 'sent_subproblems':
            return "receive", [], self.prc_blnc
        elif self.state == "nothing_to_receive":
            if isinstance(add_args, list) and len(add_args) == 3 \
                    and isinstance(add_args[0], list):
                proc_ind = add_args[2]
                isSentGR = add_args[1][proc_ind]
                if not isSentGR:
                    add_args[1][proc_ind] = True
                    return "send_get_request", [0, 1], self.prc_blnc
                else:
                    self.state = "receive"
                    return "receive", [], self.prc_blnc
            else:
                raise Exception(f"Wrong args list format: {add_args}")
        elif state == "received_subproblems" or self.state == 'received_S':
            if isinstance(add_args, list) and len(add_args) == 3\
                    and isinstance(add_args[1], list) and isinstance(add_args[2], int):
                proc_ind = add_args[2]
                add_args[1][proc_ind] = False
            return "solve", [self.T], self.prc_blnc
        elif self.state == "solved":
            if subs_amount > 0:
                if subs_amount > self.S:
                    return "send_subproblems", [0, self.S], self.prc_blnc
                else:
                    return "solve", [self.T], self.prc_blnc
            else:
                if isinstance(add_args, list) and len(add_args) == 3 \
                        and isinstance(add_args[0], list):
                    proc_ind = add_args[2]
                    isSentGR = add_args[1][proc_ind]
                    if not isSentGR:
                        add_args[1][proc_ind] = True
                        return "send_get_request", [0, 1], self.prc_blnc
                    else:
                        raise Exception(f"Wrong args list format: {add_args}")
                else:
                    raise Exception(f"Wrong args list format: {add_args}")
        elif state == "received_exit_command":
            return "exit", [], self.prc_blnc
        else:
            raise Exception(f"no suitable state discovered for state={state}")
