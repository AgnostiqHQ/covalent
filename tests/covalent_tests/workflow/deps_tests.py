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
