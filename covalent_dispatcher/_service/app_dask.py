from __future__ import annotations
import dask.config
import asyncio
from logging import Logger
from dask.distributed import LocalCluster, Client
from multiprocessing import Process
from covalent._shared_files import logger
from covalent._shared_files.config import set_config
from distributed.core import Server

app_log = logger.app_log

# Configure dask to not allow daemon workers
dask.config.set({"distributed.worker.daemon": False})

class DaskCluster(Process):
    def __init__(self, logger: Logger, admin_host: str = '127.0.0.1',
                 admin_port: int = 8000):
        """
        Start a local Dask cluster in a separate multiprocessing process whose
        lifetime is tied to Covalent. The cluster also starts and
        admin/monitoring server along with it so that the cluster can be
        administered and dynamically altered after covalent has started. By
        default the admin server listens for TCP connections at
        tcp://127.0.0.1:8000
        """
        super(DaskCluster, self).__init__()
        self.logger = logger
        self.daemon = False
        self.cluster = None
        self.name = "DaskClusterProcess"
        self.admin_host = admin_host
        self.admin_port = admin_port

    async def admin_server(self):
        """
        Dask core server to administer the Dask cluster. The different handlers
        are added to the server either as python lambda functions or as instance
        methods
        """
        s = Server({'cluster_status': lambda comm: self.cluster.status,
                    'cluster_info': lambda comm: self.cluster.scheduler_info,
                    'cluster_restart': lambda comm: None,
                    'cluster_scale': lambda comm, nworkers:
                    self.cluster.scale(n=nworkers),
                    'cluster_adapt': lambda comm, min_workers, max_workers:
                    None,
                    'cluster_addresses': lambda comm: {'scheduler':
                                             self.cluster.scheduler_address,
                                             'workers': [{f"Worker {id}":
                                                          f"{worker.address}"}
                                                          for id, worker in
                                                          self.cluster.workers.items()]}})

        await s.listen(f"tcp://{self.admin_host}:{self.admin_port}")

    def run(self):
        """
        Runs a local dask cluster along with its monitoring thread
        """
        self.cluster = LocalCluster()
        scheduler_address = self.cluster.scheduler_address
        dashboard_link = self.cluster.dashboard_link
        set_config({"dask": {"scheduler_address": scheduler_address,
                             "dashboard_link": dashboard_link,
                             "admin_host": self.admin_host,
                             "admin_port": self.admin_port}})

        # Start monitoring server on an event loop
        loop = asyncio.get_event_loop()
        loop.create_task(self.admin_server())
        loop.run_forever()
