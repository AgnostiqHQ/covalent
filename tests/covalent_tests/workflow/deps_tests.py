import covalent as ct


def test_bash_deps_apply():
    cmds = ["pip list", "yum install gcc"]
    deps = ct.BashDeps(cmds)
    assert deps.apply() == cmds
