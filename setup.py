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
import platform
import shutil
import site
import sys

from setuptools import Command, find_packages, setup
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop

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

    @staticmethod
    def _run(command, stdout=None, cwd=None, check=False, capture_output=False):
        import subprocess

        proc = subprocess.run(
            command, stdout=stdout, cwd=cwd, check=check, capture_output=capture_output
        )
        if proc.returncode != 0:
            raise Exception(proc.stderr.decode("utf-8").strip())
        return proc

    @staticmethod
    def _node_versions():
        import requests

        r = requests.get("https://nodejs.org/download/release/index.json")
        return r.json()

    @staticmethod
    def _latest_lts(node_versions):
        for version in node_versions:
            if version["lts"]:
                return version["version"]

    @staticmethod
    def _node_lts(node_versions):
        import subprocess

        proc = BuildUI._run(["node", "-v"], stdout=subprocess.PIPE)
        installed_version = proc.stdout.decode("utf-8")[:-1]
        print(f"The installed Node.js version is {installed_version}.")
        for version in node_versions:
            if version["version"] == installed_version:
                return version["lts"]

    def initialize_options(self):
        self.clean = False

    def finalize_options(self):
        pass

    def run(self):
        node_versions = self._node_versions()
        if self.clean:
            import shutil

            shutil.rmtree("covalent_ui/webapp/build", ignore_errors=True)
        elif self._node_lts(node_versions):
            import subprocess

            self._run(
                ["yarn", "install"], cwd="covalent_ui/webapp", check=True, capture_output=True
            )
            self._run(["yarn", "build"], cwd="covalent_ui/webapp", check=True, capture_output=True)
        else:
            lts = self._latest_lts(node_versions)[1:]
            print(
                "The installed Node.js version is incompatible with the yarn build.\n",
                "You must use a Node.js LTS version to install the Covalent webapp. ",
                f"The latest LTS version is {lts}.\n",
                "See https://stackoverflow.com/a/69778087/5513030 for more information ",
                f"or simply run `nvm use {lts}`.",
            )


def purge_config():
    import os

    # remove legacy config
    try:
        os.remove(".env")
    except OSError:
        pass
    try:
        os.remove("supervisord.conf")
    except OSError:
        pass

    # remove latest config
    HOME_PATH = os.environ.get("XDG_CACHE_HOME") or (os.environ["HOME"] + "/.cache")
    COVALENT_CACHE_DIR = os.path.join(HOME_PATH, "covalent")
    shutil.rmtree(COVALENT_CACHE_DIR, ignore_errors=True)


def install_nats():
    import subprocess

    nats_version = "2.7.4"
    nats_download_prefix = (
        f"https://github.com/nats-io/nats-server/releases/download/v{nats_version}/"
    )
    nats_dist_mapping = {
        "Linux": f"nats-server-v{nats_version}-linux-amd64.zip",
        "Darwin": f"nats-server-v{nats_version}-darwin-amd64.zip",
    }

    if platform.system() == "Darwin" or platform.system() == "Linux":
        import requests

        nats_dist = nats_dist_mapping[platform.system()]
        r = requests.get(
            nats_download_prefix + nats_dist,
            allow_redirects=True,
        )
        r.raise_for_status()

        open(nats_dist, "wb").write(r.content)
        subprocess.run(["unzip", nats_dist], check=True)
        shutil.move(nats_dist[:-4] + "/nats-server", "covalent_queuer/nats-server")

        shutil.rmtree(nats_dist[:-4])
        os.remove(nats_dist)
    else:
        print(
            "Platform is not natively supported. Please manually install nats-server.",
            file=sys.stderr,
        )
        sys.exit(1)


class BuildCovalent(build_py):
    """Build Covalent with NATS server"""

    def run(self):
        purge_config()
        install_nats()
        build_py.run(self)


class DevelopCovalent(develop):
    """Post-Installation for Covalent in develop mode with NATS server"""

    def run(self):
        purge_config()
        install_nats()
        develop.run(self)


setup_info = {
    "name": "cova",
    "packages": find_packages(exclude=["*tests*", "*_legacy"]),
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
        "covalent": [
            "executor/executor_plugins/local.py",
            "notify/notification_plugins/webhook.py",
        ],
        "covalent_ui": recursively_append_files("covalent_ui/webapp/build"),
        "covalent_queuer": ["nats-server"],
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
        "Programming Language :: Python :: 3.9",
        "Topic :: Adaptive Technologies",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
        "Topic :: Software Development",
        "Topic :: System :: Distributed Computing",
    ],
    "cmdclass": {
        "build_py": BuildCovalent,
        "develop": DevelopCovalent,
        "docs": Docs,
        "webapp": BuildUI,
    },
    "entry_points": {
        "console_scripts": [
            "covalent = covalent._cli.cli:cli",
            "nats-server = covalent_queuer.nats_server:main",
        ],
    },
}

if __name__ == "__main__":
    if os.getenv("COVA_SDK"):
        setup_info["packages"] = find_packages(exclude=["*tests*", "*_legacy", "covalent_*"])
    setup(**setup_info)
