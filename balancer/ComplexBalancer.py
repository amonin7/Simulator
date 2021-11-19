from queue import Queue

import balancer.SimpleBalancer as sb


class MasterBalancer(sb.GenericBalancer):
    def __init__(self, max_depth, proc_am, prc_blnc, T=0, S=10, m=50, M=100, arg=10):
        super().__init__(max_depth, proc_am, prc_blnc)
        self.T = T
        self.S = S
        self.M = M
        self.m = m
        self.arg = arg
        self.cur_S = S
        self.poor_proc = Queue()

    def balance(self, state, subs_amount, add_args=None):
        if state == "starting":
            return "solve", [self.proc_am * self.arg]
        elif state == "solved" or state == "nothing_to_receive":
            return "receive", []
        elif state == "received_get_request":
            if isinstance(add_args, list) and len(add_args) == 3 \
                    and isinstance(add_args[0], list) and len(add_args[0]) == 2:
                info = add_args[0]
                get_amount, sender = info[0], info[1]
                if subs_amount == 0:
                    self.poor_proc.put((sender, get_amount))
                    if self.poor_proc.qsize() == self.proc_am - 1:
                        return "send_all_exit_command", [self.poor_proc]
                    else:
                        return "receive", []
                elif subs_amount >= get_amount:
                    return "send_subproblems", [sender, get_amount]
                elif subs_amount < get_amount:
                    return "send_subproblems", [sender, subs_amount]
            else:
                raise Exception(f"Wrong args list format: {add_args}")
        elif state == "received_subproblems":
            sender = add_args[0][1]
            if subs_amount < self.m:
                self.cur_S = self.S
            elif subs_amount > self.M:
                self.cur_S = 0
            return "send_S", [self.cur_S, sender]
        elif state == "sent_S":
            return "try_send_subproblems", [self.poor_proc]
        elif state == "sent_subproblems" or state == "sent_get_request"\
                or state == "sent_exit_command":
            return "receive", []
        elif state == "sent_all_exit_command":
            return "exit", []
        else:
            raise Exception(f"Wrong state={state}")


class SlaveBalancer(sb.GenericBalancer):

    def __init__(self, max_depth, proc_am, prc_blnc, alive_proc_am=0, T=200, S=10, m=0, M=0, arg=5):
        super().__init__(max_depth, proc_am, prc_blnc)
        self.alive_proc_am = alive_proc_am
        self.T = T
        self.S = S
        self.M = M
        self.m = m
        self.arg = arg

    def balance(self, state, subs_amount, add_args=None):
        if state == "sent_get_request" or state == "sent" or state == 'sent_subproblems':
            return "receive", []
        elif state == "starting":
            if isinstance(add_args, list) and len(add_args) == 3 \
                    and isinstance(add_args[0], list):
                isSentGR = add_args[1]
                if not isSentGR:
                    return "send_get_request", [0, 1]
                else:
                    raise Exception(f"Double needance of sending GR, add_args={add_args}")
            else:
                raise Exception(f"Wrong args list format: {add_args}")
        elif state == "received_subproblems" or state == 'received_S':
            return "solve", [self.T]
        elif state == "solved":
            if subs_amount > 0:
                if subs_amount > self.S:
                    return "send_subproblems", [0, self.S]
                else:
                    return "solve", [self.T]
            else:
                if isinstance(add_args, list) and len(add_args) == 3 \
                        and isinstance(add_args[0], list):
                    if not add_args[1]:
                        return "send_get_request", [0, 1]
                    else:
                        raise Exception(f"Wrong args list format: {add_args}")
                else:
                    raise Exception(f"Wrong args list format: {add_args}")
        elif state == "received_exit_command":
            return "exit", []
        else:
            raise Exception(f"Wrong state={state}")
