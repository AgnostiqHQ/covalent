# Copyright 2021-2022 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the GNU Affero General Public License 3.0 (the "License").
# A copy of the License may be obtained with this software package or at
#
#      https://www.gnu.org/licenses/agpl-3.0.en.html
#
# Use of this file is prohibited except in compliance with the License. Any
# modifications or derivative works of this file must retain this copyright
# notice, and modified files must contain a notice indicating that they have
# been altered from the originals.
#
# Covalent is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
#
# Relief from the License may be granted by purchasing a commercial license.

"""
sphinx-execute-code module for execute_code directive
To use this module, add: extensions.append('sphinx_execute_code')

Available options:

        'linenos': directives.flag,
        'output_language': directives.unchanged,
        'hide_code': directives.flag,
        'hide_headers': directives.flag,
        'filename': directives.path,
        'hide_filename': directives.flag,

Usage:

.. example_code:
   :linenos:
   :hide_code:

   print 'Execute this python code'
"""

import os
import sys
from io import StringIO

from docutils import nodes
from docutils.parsers.rst import Directive, directives

# execute_code function thanks to Stackoverflow code post from hekevintran
# https://stackoverflow.com/questions/701802/how-do-i-execute-a-string-containing-python-code-in-python

__author__ = "jp.senior@gmail.com"
__docformat__ = "restructuredtext"
__version__ = "0.2a2"


class ExecuteCode(Directive):
    """Sphinx class for execute_code directive"""

    has_content = True
    required_arguments = 0
    optional_arguments = 5

    option_spec = {
        "linenos": directives.flag,
        "output_language": directives.unchanged,  # Runs specified pygments lexer on output data
        "hide_code": directives.flag,
        "hide_headers": directives.flag,
        "filename": directives.path,
        "hide_filename": directives.flag,
    }

    @classmethod
    def execute_code(cls, code):
        """Executes supplied code as pure python and returns a list of stdout, stderr

        Args:
            code (string): Python code to execute

        Results:
            (list): stdout, stderr of executed python code

        Raises:
            ExecutionError when supplied python is incorrect

        Examples:
            >>> execute_code('print "foobar"')
            'foobar'
        """

        output = StringIO()
        err = StringIO()

        sys.stdout = output
        sys.stderr = err

        try:
            exec(code)
        # If the code is invalid, just skip the block - any actual code errors
        # will be raised properly
        except TypeError:
            pass
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        results = list()
        results.append(output.getvalue())
        results.append(err.getvalue())
        results = "".join(results)

        return results

    def run(self):
        """Executes python code for an RST document, taking input from content or from a filename

        :return:
        """
        language = self.options.get("language") or "python"
        output_language = self.options.get("output_language") or "none"
        filename = self.options.get("filename")
        code = ""

        if not filename:
            code = "\n".join(self.content)
        if filename:
            try:
                with open(filename, "r") as code_file:
                    code = code_file.read()
                    self.warning("code is %s" % code)
            except (IOError, OSError) as err:
                # Raise warning instead of a code block
                error = "Error opening file: %s, working folder: %s" % (err, os.getcwd())
                self.warning(error)
                return [nodes.warning(error, error)]

        output = []

        # Show the example code
        if "hide_code" not in self.options:
            input_code = nodes.literal_block(code, code)

            input_code["language"] = language
            input_code["linenos"] = "linenos" in self.options
            if "hide_headers" not in self.options:
                suffix = ""
                if "hide_filename" not in self.options:
                    suffix = "" if filename is None else str(filename)
                output.append(nodes.caption(text="Example %s" % suffix))
            output.append(input_code)

        # Show the code results
        if "hide_headers" not in self.options:
            output.append(nodes.caption(text="Results"))
        code_results = self.execute_code(code)
        code_results = nodes.literal_block(code_results, code_results)

        code_results["linenos"] = "linenos" in self.options
        code_results["language"] = output_language
        output.append(code_results)
        return output


def setup(app):
    """Register sphinx_execute_code directive with Sphinx"""
    app.add_directive("execute_code", ExecuteCode)
    return {"version": __version__}
