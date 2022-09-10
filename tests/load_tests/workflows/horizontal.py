import covalent as ct


@ct.electron
def add(x, y):
    return x + y


def horizontal_workflow(N: int):
    for _ in range(N):
        r1 = add(2, 3)
    return r1
