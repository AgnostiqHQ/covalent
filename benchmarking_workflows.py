import covalent as ct

SMALL_UNIDIRECTIONAL_N = 5
SMALL_HAGRID_N = 3

LARGE_UNIDIRECTIONAL_N = 25
LARGE_HAGRID_N = 10


@ct.electron
def identity(x):
    return x


@ct.electron
def combine(x):
    return sum(x)


@ct.electron
def strategy_func(func, a):
    return func(a)


@ct.lattice
def workflow(n, parallel=False, serial=False):
    vals = []
    result = 1
    nodes = range(n)

    if parallel and not serial:
        for _ in nodes:
            vals.append(identity(1))
        vals = combine(vals)

    elif serial and not parallel:
        for _ in nodes:
            result = identity(result)

    elif serial and parallel:
        for i in nodes:
            for _ in nodes:
                if i == 0:
                    vals.append(identity(1))
                else:
                    vals.append(identity(result))
            result = combine(vals)

    return result, vals


dispatcher = ct.dispatch(workflow)

small_horizontal_id = dispatcher(n=SMALL_UNIDIRECTIONAL_N, parallel=True)
small_vertical_id = dispatcher(n=SMALL_UNIDIRECTIONAL_N, serial=True)
small_hagrid_id = dispatcher(n=SMALL_HAGRID_N, serial=True, parallel=True)

large_horizontal_id = dispatcher(n=LARGE_UNIDIRECTIONAL_N, parallel=True)
large_vertical_id = dispatcher(n=LARGE_UNIDIRECTIONAL_N, serial=True)
large_hagrid_id = dispatcher(n=LARGE_HAGRID_N, serial=True, parallel=True)
