import sys
from copy import deepcopy
from ctypes import CDLL, POINTER, byref, c_int32, pointer
from functools import wraps
from typing import Any, Callable, List, Optional

import covalent as ct
from covalent._shared_files.logger import app_log
from covalent._workflow.electron import Electron

# Current status
# The lepton function runs outside a workflow
# but experiences some errors inside an active lattice


class Lepton(Electron):
    INPUT = 0
    OUTPUT = 1
    INPUT_OUTPUT = 2

    def __init__(
        self,
        language: str = "python",
        library_name: str = "",
        function_name: str = "",
        argtypes: List = [],
    ) -> None:
        self.language = language
        self.library_name = library_name
        self.function_name = function_name
        self.argtypes = argtypes

        super().__init__(self.wrap_function())

    def wrap_function(self) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            if kwargs and self.language not in ["Python", "python"]:
                app_log.critical(
                    f"Keyword arguments are not supported when calling {self.function}."
                )
                sys.exit(3)

            if self.language in ["C", "c", "C++", "c++"]:
                from ctypes import CDLL, pointer

                try:
                    handle = CDLL(self.library_name)
                except OSError:
                    app_log.warning(f"Could not open {self.library_name}.")
                    sys.exit(1)

                entrypoint = self.function_name
                types = [t[0] for t in self.argtypes]
                attrs = [t[1] for t in self.argtypes]
                handle[entrypoint].argtypes = types
                handle[entrypoint].restype = None

                c_func_args = []
                for idx, (t, arg) in enumerate(zip(types, args)):
                    # 1. The user specifies a scalar (non-subscriptable)
                    #    and this variable returns data
                    if (
                        attrs[idx] != self.INPUT
                        and not hasattr(arg, "__getitem__")
                        and types[idx].__name__.startswith("LP_")
                    ):
                        c_func_args.append(pointer(types[idx]._type_(arg)))
                    # 2. The user specifies an array (subscriptable)
                    elif hasattr(arg, "__getitem__") and types[idx].__name__.startswith("LP_"):
                        c_func_args.append((types[idx]._type_ * len(arg))(*arg))
                    # 3. Data passed by value
                    elif attrs[idx] == self.INPUT:
                        c_func_args.append(types[idx]._type_(arg))
                    # An invalid type was used
                    else:
                        app_log.error("An invalid type was specified!")
                        sys.exit(4)

                handle[entrypoint](*c_func_args)

                return_vals = []
                for idx, arg in enumerate(c_func_args):
                    if attrs[idx] == self.INPUT:
                        continue

                    # Check for pointers to scalars
                    if hasattr(arg, "contents"):
                        return_vals.append(arg.contents.value)
                    # This is a list or array
                    elif hasattr(arg, "__getitem__"):
                        return_vals.append([x.value for x in arg])
                    else:
                        app_log.error("Unexpected error.")
                        sys.exit(5)
            elif self.language in ["Python", "python"]:
                import importlib

                try:
                    module = importlib.import_module(self.library_name)
                except ModuleNotFoundError:
                    app_log.warning(f"Could not import the module '{self.library_name}'.")
                    return

                try:
                    func = getattr(module, self.function_name)
                except AttributeError:
                    app_log.warning(
                        f"Could not find the function '{self.function_name}' in '{self.library_name}'."
                    )
                    return

                return func(*args, **kwargs)
            else:
                app_log.warning("Language not supported!")
                sys.exit(2)

            if not return_vals:
                return None
            elif len(return_vals) == 1:
                return return_vals[0]
            else:
                return tuple(return_vals)

        return wrapper


###########
# This is the desired new UX
###########

lep = Lepton(
    "C",
    "libtest.so",
    "test_entry",
    [(POINTER(c_int32), Lepton.INPUT_OUTPUT)],
)

lep2 = Lepton("python", "test2", "test_entry2")

###########
# Below is what we want to abstract
###########


@ct.electron
def test_entry_py(x):
    library_name = "libtest.so"
    function_name = "test_entry"

    try:
        handle = CDLL(library_name)
    except OSError:
        app_log.critical(f"Could not open {library_name}!")
        sys.exit(1)

    handle[function_name].argtypes = [POINTER(c_int32)]
    # Always return None
    handle[function_name].restype = None

    f_x = pointer(c_int32(x))

    # This is the call to the C function
    handle[function_name](
        f_x,
    )

    return f_x.contents.value


@ct.lattice
def test_workflow(x):
    # return test_entry_py(x)
    return lep(x)


if __name__ == "__main__":
    # dispatch_id = ct.dispatch(test_workflow)(1)
    # result = ct.get_result(dispatch_id, wait=True).result
    # print(result)

    # print(lep(1))
    print(lep2(1, y=2))
