import covalent as ct

@ct.electron
def add(x: int, y: int) -> int:
    return x + y

@ct.electron
def multiply(x: int, y: int) -> int:
    return x*y

@ct.lattice
def workflow(x: int, y: int) -> int:
    r1 = add(x, y)
    r2 = multiply(r1, y)
    return r1 + r2

if __name__ == "__main__":
    result = ct.dispatch_sync(workflow)(2, 3).result
    assert result == 20