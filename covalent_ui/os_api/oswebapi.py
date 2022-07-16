#!/usr/bin/python3

# Copyright 2021 Agnostiq Inc.
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
"""script manager"""

import os
import sys


def arg_fetch():
    try:
        args_passed = sys.argv[1]
        process(args_passed)
    except Exception as e:
        print("pass atleast one command [start, stop, restart]")
        return e


def process(args_passed):
    print(args_passed)
    try:
        if args_passed == "start":
            os.system("supervisord")
            os.system("supervisorctl start all")
            print("started sucessfully")
        elif args_passed == "stop":
            os.system("supervisorctl stop all")
            print("stoped sucessfully")
        elif args_passed == "restart":
            os.system("supervisorctl restart all")
            print("restarted sucessfully")
        else:
            print("Allowed commands are [start, stop, restart]")
    except:
        print("Something went wrong, see /logs folder for logs")


arg_fetch()
