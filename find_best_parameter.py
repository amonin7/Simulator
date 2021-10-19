from EngineSecond import Engine


def find_best_arg_range():
    # for proc_am in range(15, 26, 5):
    #     add = (proc_am // 5 - 2) * 2
    #     items = 24 + add
    proc_am = 15
    items = 26
    for i in range(5, 99, 3):
        eng = Engine(proc_amount=proc_am, max_depth=items, arg=i)
        eng.run()
        print(f'[*] step with arg={i} is done')
    # for i in range(200, 1001, 100):
    #     eng = Engine(proc_amount=proc_am, max_depth=items, arg=i)
    #     eng.run()
    #     print(f'[*] step with arg={i} is done')
    # for i in range(1200, 2001, 200):
    #     eng = Engine(proc_amount=10, max_depth=24, arg=i)
    #     eng.run()
    #     print(f'[*] step with arg={i} is done')


if __name__ == '__main__':
    find_best_arg_range()
