import covalent as ct


@ct.electron
def test_func(x, *args, y=5, **kwargs):
    return x


@ct.lattice
def workflow(x, y):
    return test_func(x, 7, y=y, z=8)


if __name__ == "__main__":
    result = ct.dispatch_sync(workflow)(1, 1)
    print(result.result)
