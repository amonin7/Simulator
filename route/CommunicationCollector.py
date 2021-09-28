import pandas as pd
from collections import defaultdict


class CommunicationCollector:

    def __init__(self, filename):
        self.filename = filename
        self.frame = defaultdict(list)

    def write_recv(self, sender, receiver, time_send, time_recv):
        self.frame[(sender, receiver)].append(f'{time_send}:{time_recv}')

    def save(self):
        df = pd.DataFrame.from_dict(self.frame, orient='index').transpose()
        df.to_csv(self.filename)
