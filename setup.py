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

import os
import site
import sys

from setuptools import Command, find_packages, setup

site.ENABLE_USER_SITE = "--user" in sys.argv[1:]

with open("VERSION") as f:
    version = f.read().strip()

with open("requirements.txt") as f:
    required = f.read().splitlines()


def recursively_append_files(directory: str):
    """
    Append files recursively in a given directory

    Args:
        directory: Directory within which all the subdirs and files reside

    Returns:
        filepaths: List of all file paths found recursively in the directory
    """

    filepaths = []

    for path, _, filenames in os.walk(directory):
        for filename in filenames:
            filepaths.append(os.path.join(path, filename).split("/", 1)[1])

    return filepaths


class Docs(Command):
    """Generate HTML documentation"""

    description = "Generate HTML user documentation from code"

    user_options = [
        ("clean", "c", "clean directory"),
    ]

    def initialize_options(self):
        self.clean = False

    def finalize_options(self):
        pass

    def run(self):
        from doc import generate_docs

        generate_docs.run(self.clean)


class BuildUI(Command):
    """Build UI webapp"""

    description = "Build the front-end webapp from source"

    user_options = [
        ("clean", "c", "clean directory"),
    ]

    def initialize_options(self):
        self.clean = False

    def finalize_options(self):
        pass

    def run(self):
        if self.clean:
            import shutil

            shutil.rmtree("covalent_ui/webapp/build", ignore_errors=True)

        else:
            import subprocess

            subprocess.run(
                ["yarn", "install"], cwd="covalent_ui/webapp", check=True, capture_output=True
            )
            subprocess.run(
                ["yarn", "build"], cwd="covalent_ui/webapp", check=True, capture_output=True
            )


setup_info = {
    "name": "cova",
    "packages": find_packages(exclude=["tests"]),
    "version": version,
    "maintainer": "Agnostiq",
    "url": "https://github.com/AgnostiqHQ/covalent",
    "download_url": f"https://github.com/AgnostiqHQ/covalent/archive/v{version}.tar.gz",
    "license": "GNU Affero GPL v3.0",
    "author": "Agnostiq",
    "author_email": "support@agnostiq.ai",
    "description": "Covalent Workflow Tool",
    "long_description": open("README.md").read(),
    "long_description_content_type": "text/markdown",
    "include_package_data": True,
    "zip_safe": False,
    "package_data": {
        "covalent": ["executor/executor_plugins/local.py"],
        "covalent_dispatcher": ["_service/app.py"],
        "covalent_ui": recursively_append_files("covalent_ui/webapp/build"),
    },
    "install_requires": required,
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Topic :: Adaptive Technologies",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
        "Topic :: Software Development",
        "Topic :: System :: Distributed Computing",
    ],
    "cmdclass": {
        "docs": Docs,
        "webapp": BuildUI,
    },
    "entry_points": {
        "console_scripts": [
            "covalent = covalent_dispatcher._cli.cli:cli",
        ],
    },
}

if __name__ == "__main__":
    setup(**setup_info)
