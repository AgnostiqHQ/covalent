# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import site
import sys

from setuptools import Command, find_packages, setup
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info, manifest_maker

site.ENABLE_USER_SITE = "--user" in sys.argv[1:]

with open("VERSION") as f:
    version = f.read().strip()


requirements_file = "requirements.txt"
exclude_modules = [
    "tests",
    "tests.*",
]
sdk_only = os.environ.get("COVALENT_SDK_ONLY") == "1"
if sdk_only:
    requirements_file = "requirements-client.txt"
    exclude_modules += [
        "covalent_dispatcher",
        "covalent_dispatcher.*",
        "covalent_ui",
        "covalent_ui.*",
        "covalent_migrations",
    ]
    entry_points = {}
else:
    entry_points = {
        "console_scripts": [
            "covalent = covalent_dispatcher._cli.cli:cli",
        ],
    }

with open(requirements_file) as f:
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
        filepaths.extend(os.path.join(path, filename).split("/", 1)[1] for filename in filenames)

    return filepaths


def blacklist_packages():
    """Validate blacklisted packages are not installed."""

    import site
    from importlib import metadata

    if "READTHEDOCS" in os.environ:
        return

    installed_packages = [
        d.metadata["Name"] for d in metadata.distributions(path=site.getsitepackages())
    ]

    blacklist = ["cova"]

    for package in blacklist:
        if package in installed_packages:
            print("\n***************************", file=sys.stderr)
            print(
                f"Package conflict: uninstall package {package} to proceed with installation.",
                file=sys.stderr,
            )
            print("***************************\n", file=sys.stderr)
            sys.exit(1)


class BuildCovalent(build_py):
    def run(self):
        blacklist_packages()
        build_py.run(self)


class DevelopCovalent(develop):
    def run(self):
        blacklist_packages()
        develop.run(self)


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


class EggInfoCovalent(egg_info):
    def find_sources(self):
        manifest_filename = os.path.join(self.egg_info, "SOURCES.txt")
        mm = manifest_maker(self.distribution)
        mm.manifest = manifest_filename

        if os.path.exists("MANIFEST.in") and sdk_only:
            with open("MANIFEST.in", "r") as f:
                lines = f.readlines()
            with open("MANIFEST_SDK.in", "w") as f:
                for line in lines:
                    if not any(excluded in line for excluded in exclude_modules):
                        f.write(line)

            mm.template = "MANIFEST_SDK.in"

        mm.run()
        self.filelist = mm.filelist

        try:
            os.remove("MANIFEST_SDK.in")
        except OSError:
            pass


setup_info = {
    "name": "covalent",
    "packages": find_packages(exclude=exclude_modules),
    "version": version,
    "maintainer": "Agnostiq",
    "url": "https://github.com/AgnostiqHQ/covalent",
    "download_url": f"https://github.com/AgnostiqHQ/covalent/archive/v{version}.tar.gz",
    "license": "Apache License 2.0",
    "author": "Agnostiq",
    "author_email": "support@agnostiq.ai",
    "description": "Covalent Workflow Tool",
    "long_description": open("README.md").read(),
    "long_description_content_type": "text/markdown",
    "include_package_data": True,
    "zip_safe": False,
    "install_requires": required,
    "extras_require": {
        "aws": ["boto3>=1.20.48"],
        "azure": ["azure-identity>=1.13.0", "azure-storage-blob>=12.16.0"],
        "braket": ["amazon-braket-pennylane-plugin>=1.17.4", "boto3>=1.28.5"],
        "qiskit": [
            "pennylane-qiskit==0.30",
            "qiskit==0.43.1",
            "qiskit-ibm-provider==0.6.1",
            "qiskit-ibm-runtime==0.10.0",
        ],
    },
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Adaptive Technologies",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
        "Topic :: Software Development",
        "Topic :: System :: Distributed Computing",
    ],
    "cmdclass": {
        "egg_info": EggInfoCovalent,
        "build_py": BuildCovalent,
        "develop": DevelopCovalent,
        "docs": Docs,
        "webapp": BuildUI,
    },
    "entry_points": entry_points,
}

if __name__ == "__main__":
    setup(**setup_info)
