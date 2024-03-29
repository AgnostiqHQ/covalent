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

from abc import ABC, abstractmethod
from typing import Tuple

from .transport import TransportableObject


class Deps(ABC):
    """Generic dependency class used in specifying any kind of dependency for an electron.

    Attributes:
        apply_fn: function to be executed in the backend environment
        apply_args: list of arguments to be applied in the backend environment
        apply_kwargs: dictionary of keyword arguments to be applied in the backend environment

    """

    def __init__(self, apply_fn=None, apply_args=[], apply_kwargs={}, *, retval_keyword=""):
        self.apply_fn = TransportableObject(apply_fn)
        self.apply_args = TransportableObject(apply_args)
        self.apply_kwargs = TransportableObject(apply_kwargs)
        self.retval_keyword = retval_keyword

    def apply(self) -> Tuple[TransportableObject, TransportableObject, TransportableObject, str]:
        """
        Encapsulates the exact function and args/kwargs to be executed in the backend environment.

        Args:
            None

        Returns:
            A tuple of transportable objects containing the function and optional args/kwargs
        """
        return (self.apply_fn, self.apply_args, self.apply_kwargs, self.retval_keyword)

    def short_name(self):
        return self.__module__.split("/")[-1].split(".")[-1]

    @abstractmethod
    def to_dict(self):
        raise NotImplementedError

    @abstractmethod
    def from_dict(self, object_dict):
        raise NotImplementedError
