import random
import subproblems.SimpleSubproblem as subprob


class SimpleSolver:

    def __init__(self, subproblems, records, is_record_updated, max_depth, prc_put=0.0, prc_slv=1.0):
        self.subproblems = subproblems
        self.records = records
        self.is_record_updated = is_record_updated
        self.max_depth = max_depth
        self.testDict = {1: 0}
        self.prc_put = prc_put
        self.prc_slv = prc_slv
        # random.seed(42)

    def getSubproblems(self, subprobs_amount):
        if subprobs_amount == -1:
            subprobForReturn = self.subproblems
            self.subproblems = []
        else:
            subprobForReturn = self.subproblems[:subprobs_amount]
            for x in subprobForReturn:
                self.subproblems.remove(x)
        return subprobForReturn

    def getRecord(self):
        return self.records

    def compareRecord(self, otherRecord):
        return self.records > otherRecord

    def get_sub_amount(self):
        return len(self.subproblems)

    def getInfo(self):
        return [len(self.subproblems), self.is_record_updated]

    def putSubproblems(self, newSubproblems):
        try:
            self.subproblems.extend(newSubproblems)
        except Exception:
            print(Exception)
            return -1
        else:
            time = len(newSubproblems) * self.prc_put
            return time

    def putRecord(self, newRecord):
        self.records = newRecord

    # функция выдающая с вероятностью р '1' и 1-р '0'
    # вероятность р = (текущая глубина дерева) / (макс глубину дерева)
    def generateContinueOrNot(self, subProblem):
        p = (float(subProblem.depth) / float(self.max_depth)) ** 5.6
        return random.choices([0, 1], weights=[p, 1 - p])[0]

    # непосредственное ветвление одной вершины
    def ramify(self):
        curSubProblem = self.subproblems.pop(0)
        if self.generateContinueOrNot(curSubProblem) == 1:
            self.subproblems.append(subprob.SimpleSubProblem(depth=curSubProblem.depth + 1, weight=0, cost=0))
            self.subproblems.append(subprob.SimpleSubProblem(depth=curSubProblem.depth + 1, weight=0, cost=0))
            if curSubProblem.depth + 1 in self.testDict.keys():
                self.testDict[curSubProblem.depth + 1] += 2
            else:
                self.testDict[curSubProblem.depth + 1] = 2

    # ветвление на эн итераций
    def solve(self, n):
        time = 0.0
        if n > 0:
            i = 0
            while i < n and len(self.subproblems) != 0:
                i += 1
                self.ramify()
            self.records = i
            time = i * self.prc_slv
            self.is_record_updated = True
            return "solved", n, time
        elif n == -1:
            self.is_record_updated = True
            cnt = 0
            while len(self.subproblems) != 0:
                self.records += 1
                cnt += 1
                self.ramify()
                time += self.prc_slv
            return "solved", cnt, time
