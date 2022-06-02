import asyncio

from dask.distributed import LocalCluster

from covalent._shared_files import logger
from covalent._shared_files.config import set_config

app_log = logger.app_log
log_stack_info = logger.log_stack_info


async def start_cluster():
    cluster = LocalCluster()
    scheduler_address = cluster.scheduler_address
    scheduler_port = int(scheduler_address.split(":")[-1])
    app_log.warning(f"The Dask scheduler is running on {scheduler_address}")
    set_config(
        {
            "dask": {
                "scheduler_address": scheduler_address,
                "scheduler_port": scheduler_port,
            }
        }
    )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(start_cluster())
    loop.run_forever()
