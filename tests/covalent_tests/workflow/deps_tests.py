import covalent as ct


def test_deps_bash_init():
    cmds = ["pip list", "yum install -y gcc"]
    cmd = "apt install -y build-essential"
    deps = ct.DepsBash(cmds)
    deps_from_str = ct.DepsBash(cmd)
    assert deps.commands == cmds
    assert deps_from_str.commands == [cmd]


def test_bash_deps_apply():
    cmds = ["pip list", "yum install gcc"]
    deps = ct.DepsBash(cmds)
    assert deps.apply() == cmds


def test_call_deps_init():
    from covalent._workflow.transport import TransportableObject

    def f(x):
        return x * x

    dep = ct.DepsCall(f, args=[5])
    g = dep.func.get_deserialized()
    args = dep.args.get_deserialized()
    assert args == [5]
    assert g(*args) == f(*args)


def test_call_deps_apply():
    from covalent._workflow.transport import TransportableObject

    def f(x):
        return x * x

    dep = ct.DepsCall(f, args=[5])
    g, args, kwargs = (t.get_deserialized() for t in dep.apply())
    assert args == [5]
    assert kwargs == {}
    assert g(*args) == f(*args)
