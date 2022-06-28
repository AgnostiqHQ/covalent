from __future__ import annotations

import signal
import asyncio
import os
from logging import Logger
from threading import Thread
from multiprocessing import Process, current_process

import dask.config
from dask.distributed import Client, LocalCluster
from distributed.core import Server, rpc

from covalent._shared_files import logger
from covalent._shared_files.config import set_config, get_config, update_config
from covalent._shared_files.utils import get_random_available_port

app_log = logger.app_log

# Configure dask to not allow daemon workers
dask.config.set({"distributed.worker.daemon": False})


class DaskCluster(Process):
    """
    Start a local Dask cluster in a separate multiprocessing process whose
    lifetime is tied to Covalent. The cluster also starts and
    admin/monitoring server along with it so that the cluster can be
    administered and dynamically altered after covalent has started. By
    default the admin server listens for TCP connections at
    tcp://127.0.0.1:8000
    """
    def __init__(self, name: str, logger: Logger):
        super(DaskCluster, self).__init__()
        self.name = name
        self.logger = logger
        self.cluster = None

        # Admin handler server connection args
        self.admin_host = "127.0.0.1"
        self.admin_port = get_random_available_port()

        self._listen_address = f"tcp://{self.admin_host}:{self.admin_port}"

        # Cluster configuration
        self.num_workers = None
        self.mem_per_worker = None
        self.threads_per_worker = None

        self.loop = asyncio.get_event_loop()

        # Read the configuration options from the main config file
        try:
            self.num_workers = get_config("dask.num_workers")
        except KeyError:
            self.logger.warning("Num workers not specified, using default = 1")

        try:
            self.mem_per_worker = get_config("dask.mem_per_worker")
        except KeyError:
            self.logger.warning("Memory limit per worker not provided, using default = 'auto'")

        try:
            self.threads_per_worker = get_config("dask.threads_per_worker")
        except KeyError:
            self.logger.warning("Threads per worker not provided, using default = 1")

        # Register handlers
        self.handlers = {'cluster_size': self.__len__,
                         'cluster_info': self._get_cluster_info,
                         'cluster_status': self._get_cluster_status,
                         'cluster_address': self._get_cluster_addresses,
                         'cluster_restart': self._cluster_restart,
                         'cluster_scale': lambda comm, size: self.cluster.scale(int(size)),
                         'cluster_logs': self._get_cluster_logs}

        self.admin_server = Server(handlers=self.handlers)

    async def _get_cluster_logs(self):
        """
        Retrive cluster logs from the scheduler
        """
        cluster_logs = []
        async with rpc(self.cluster.scheduler_address) as r:
            cluster_logs.append(await r.get_logs())
            cluster_logs.append(await r.worker_logs())
        return cluster_logs

    async def _restart_worker(self, worker_id, worker_nanny_addr):
        async with rpc(worker_nanny_addr) as r:
            await r.restart()

        self.logger.warning(f"Worker-{worker_id} restarted")

    async def _cluster_restart(self):
        """
        Restart the workers using their respective nanny services
        """
        worker_service_addrs = {}
        async with rpc(self.cluster.scheduler_address) as r:
            cinfo = await r.identity()
            for _, worker_info in cinfo['workers'].items():
                worker_id = worker_info['id']
                worker_service_addrs[f"{worker_id}"] = worker_info['nanny']

        await asyncio.gather(*[self._restart_worker(worker_id, nanny_addr)
                               for worker_id, nanny_addr in worker_service_addrs.items()])

    async def _get_cluster_info(self):
        """
        Retrive cluster info from the scheduler
        """
        async with rpc(self.cluster.scheduler_address) as r:
            return await r.identity()

    async def _get_cluster_status(self):
        """
        Retrive status of the scheduler and all workers part of the cluster
        """
        proc_status = {}
        async with rpc(self.cluster.scheduler_address) as r:
            cinfo = await r.identity()

        if cinfo:
            proc_status['scheduler'] = 'running'

        for worker_addr, worker_info in cinfo['workers'].items():
            worker_id = worker_info['id']
            proc_status[f"worker-{worker_id}"] = worker_info['status']

        return proc_status

    async def _get_cluster_addresses(self):
        """
        Retrive the scheduler and worker addresses that are part of the cluster
        """
        addresses = {}
        async with rpc(self.cluster.scheduler_address) as r:
            cinfo = await r.identity()

        addresses["scheduler"] = cinfo["address"]
        addresses["workers"] = {}
        for addr, worker_info in cinfo["workers"].items():
            worker_id = worker_info["id"]
            addresses["workers"][f"{worker_id}"] = addr

        return addresses

    def __len__(self) -> int:
        """
        Return the number of active workers in the cluster
        """
        if self.cluster:
            return len(self.cluster.workers)
        return 0

    def run(self):
        """
        Runs a local dask cluster along with its monitoring thread
        """
        # listen for connections
        self.loop.create_task(self.admin_server.listen((self.admin_host,
                                                        self.admin_port)))
        try:
            self.cluster = LocalCluster(n_workers=self.num_workers,
                                        threads_per_worker=self.threads_per_worker,
                                        **{"memory_limit": self.mem_per_worker})
        except Exception as e:
            self.logger.exception(e)

        scheduler_address = self.cluster.scheduler_address
        dashboard_link = self.cluster.dashboard_link

        try:
            update_config(
                {
                    "dask": {
                        "scheduler_address": scheduler_address,
                        "dashboard_link": dashboard_link,
                        "process_info": current_process(),
                        "pid": os.getpid(),
                        "admin_host": self.admin_host,
                        "admin_port": self.admin_port
                    }
                }
            )
        except Exception as e:
            self.logger.exception(e)

        self.loop.run_forever()
