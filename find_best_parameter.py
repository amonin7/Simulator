from EngineSecond import Engine


def find_best_arg_range():
    proc_am = 8
    items = 26

    for i in range(100, 179, 3):
        eng = Engine(proc_amount=proc_am, max_depth=items, arg=i)
        eng.run()
        print(f'[*] step with arg={i} is done')


if __name__ == '__main__':
    find_best_arg_range()
