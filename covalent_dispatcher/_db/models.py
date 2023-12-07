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

"""
Models for the workflows db. Based on schema v9
"""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import declarative_base

from covalent._shared_files.util_classes import RESULT_STATUS

Base = declarative_base()


class Lattice(Base):
    __tablename__ = "lattices"
    __table_args__ = (UniqueConstraint("dispatch_id", name="u_dispatch_id"),)

    id = Column(Integer, primary_key=True)
    dispatch_id = Column(String(64), nullable=False)

    # id of node if the lattice is actually a sublattice
    electron_id = Column(Integer)

    # name of the lattice function
    name = Column(Text, nullable=False)

    # name of the file containing the lattice function's docstring
    docstring_filename = Column(Text)

    # Workflow status
    status = Column(String(24), nullable=False)

    # Number of nodes in the lattice
    electron_num = Column(Integer, nullable=False)

    # Number of completed nodes in the lattice
    completed_electron_num = Column(Integer, nullable=False)

    # Storage backend type for data files ("local", "s3")
    storage_type = Column(Text)

    # Bucket name (dispatch_id)
    storage_path = Column(Text)

    # Name of the file containing the serialized function
    function_filename = Column(Text)

    # Name of the file containing the function string
    function_string_filename = Column(Text)

    # Short name describing the executor ("local", "dask", etc)
    executor = Column(Text)

    # JSONified executor attributes
    executor_data = Column(Text)

    # Short name describing the workflow executor ("local", "dask", etc)
    workflow_executor = Column(Text)

    # JSONified executor attributes
    workflow_executor_data = Column(Text)

    # Name of the file containing an error message for the workflow
    error_filename = Column(Text)

    # Name of the file containing the serialized input data
    inputs_filename = Column(Text)

    # Name of the file containing the serialized named args
    named_args_filename = Column(Text)

    # Name of the file containing the serialized named kwargs
    named_kwargs_filename = Column(Text)

    # name of the file containing the serialized output
    results_filename = Column(Text)

    # Name of the file containing the default electron dependencies
    deps_filename = Column(Text)

    # Name of the file containing the default list of callables before electrons are executed
    call_before_filename = Column(Text)

    # Name of the file containing the default list of callables after electrons are executed
    call_after_filename = Column(Text)

    # Name of the file containing the set of cova imports
    cova_imports_filename = Column(Text)

    # Name of the file containing the set of lattice imports
    lattice_imports_filename = Column(Text)

    # Results directory (will be deprecated soon)
    results_dir = Column(Text)

    # Dispatch id of the root lattice in a hierarchy of sublattices
    root_dispatch_id = Column(String(64), nullable=True)

    # Name of the column which signifies soft deletion of a lattice
    is_active = Column(Boolean, nullable=False, default=True)

    # Python version
    python_version = Column(Text)

    # Covalent SDK version
    covalent_version = Column(Text)

    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, onupdate=func.now(), server_default=func.now())
    started_at = Column(DateTime)
    completed_at = Column(DateTime)


class Electron(Base):
    __tablename__ = "electrons"
    __table_args__ = (Index("latid_nodeid_idx", "parent_lattice_id", "transport_graph_node_id"),)
    id = Column(Integer, primary_key=True)

    # id of the lattice containing this electron
    parent_lattice_id = Column(Integer, ForeignKey("lattices.id"), nullable=False)

    # id of the node in the context of a transport graph
    transport_graph_node_id = Column(Integer, nullable=False)

    # id of the node's task group in the context of a transport graph
    task_group_id = Column(Integer, nullable=False)

    # Node type
    type = Column(String(24), nullable=False)

    # Node name
    name = Column(Text, nullable=False)

    # Execution status of the node
    status = Column(String(24), nullable=False)

    # Storage backend type for data files ("local", "s3")
    storage_type = Column(Text)

    # Bucket name (dispatch_id)
    storage_path = Column(Text)

    # Name of the file containing the serialized function
    function_filename = Column(Text)

    # Name of the file containing the function string
    function_string_filename = Column(Text)

    # Short name describing the executor ("local", "dask", etc)
    executor = Column(Text)

    # JSONified executor attributes
    executor_data = Column(Text)

    # name of the file containing the serialized output
    results_filename = Column(Text)

    # Name of the file containing the serialized parameter (for parameter nodes)
    value_filename = Column(Text)

    # Name of the file containing standard output generated by the task
    stdout_filename = Column(Text)

    # Name of the file containing the electron execution dependencies
    deps_filename = Column(Text)

    # Name of the file containing the functions that are called before electron execution
    call_before_filename = Column(Text)

    # Name of the file containing the functions that are called before electron execution
    call_after_filename = Column(Text)

    # Whether qelectron data exists or not
    qelectron_data_exists = Column(Boolean, nullable=False, default=False)

    # Name of the file containing standard error generated by the task
    stderr_filename = Column(Text)

    # Name of the file containing errors generated by the task runner or executor
    error_filename = Column(Text)

    # Name of the column which signifies soft deletion of the electrons corresponding to a lattice
    is_active = Column(Boolean, nullable=False, default=True)

    # Foreign key reference to Jobs table
    job_id = Column(Integer, ForeignKey("jobs.id", name="job_id_link"), nullable=False)

    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, onupdate=func.now(), server_default=func.now())
    started_at = Column(DateTime)
    completed_at = Column(DateTime)


class ElectronDependency(Base):
    __tablename__ = "electron_dependency"
    id = Column(Integer, primary_key=True)
    __table_args__ = (Index("cnode_idx", "electron_id"), Index("pnode_idx", "parent_electron_id"))
    # Unique ID of electron
    electron_id = Column(
        Integer, ForeignKey("electrons.id", name="child_electron_link"), nullable=False
    )

    # Unique ID of the electron's parent
    parent_electron_id = Column(
        Integer, ForeignKey("electrons.id", name="parent_electron_link"), nullable=False
    )

    edge_name = Column(Text, nullable=False)

    # arg, kwarg, null
    parameter_type = Column(String(24), nullable=True)

    # Argument position - this value is null unless parameter_type is arg
    arg_index = Column(Integer, nullable=True)

    # Name of the column which signifies soft deletion of the electron dependencies corresponding to a lattice
    is_active = Column(Boolean, nullable=False, default=True)

    updated_at = Column(DateTime, nullable=True, onupdate=func.now(), server_default=func.now())
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)

    # Indicates whether the job has been requested to be cancelled
    cancel_requested = Column(Boolean, nullable=False, default=False)

    # Job state -- to be filtered/interpreted by each plugin
    status = Column(String(24), nullable=False, default=str(RESULT_STATUS.NEW_OBJECT))

    # JSON-serialized identifier for job
    job_handle = Column(Text, nullable=False, default="null")


# Core Lattice assets
class LatticeAsset(Base):
    __tablename__ = "lattice_assets"
    __table_args__ = (Index("lattice_assets_idx", "meta_id", "key"),)

    id = Column(Integer, primary_key=True)

    # Lattice record id
    meta_id = Column(Integer, ForeignKey("lattices.id", name="lattice_link"), nullable=False)

    # Asset record id
    asset_id = Column(Integer, ForeignKey("assets.id", name="asset_link"), nullable=False)

    # Asset key
    key = Column(String(24), nullable=False)


# Core Electron assets
class ElectronAsset(Base):
    __tablename__ = "electron_assets"
    __table_args__ = (Index("electron_assets_idx", "meta_id", "key"),)
    id = Column(Integer, primary_key=True)

    # Electron record id
    meta_id = Column(Integer, ForeignKey("electrons.id", name="electron_link"), nullable=False)

    # Asset record id
    asset_id = Column(Integer, ForeignKey("assets.id", name="asset_link"), nullable=False)

    # Asset key
    key = Column(String(24), nullable=False)


class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True)

    # Storage backend type for data files ("local", "s3")
    storage_type = Column(Text, nullable=False)

    # Bucket name
    storage_path = Column(Text, nullable=False)

    # Object key
    object_key = Column(Text, nullable=False)

    # Digest algorithm ("md5", "sha1")
    digest_alg = Column(Text, nullable=True)

    # Hex repr of digest
    digest = Column(Text, nullable=True)

    # Remote location of asset
    remote_uri = Column(Text, nullable=True)

    # Size in bytes
    size = Column(Integer, nullable=True)
