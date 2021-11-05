import balancer.ThirdBalancer as sb
# import balancer.SecondBalancer as sb
# import balancer.SimpleBalancer as sb
import subproblems.SimpleSubproblem as sp
import solver.SimpleSolver as slv
import communicator.SimpleCommunicator as com
import messages.MessageRepo as ms
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
                 price_solve=0.0000424,
                 price_balance=0.0000405,
                 price_receive=0.0001913,
                 price_send=0.0000031):
        self.arg = arg
        self.processes_amount = proc_amount  # amount of simulated processes
        self.max_depth = max_depth  # max depth of solving tree
        self.price_rcv = price_receive  # price of receiving message
        self.price_snd = price_send  # price of sending message
        self.price_put = price_put  # price of putting message into solver
        self.price_get = price_get  # price of getting message from solver
        self.price_blc = price_balance  # price of balancing
        self.price_slv = price_solve  # price of solving

        self.mes_service = ms.MessageRepo()
        self.route_collector = rc.TraceCollector('Trace33.csv', self.processes_amount)
        self.comm_collector = cc.CommunicationCollector('Communication33.csv')
        self.balancers = []
        self.solvers = []
        self.communicators = []
        self.timers = []
        self.downtime = []  # amount of time when process was without any tasks
        self.isDoneStatuses = []
        self.isSentRequest = []
        self.state = []

    # TODO: вынести в отдельный метод вне ENGINE
    def initializeAll(self) -> None:
        master = sb.MasterBalancer(max_depth=self.max_depth,
                                   proc_am=self.processes_amount,
                                   prc_blnc=self.price_blc
                                   ,
                                   alive_proc_am=self.processes_amount - 1
                                   ,
                                   T=200,
                                   S=10,
                                   m=100,
                                   M=1000
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
        self.communicators = [com.SimpleCommunicator(proc_id=0,
                                                     proc_am=self.processes_amount,
                                                     ms=self.mes_service,
                                                     prc_rcv=self.price_rcv,
                                                     prc_snd=self.price_snd)]
        self.timers = [0.0] * self.processes_amount
        self.downtime = [0.0] * self.processes_amount
        self.isDoneStatuses = [False] * self.processes_amount
        self.isSentRequest = [False] * self.processes_amount
        self.state = ["starting"] * self.processes_amount

        for i in range(1, self.processes_amount):
            slave = sb.SlaveBalancer(max_depth=self.max_depth, proc_am=self.processes_amount,
                                     prc_blnc=self.price_blc
                                     ,
                                     alive_proc_am=self.processes_amount - 1
                                     ,
                                     T=200,
                                     S=10,
                                     m=100,
                                     M=1000
                                     ,
                                     arg=self.arg
                                     )
            self.balancers.append(slave)

            solver = slv.SimpleSolver(subproblems=[], records=0, is_record_updated=False, max_depth=self.max_depth,
                                      prc_put=self.price_put, prc_slv=self.price_slv)
            self.solvers.append(solver)

            communicator = com.SimpleCommunicator(proc_id=i, proc_am=self.processes_amount, ms=self.mes_service,
                                                  prc_rcv=self.price_rcv,
                                                  prc_snd=self.price_snd)
            self.communicators.append(communicator)

    def run(self) -> None:
        self.initializeAll()
        proc_ind = 0
        while True:
            state = self.state[proc_ind]
            if state == "receiving":
                command = "receive"
            else:
                command, outputs = self.balance(proc_ind,
                                                state=state,
                                                subs_amount=self.solvers[proc_ind].get_sub_amount(),
                                                add_args=[[], self.isSentRequest, proc_ind])
            if command == "start" or command == "receive":
                receive_status, outputs = self.receive_message(proc_id=proc_ind)
                if receive_status != "received_exit_command":
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
                    elif command == "send_exit":
                        self.state[proc_ind] = self.send_exit(proc_id=proc_ind, dest_id=outputs[0])
                    elif command == "solve":
                        tasks_am = outputs[0]
                        self.state[proc_ind] = self.solve(proc_id=proc_ind, tasks_amount=tasks_am)
                    elif command == "receive":
                        self.state[proc_ind] = "receiving"
                    else:
                        raise Exception(f"wrong command={command}")
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
                # break

            # TODO: добавить в метод balance параметром состояние солвера (эм_таскс + рекорд)

            # TODO: comp record
            # if command == "stop" and self.solvers[proc_ind].compareRecord(optimal_value):
            #     optimal_value = self.solvers[proc_ind].getRecord()
            proc_ind = (proc_ind + 1) % self.processes_amount
            i = 0
            while self.isDoneStatuses[proc_ind]:
                i += 1
                if i > self.processes_amount + 1:
                    break
                proc_ind = (proc_ind + 1) % self.processes_amount
            if i > self.processes_amount + 1:
                break

        self.route_collector.save()
        self.comm_collector.save()

    def start(self, proc_id, state):
        rcv_output = self.receive_message(proc_id=proc_id)
        command, outputs = self.balance(proc_id, state, subs_amount=self.solvers[proc_id].get_sub_amount(),
                                        add_args=[[], self.isSentRequest, proc_id])
        return command, outputs

    def receive_message(self, proc_id):
        command, message, time_for_rcv = self.communicators[proc_id].receive_one()
        if command == "put_message":
            if self.timers[proc_id] < message.timestamp:
                self.route_collector.write(proc_id,
                                           str(round(self.timers[proc_id], 3)) + '-' + str(
                                               round(message.timestamp, 3)),
                                           'Await for receive',
                                           '-')
                self.route_collector.write(proc_id,
                                           str(round(message.timestamp, 3)) + '-' + str(
                                               round(message.timestamp + time_for_rcv, 3)),
                                           'Receive',
                                           message.mes_type)
                self.downtime[proc_id] += message.timestamp - self.timers[proc_id]
                self.timers[proc_id] = message.timestamp + time_for_rcv
            else:
                self.route_collector.write(proc_id,
                                           str(round(self.timers[proc_id], 3)) + '-' + str(
                                               round(self.timers[proc_id] + time_for_rcv, 3)),
                                           'Receive',
                                           message.mes_type)
                self.timers[proc_id] += time_for_rcv
            self.comm_collector.write_recv(message.sender, proc_id, message.timestamp, self.timers[proc_id])
            if message.mes_type == "get_request":
                return "received_get_request", [message.payload, message.sender]
            elif message.mes_type == "subproblems":
                self.solvers[proc_id].putSubproblems(message.payload)
                return "received_subproblems", []
            elif message.mes_type == "exit_command":
                return "received_exit_command", []

            return "received", []
        elif command == "continue":
            return "nothing_to_receive", []

    def solve(self, proc_id, tasks_amount):
        state, _, time = self.solvers[proc_id].solve(tasks_amount)
        if state == "solved":
            self.route_collector.write(proc_id,
                                       str(round(self.timers[proc_id], 3)) + '-' + str(
                                           round(self.timers[proc_id] + time, 3)),
                                       'Solve',
                                       'tasks_am=' + str(tasks_amount))
            self.timers[proc_id] += time
        else:
            raise Exception('Solving went wrong')
        return state

    def balance(self, proc_id, state, subs_amount, add_args):
        command, outputs, time = self.balancers[proc_id].balance(state=state,
                                                                 subs_amount=subs_amount,
                                                                 add_args=add_args)
        if state == "nothing_to_receive" and command == "receive":
            return command, outputs
        self.route_collector.write(proc_id,
                                   str(round(self.timers[proc_id], 3)) + '-' + str(
                                       round(self.timers[proc_id] + time, 3)),
                                   'Balance',
                                   'state=' + state)
        self.timers[proc_id] += time
        return command, outputs

    def send_get_request(self, dest_proc_id, sender_proc_id, tasks_amount):
        state, time = self.communicators[sender_proc_id].send(
            receiver=dest_proc_id,
            message=sm.Message2(sender=sender_proc_id,
                                dest=dest_proc_id,
                                mes_type="get_request",
                                payload=tasks_amount,
                                timestamp=self.timers[sender_proc_id]),
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
        state, time = self.communicators[proc_id].send(
            receiver=dest_id,
            message=message,
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
            state, time = self.communicators[proc_id].send(
                receiver=dest_proc,
                message=message,
                            )
            self.save_time(proc_id=proc_id, timestamp=time, dest_proc=dest_proc)
        return "sent_subproblems"

    def send(self, proc_id, messages_to_send):
        is_sent = True
        """
        outputs[0] -- is the list of numbers of processes, where we will send subproblems

        outputs[1] -- is the list of amounts of subproblems, which we will send to other processes
        """
        if len(messages_to_send) == 2:
            if len(messages_to_send[0]) >= 1 and messages_to_send[0][0] == -1:
                if len(messages_to_send[1]) >= 1 and messages_to_send[1][0] == -1:
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
                        state, time = self.communicators[proc_id].send(
                            receiver=dest_proc,
                            message=message,
                                                    )
                        is_sent = is_sent and (state == 'sent')
                        self.save_time(proc_id=proc_id, timestamp=time, dest_proc=dest_proc)
                elif len(messages_to_send[1]) == 1:
                    send_amount = messages_to_send[1][0]
                    for dest_proc in range(1, self.processes_amount):
                        probs_to_send = self.solvers[proc_id].getSubproblems(send_amount)
                        if len(probs_to_send) == 0 and dest_proc == 1:
                            raise Exception('There is nothing to send')
                        elif len(probs_to_send) == 0:
                            break
                        else:
                            message_list = probs_to_send
                            message = sm.Message2(sender=proc_id,
                                                  dest=dest_proc,
                                                  mes_type="subproblems",
                                                  payload=message_list,
                                                  timestamp=self.timers[proc_id])
                            state, time = self.communicators[proc_id].send(
                                receiver=dest_proc,
                                message=message,
                                                            )
                            is_sent = is_sent and (state == 'sent')
                            self.save_time(proc_id=proc_id, timestamp=time, dest_proc=dest_proc)
                elif len(messages_to_send[1]) != 1:
                    raise Exception('Unexpected arguments are passes to send function')
            elif len(messages_to_send[1]) == len(messages_to_send[0]):
                probs = self.solvers[proc_id].getSubproblems(np.sum(messages_to_send[1]))
                for com_id in messages_to_send[0]:
                    list_to_put = []
                    for dest_proc in range(messages_to_send[1][com_id]):
                        list_to_put.append(probs.pop())
                    message_list = list_to_put
                    message = sm.Message2(sender=proc_id,
                                          dest=com_id,
                                          mes_type="subproblems",
                                          payload=message_list,
                                          timestamp=self.timers[proc_id])
                    state, time = self.communicators[proc_id].send(
                        receiver=com_id,
                        message=message,
                                            )
                    is_sent = is_sent and (state == 'sent')
                    self.save_time(proc_id=proc_id, timestamp=time, dest_proc=com_id)
                if len(probs) > 0:
                    self.solvers[0].putSubproblems(probs)
            elif len(messages_to_send[1]) >= 1 and messages_to_send[1][0] == -1 and len(messages_to_send[0]) >= 1:
                probs = self.solvers[-1].getSubproblems(-1)
                probs_amnt = len(probs)
                part = 1 / len(messages_to_send[0])
                for dest_proc in messages_to_send[0]:
                    message_list = probs[int((dest_proc - 1) * probs_amnt * part): int(dest_proc * probs_amnt * part)]
                    message = sm.Message2(sender=proc_id,
                                          dest=dest_proc,
                                          mes_type="subproblems",
                                          payload=message_list,
                                          timestamp=self.timers[proc_id])
                    state, time = self.communicators[proc_id].send(
                        receiver=dest_proc,
                        message=message,
                                            )
                    is_sent = is_sent and (state == 'sent')
                    self.save_time(proc_id=proc_id, timestamp=time, dest_proc=dest_proc)

        if not is_sent:
            raise Exception('Sending went wrong')
        else:
            state = "sent"

        command, outputs = self.balance(proc_id, state,
                                        subs_amount=self.solvers[proc_id].get_sub_amount(),
                                        add_args=[[], self.isSentRequest, proc_id])
        return command, outputs

    def save_time(self, proc_id, timestamp, dest_proc):
        self.route_collector.write(proc_id,
                                   str(round(self.timers[proc_id], 3)) + '-' + str(
                                       round(self.timers[proc_id] + timestamp, 3)),
                                   'Send',
                                   'dest=' + str(dest_proc))
        self.timers[proc_id] += timestamp


if __name__ == "__main__":
    # proc_am = [10, 50, 100, 200, 500, 1000]
    eng = Engine(proc_amount=10, max_depth=15)
    eng.run()
