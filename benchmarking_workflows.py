import covalent as ct

UNIDIRECTIONAL_N = 100
HAGRID_N = 9


@ct.electron
def identity(x):
    return x


@ct.electron
def combine(x):
    return sum(x)


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

# horizontal_id = dispatcher(n=UNIDIRECTIONAL_N, parallel=True)
# print(f"Horizontal [n={UNIDIRECTIONAL_N}] Dispatch ID: {horizontal_id}")

# vertical_id = dispatcher(n=UNIDIRECTIONAL_N, serial=True)
# print(f"Vertical [n={UNIDIRECTIONAL_N}] Dispatch ID: {vertical_id}")

hagrid_id = dispatcher(n=HAGRID_N, serial=True, parallel=True)
print(f"Hagrid [n={HAGRID_N}] Dispatch ID: {hagrid_id}")
