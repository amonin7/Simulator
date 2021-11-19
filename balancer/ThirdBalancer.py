import balancer.SimpleBalancer as sb


class MasterBalancer(sb.GenericBalancer):
    def __init__(self, max_depth, proc_am, prc_blnc, alive_proc_am, T, S, m, M, arg=5):
        super().__init__(max_depth, proc_am, prc_blnc)
        self.alive_proc_am = alive_proc_am
        self.T = T
        self.S = S
        self.M = M
        self.m = m
        self.arg = arg

    def balance(self, state, subs_amount, add_args=None):
        if state == "starting":
            return "solve", [self.proc_am * self.arg]
        elif state == "solved" or state == "nothing_to_receive":
            return "receive", []
        elif state == "received_get_request":
            if isinstance(add_args, list) and len(add_args) == 3\
                    and isinstance(add_args[0], list) and len(add_args[0]) == 2:
                info = add_args[0]
                get_amount, sender = info[0], info[1]
                if subs_amount == 0:
                    self.alive_proc_am -= 1
                    return "send_exit", [sender]
                elif subs_amount >= get_amount:
                    return "send_subproblems", [sender, get_amount]
                elif subs_amount < get_amount:
                    return "send_subproblems", [sender, subs_amount]
            else:
                raise Exception(f"Wrong args list format: {add_args}")
        elif state == "received" or state == "received_subproblems":
            return "receive", []
        elif state == "sent_subproblems" or state == "sent_get_request" or state == "sent_exit_command":
            if self.alive_proc_am == 0:
                return "exit", []
            else:
                return "receive", []


class SlaveBalancer(sb.GenericBalancer):

    def __init__(self, max_depth, proc_am, prc_blnc, alive_proc_am, T, S, m, M, arg=5):
        super().__init__(max_depth, proc_am, prc_blnc)
        self.alive_proc_am = alive_proc_am
        self.T = T
        self.S = S
        self.M = M
        self.m = m
        self.arg=arg

    def balance(self, state, subs_amount, add_args=None):
        if state == "starting" or state == "sent_get_request" or state == "sent":
            return "receive", []
        elif state == "nothing_to_receive":
            if isinstance(add_args, list) and len(add_args) == 3\
                    and isinstance(add_args[1], list) and isinstance(add_args[2], int):
                proc_ind = add_args[2]
                is_sent_gr = add_args[1][proc_ind]
                if not is_sent_gr:
                    add_args[1][proc_ind] = True
                    return "send_get_request", [0, 1]
                else:
                    return "receive", []
        elif state == "received_subproblems":
            if isinstance(add_args, list) and len(add_args) == 3\
                    and isinstance(add_args[1], list) and isinstance(add_args[2], int):
                proc_ind = add_args[2]
                add_args[1][proc_ind] = False
            return "solve", [self.T]
        elif state == "solved" or state == 'sent_subproblems':
            if subs_amount > 0:
                if subs_amount > self.S:
                    return "send_subproblems", [0, self.S]
                else:
                    return "solve", [self.T]
            else:
                if isinstance(add_args, list) and len(add_args) == 3 \
                        and isinstance(add_args[1], list) and isinstance(add_args[2], int):
                    proc_ind = add_args[2]
                    is_sent_gr = add_args[1][proc_ind]
                    if not is_sent_gr:
                        add_args[1][proc_ind] = True
                        return "send_get_request", [0, 1]
                    else:
                        return "receive", []
        elif state == "got_exit_command":
            return "exit", []
        else:
            raise Exception(f"no suitable state discovered for state={state}")
