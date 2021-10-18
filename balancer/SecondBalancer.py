import balancer.SimpleBalancer as sb


class MasterBalancer(sb.SimpleBalancer):

    def __init__(self, state, max_depth, proc_am, prc_blnc, alive_proc_am=None, arg=5):
        super().__init__(state, max_depth, proc_am, prc_blnc)
        self.alive_proc_am = proc_am - 1 if alive_proc_am is None else alive_proc_am
        self.arg = arg

    def balance(self, state, subs_amount, add_args=None):
        if state == "starting":
            self.state = state
            return "solve", [self.proc_am * self.arg]
        elif state == "solved":
            self.state = state
            return "receive", []
        elif state == "sent_subproblems" or state == "sent_get_request" or state == "sent_exit_command":
            if self.alive_proc_am == 0:
                self.state = "exit"
                return "exit", []
            else:
                self.state = "receive"
                return "receive", []
        elif state == "received_subproblems":
            self.state = "receive"
            return "receive", []
        elif state == "received_get_request":
            if isinstance(add_args, list) and len(add_args) == 3 \
                    and isinstance(add_args[0], list) and len(add_args[0]) == 2:
                info = add_args[0]
                get_amount, sender = info[0], info[1]
                if subs_amount == 0:
                    self.alive_proc_am -= 1
                    return "send_exit_command", [sender]
                elif subs_amount >= get_amount:
                    return "send_subproblems", [sender, get_amount]
                elif subs_amount < get_amount:
                    return "send_subproblems", [sender, subs_amount]
            else:
                raise Exception(f'Something went wrong: args={add_args}')
            return "send_subproblems", [-1, -1]
        else:
            raise Exception(f"Wrong state={state}")


class SlaveBalancer(sb.SimpleBalancer):

    def __init__(self, state, max_depth, proc_am, prc_blnc, arg=5):
        super().__init__(state, max_depth, proc_am, prc_blnc)
        self.arg = arg

    def balance(self, state, subs_amount, add_args=None):
        self.state = state
        if self.state == "starting" or self.state == "solved":
            return "send_get_request", [0, 1]
        elif self.state == "received_exit_command":
            return "exit", []
        elif self.state == "received_subproblems":
            if isinstance(add_args, list) and len(add_args) == 3 \
                    and isinstance(add_args[1], list) and isinstance(add_args[2], int):
                proc_ind = add_args[2]
                add_args[1][proc_ind] = False
            return "solve", [-1]
        elif state == "sent_get_request":
            return "receive", []
        else:
            raise Exception(f"Wrong state={state}")
