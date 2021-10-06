import balancer.ComplexBalancer as sb
import subproblems.SimpleSubproblem as sp
import solver.SimpleSolver as slv
import communicator.SimpleCommunicator as com
import messages.MessageService as ms
import messages.SimpleMessage as sm
import numpy as np
import route.TraceCollector as rc
import route.CommunicationCollector as cc


class Engine:

    def __init__(self,
                 proc_amount,
                 max_depth,
                 arg=7,
                 price_put=0.0,
                 price_get=0.0,
                 price_solve=0.0000378,
                 price_balance=0.0000235,
                 price_receive=0.0001550,
                 price_send=0.0000043):
        self.arg = arg
        self.processes_amount = proc_amount  # amount of simulated processes
        self.max_depth = max_depth  # max depth of solving tree
        self.price_rcv = price_receive  # price of receiving message
        self.price_snd = price_send  # price of sending message
        self.price_put = price_put  # price of putting message into solver
        self.price_get = price_get  # price of getting message from solver
        self.price_blc = price_balance  # price of balancing
        self.price_slv = price_solve  # price of solving

        self.mes_service = ms.MessageService()
        self.route_collector = rc.TraceCollector('TraceC.csv', self.processes_amount)
        self.comm_collector = cc.CommunicationCollector('CommunicationC.csv')
        self.balancers = []
        self.solvers = []
        self.communicators = []
        self.timers = []
        self.downtime = []  # amount of time when process was without any tasks
        self.isDoneStatuses = []
        self.isSentRequest = []
        self.state = []

        self.solved = 0

    # TODO: вынести в отдельный метод вне ENGINE
    def initializeAll(self) -> None:
        master = sb.MasterBalancer("start", max_depth=self.max_depth,
                                   proc_am=self.processes_amount,
                                   prc_blnc=self.price_blc
                                   ,
                                   T=200,
                                   S=10,
                                   m=100,
                                   M=150
                                   ,
                                   arg=self.arg
                                   )
        self.balancers = [master]
        self.solvers = [slv.SimpleSolver(subproblems=[sp.SimpleSubProblem(0, 0, 0)],
                                         records=0,
                                         is_record_updated=False,
                                         max_depth=self.max_depth,
                                         prc_put=self.price_put,
                                         prc_slv=self.price_slv)]
        self.communicators = [com.SimpleCommunicator("ready",
                                                     proc_id=0,
                                                     proc_am=self.processes_amount,
                                                     prc_rcv1=0.0033543942799634805,
                                                     prc_rcv2=-1.51795035e-05,
                                                     prc_snd=self.price_snd)]
        self.timers = [0.0] * self.processes_amount
        self.downtime = [0.0] * self.processes_amount
        self.isDoneStatuses = [False] * self.processes_amount
        self.isSentRequest = [False] * self.processes_amount
        self.state = ["starting"] * self.processes_amount

        for i in range(1, self.processes_amount):
            slave = sb.SlaveBalancer("start", max_depth=self.max_depth, proc_am=self.processes_amount,
                                     prc_blnc=self.price_blc
                                     ,
                                     alive_proc_am=self.processes_amount - 1
                                     ,
                                     T=200,
                                     S=10,
                                     m=100,
                                     M=150
                                     ,
                                     arg=self.arg
                                     )
            self.balancers.append(slave)

            solver = slv.SimpleSolver(subproblems=[], records=0, is_record_updated=False, max_depth=self.max_depth,
                                      prc_put=self.price_put, prc_slv=self.price_slv)
            self.solvers.append(solver)

            communicator = com.SimpleCommunicator("ready", proc_id=i, proc_am=self.processes_amount,
                                                  prc_rcv1=0.0033543942799634805,
                                                  prc_rcv2=-1.51795035e-05,
                                                  prc_snd=self.price_snd)
            self.communicators.append(communicator)

    def run(self) -> None:
        self.initializeAll()
        proc_ind = 0
        while True:
            state = self.state[proc_ind]
            if state == "receiving":
                command, outputs = "receive", []
            else:
                command, outputs = self.balance(proc_ind,
                                                state=state,
                                                subs_amount=self.solvers[proc_ind].get_sub_amount(),
                                                add_args=[[], self.isSentRequest[proc_ind], proc_ind])
            if command == "start" or command == "receive":
                receive_status, outputs = self.receive_message(proc_id=proc_ind)
                if receive_status != "received_exit_command" and receive_status != "nothing_to_receive":
                    command, outputs = self.balance(proc_ind,
                                                    state=receive_status,
                                                    subs_amount=self.solvers[proc_ind].get_sub_amount(),
                                                    add_args=[outputs, self.isSentRequest, proc_ind])
                    if command == "send_subproblems":
                        self.state[proc_ind] = self.send_subproblems(proc_id=proc_ind, subs_am=outputs[1],
                                                                     dest_id=outputs[0])
                    elif command == "send_get_request":
                        self.state[proc_ind] = self.send_get_request(dest_proc_id=outputs[0],
                                                                     sender_proc_id=proc_ind,
                                                                     tasks_amount=outputs[1])
                    elif command == "send_exit_command":
                        self.state[proc_ind] = self.send_exit(proc_id=proc_ind, dest_id=outputs[0])
                    elif command == "solve":
                        tasks_am = outputs[0]
                        self.state[proc_ind] = self.solve(proc_id=proc_ind, tasks_amount=tasks_am)
                    elif command == "send_S":
                        [S, sender] = outputs
                        self.state[proc_ind] = self.send_S(proc_id=proc_ind, s=S, sender=sender)
                    elif command == "receive":
                        self.state[proc_ind] = "receiving"
                    elif command == "send_all_exit_command":
                        while not outputs[0].empty():
                            (receiver, get_amount) = outputs[0].get()
                            self.state[proc_ind] = self.send_exit(proc_id=proc_ind, dest_id=receiver)
                        self.state[proc_ind] = "sent_all_exit_command"
                    else:
                        raise Exception(f"wrong command={command}")
                elif receive_status == "nothing_to_receive":
                    self.state[proc_ind] = "receiving"
                else:
                    self.isDoneStatuses[proc_ind] = True
            elif command == "send_subproblems":
                self.state[proc_ind] = self.send_subproblems(proc_id=proc_ind, subs_am=outputs[1], dest_id=outputs[0])
            elif command == "send_all":
                self.state[proc_ind] = self.send_all_subs_to_all_proc(proc_id=proc_ind)
            elif command == "send_get_request":
                self.state[proc_ind] = self.send_get_request(dest_proc_id=outputs[0],
                                                             sender_proc_id=proc_ind,
                                                             tasks_amount=outputs[1])
            elif command == "send_exit":
                self.state[proc_ind] = self.send_exit(proc_id=proc_ind, dest_id=outputs[0])
            elif command == "solve":
                tasks_am = outputs[0]
                state = self.solve(proc_id=proc_ind, tasks_amount=tasks_am)
                self.state[proc_ind] = state
            elif command == "exit":
                self.isDoneStatuses[proc_ind] = True
                if proc_ind == 0:
                    print(self.route_collector.frame['timestamp0'][-1])
                # break
            elif command == "send_all_exit_command":
                while not outputs[0].empty():
                    (receiver, get_amount) = outputs[0].get()
                    self.state[proc_ind] = self.send_exit(proc_id=proc_ind, dest_id=receiver)
                self.state[proc_ind] = "sent_all_exit_command"
            elif command == "try_send_subproblems":
                q = outputs[0]
                while not q.empty() and self.solvers[proc_ind].get_sub_amount() > 0:
                    (receiver, get_amount) = q.get()
                    self.send_subproblems(proc_ind, get_amount, receiver)
                self.state[proc_ind] = "sent_subproblems"
            else:
                raise Exception(f"wrong command={command}")

            proc_ind = (proc_ind + 1) % self.processes_amount
            i = 0
            while self.isDoneStatuses[proc_ind]:
                i += 1
                if i > self.processes_amount + 1:
                    break
                proc_ind = (proc_ind + 1) % self.processes_amount
            if i > self.processes_amount + 1:
                break

        print(f"subs_am={self.solved}")
        self.route_collector.save()
        self.comm_collector.save()

    def start(self, proc_id, state):
        rcv_output = self.receive_message(proc_id=proc_id)
        command, outputs = self.balance(proc_id, state, subs_amount=self.solvers[proc_id].get_sub_amount(),
                                        add_args=[[], self.isSentRequest, proc_id])
        return command, outputs

    def receive_message(self, proc_id):
        command, message, time_for_rcv = self.communicators[proc_id].receive_one(proc_id, self.mes_service)
        if command == "put_message":
            if self.timers[proc_id] < message.timestamp:
                self.route_collector.write(proc_id,
                                           str(round(self.timers[proc_id], 7)) + '%' + str(
                                               round(message.timestamp, 7)),
                                           'Await for receive',
                                           '-')
                self.route_collector.write(proc_id,
                                           str(round(message.timestamp, 7)) + '%' + str(
                                               round(message.timestamp + time_for_rcv, 7)),
                                           'Receive',
                                           message.mes_type)
                self.downtime[proc_id] += message.timestamp - self.timers[proc_id]
                self.timers[proc_id] = message.timestamp + time_for_rcv
            else:
                self.route_collector.write(proc_id,
                                           str(round(self.timers[proc_id], 7)) + '%' + str(
                                               round(self.timers[proc_id] + time_for_rcv, 7)),
                                           'Receive',
                                           message.mes_type)
                self.timers[proc_id] += time_for_rcv
            self.comm_collector.write_recv(message.sender, proc_id, message.timestamp, self.timers[proc_id])
            if message.mes_type == "get_request":
                return "received_get_request", [message.payload, message.sender]
            elif message.mes_type == "subproblems":
                self.solvers[proc_id].putSubproblems(message.payload)
                return "received_subproblems", [message.payload, message.sender]
            elif message.mes_type == "exit_command":
                return "received_exit_command", []
            elif message.mes_type == "S":
                self.balancers[proc_id].S = message.payload
                return "received_S", []
            else:
                raise Exception(f"wrong message_type={message.mes_type}")
        elif command == "continue":
            return "nothing_to_receive", []

    def solve(self, proc_id, tasks_amount):
        state, solved_am, time = self.solvers[proc_id].solve(tasks_amount)
        if state == "solved":
            self.route_collector.write(proc_id,
                                       str(round(self.timers[proc_id], 7)) + '%' + str(
                                           round(self.timers[proc_id] + time, 7)),
                                       'Solve',
                                       'tasks_am=' + str(tasks_amount))
            self.timers[proc_id] += time
        else:
            raise Exception('Solving went wrong')
        self.solved += solved_am
        return state

    def balance(self, proc_id, state, subs_amount, add_args):
        command, outputs = self.balancers[proc_id].balance(state=state,
                                                           subs_amount=subs_amount,
                                                           add_args=add_args)
        time = self.price_blc
        self.route_collector.write(proc_id,
                                   str(round(self.timers[proc_id], 7)) + '%' + str(
                                       round(self.timers[proc_id] + time, 7)),
                                   'Balance',
                                   'state=' + state)
        self.timers[proc_id] += time
        return command, outputs

    def send_get_request(self, dest_proc_id, sender_proc_id, tasks_amount):
        state, _, time = self.communicators[sender_proc_id].send(
            receiver=dest_proc_id,
            message=sm.Message2(sender=sender_proc_id,
                                dest=dest_proc_id,
                                mes_type="get_request",
                                payload=tasks_amount,
                                timestamp=self.timers[sender_proc_id]),
            ms=self.mes_service
        )
        if state != "sent":
            raise Exception('Sending went wrong')
        # self.isSentRequest[sender_proc_id] = True
        self.save_time(proc_id=sender_proc_id, timestamp=time, dest_proc=dest_proc_id)
        # command, outputs = self.balance(sender_proc_id, state)
        return "sent_get_request"

    def send_subproblems(self, proc_id, subs_am, dest_id):
        message = sm.Message2(sender=proc_id,
                              dest=dest_id,
                              mes_type="subproblems",
                              payload=self.solvers[proc_id].getSubproblems(subs_am),
                              timestamp=self.timers[proc_id])
        state, outputs, time = self.communicators[proc_id].send(
            receiver=dest_id,
            message=message,
            ms=self.mes_service
        )
        if state != "sent":
            raise Exception('Sending went wrong')
        self.save_time(proc_id=proc_id, timestamp=time, dest_proc=dest_id)
        return "sent_subproblems"

    def send_exit(self, proc_id, dest_id):
        state, _, time = self.communicators[proc_id].send(
            receiver=dest_id,
            message=sm.Message2(sender=proc_id,
                                dest=dest_id,
                                mes_type="exit_command",
                                payload=None,
                                timestamp=self.timers[proc_id]),
            ms=self.mes_service
        )
        if state != "sent":
            raise Exception('Sending went wrong')
        self.save_time(proc_id=proc_id, timestamp=time, dest_proc=proc_id)
        return "sent_exit_command"

    def send_all_subs_to_all_proc(self, proc_id):
        probs = self.solvers[proc_id].getSubproblems(-1)
        probs_amnt = len(probs)
        part = 1 / (self.processes_amount - 1)
        for dest_proc in range(1, self.processes_amount):
            message_list = probs[
                           int((dest_proc - 1) * probs_amnt * part): int(dest_proc * probs_amnt * part)]
            message = sm.Message2(sender=proc_id,
                                  dest=dest_proc,
                                  mes_type="subproblems",
                                  payload=message_list,
                                  timestamp=self.timers[proc_id])
            state, outputs, time = self.communicators[proc_id].send(
                receiver=dest_proc,
                message=message,
                ms=self.mes_service
            )
            self.save_time(proc_id=proc_id, timestamp=time, dest_proc=dest_proc)
        return "sent_subproblems"

    def save_time(self, proc_id, timestamp, dest_proc):
        self.route_collector.write(proc_id,
                                   str(round(self.timers[proc_id], 7)) + '%' + str(
                                       round(self.timers[proc_id] + timestamp, 7)),
                                   'Send',
                                   'dest=' + str(dest_proc))
        self.timers[proc_id] += timestamp

    def send_S(self, proc_id, s, sender):
        state, _, time = self.communicators[proc_id].send(
            receiver=sender,
            message=sm.Message2(sender=proc_id,
                                dest=sender,
                                mes_type="S",
                                payload=s,
                                timestamp=self.timers[proc_id]),
            ms=self.mes_service
        )
        if state != "sent":
            raise Exception('Sending went wrong')
        self.save_time(proc_id=proc_id, timestamp=time, dest_proc=proc_id)
        return "sent_S"


if __name__ == "__main__":
    # proc_am = [10, 50, 100, 200, 500, 1000]
    eng = Engine(proc_amount=10, max_depth=15)
    eng.run()
