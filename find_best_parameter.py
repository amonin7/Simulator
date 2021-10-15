from EngineSimple import Engine


def find_best_arg_range():
    for i in range(1, 150, 2):
        eng = Engine(proc_amount=10, max_depth=24, arg=i)
        eng.run()
        print(f'[*] step with arg={i} is done')


if __name__ == '__main__':
    find_best_arg_range()
