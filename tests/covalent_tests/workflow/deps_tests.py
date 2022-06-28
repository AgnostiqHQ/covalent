import subprocess

import covalent as ct


def test_deps_bash_init():
    cmds = ["pip list", "yum install -y gcc"]
    cmd = "apt install -y build-essential"
    deps = ct.DepsBash(cmds)
    deps_from_str = ct.DepsBash(cmd)
    assert deps.commands == cmds
    assert deps_from_str.commands == [cmd]


def test_bash_deps_apply():
    import tempfile
    from pathlib import Path

    f = tempfile.NamedTemporaryFile(delete=True)
    tmp_path = f.name
    f.close()

    cmds = [f"touch {tmp_path}"]
    deps = ct.DepsBash(cmds)

    serialized_fn, serialized_args, serialized_kwargs = deps.apply()

    fn = serialized_fn.get_deserialized()
    args = serialized_args.get_deserialized()
    kwargs = serialized_kwargs.get_deserialized()
    assert args == [cmds]
    assert kwargs == {}

    fn(*args, **kwargs)

    assert Path(tmp_path).is_file()

    Path(tmp_path).unlink()


def test_call_deps_init():
    from covalent._workflow.transport import TransportableObject

    def f(x):
        return x * x

    dep = ct.DepsCall(f, args=[5])
    g = dep.apply_fn.get_deserialized()
    args = dep.apply_args.get_deserialized()
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
