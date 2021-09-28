import pandas as pd
import os


class TraceCollector:

    def __init__(self, filename, proc_am):
        self.filename = filename
        self.frame = {}
        for i in range(proc_am):
            self.frame['timestamp' + str(i)] = [0]
            self.frame['state' + str(i)] = ['init']
            self.frame['args' + str(i)] = ['-']
        self.proc_am = proc_am

    def write(self, proc_num, timestamp, state, args):
        self.frame['timestamp' + str(proc_num)].append(timestamp)
        self.frame['state' + str(proc_num)].append(state)
        self.frame['args' + str(proc_num)].append(args)

    def save(self):
        df = pd.DataFrame.from_dict(self.frame, orient='index').transpose()
        df.to_csv(os.getcwd() + "/" + self.filename)
        print("done")
