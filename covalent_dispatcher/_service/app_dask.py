from __future__ import annotations

import signal
import asyncio
import os
from logging import Logger
from threading import Thread
from multiprocessing import Process, current_process

import dask.config
from dask.distributed import Client, LocalCluster
from distributed.core import Server

from covalent._shared_files import logger
from covalent._shared_files.config import set_config

app_log = logger.app_log

# Configure dask to not allow daemon workers
dask.config.set({"distributed.worker.daemon": False})


class DaskCluster(Process):
    def __init__(self, logger: Logger, admin_host: str = "127.0.0.1", admin_port: int = 8000):
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
        self.loop = asyncio.get_event_loop()

    async def admin_server(self):
        s = Server(
            {
                "scale": lambda comm, nworkers: self.cluster.scale(n=nworkers),
            }
        )

        await s.listen(f"tcp://{self.admin_host}:{self.admin_port}")


    def run(self):
        """
        Runs a local dask cluster along with its monitoring thread
        """
        self.cluster = LocalCluster()
        scheduler_address = self.cluster.scheduler_address
        dashboard_link = self.cluster.dashboard_link
        try:
            set_config(
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

        self.loop.create_task(self.admin_server())
        self.loop.run_forever()
