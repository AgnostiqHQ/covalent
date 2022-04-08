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

from app.core.miniostoragebackend import MinioStorageBackend

DIRNAME = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
BUCKET = "_test_assets"
OBJECT = "result"
FILENAME = os.path.join(DIRNAME, BUCKET, OBJECT)


def file_reader(path):
    with open(path, "rb") as f:
        yield from f


class MockResponse:
    status = 200

    def __init__(self, path):
        self.path = path

    def stream(self):
        return file_reader(self.path)


class MockMinioClient:
    def get_object(self, bucket_name, object_name):
        return MockResponse(FILENAME)

    def put_object(self, bucket_name, object_name, data, length):
        return MockResponse(FILENAME)

    def stat_object(self, bucket_name, object_name):
        return MockResponse(FILENAME)


class TestMinioStorageBackend:
    def test_get(self):
        backend = MinioStorageBackend(MockMinioClient())
        result = backend.get(BUCKET, OBJECT)
        assert len(next(result, None)) > 0

    def test_put(self):
        backend = MinioStorageBackend(MockMinioClient())
        with open(FILENAME, "rb") as f:
            f.seek(0, 2)
            length = f.tell()
            f.seek(0)
            path, filename = backend.put(f, BUCKET, OBJECT, length)
            assert os.path.exists(os.path.join(DIRNAME, path, filename))
