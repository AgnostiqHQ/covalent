import covalent as ct


def test_deps_bash_init():
    cmds = ["pip list", "yum install gcc"]
    deps = ct.DepsBash(cmds)
    assert deps.commands == cmds


def test_bash_deps_apply():
    cmds = ["pip list", "yum install gcc"]
    deps = ct.DepsBash(cmds)
    assert deps.apply() == cmds
