from __future__ import annotations

import asyncio
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ContextManager,
    Dict,
    Generator,
    Iterable,
    List,
    Tuple,
)

if TYPE_CHECKING:
    from ..base import BaseAsyncExecutor

from covalent._shared_files import logger

app_log = logger.app_log


class AsyncFileMonitor:
    def __init__(
        self,
        executor: BaseAsyncExecutor,
        path: str,
        results_dir: str,
        dispatch_id: str,
        node_id: int,
    ):
        self.executor = executor
        self.path = path
        self.results_dir = results_dir
        self.dispatch_id = dispatch_id
        self.node_id = node_id

        self.msg_queue = asyncio.Queue()
        self.monitored_file = None

        self.watch_future = None

    # Async generator
    async def generate_file_contents(self, path: str, chunksize: int = -1) -> Generator:
        bytes_read = 0
        while True:
            contents = await self.executor.poll_file(path, bytes_read, chunksize)
            bytes_read += len(contents)

            app_log.debug(f"file_monitor: read {bytes_read} bytes from {path}")
            yield contents

    async def update_node_info(self, chunk):
        app_log.debug(f"update_node_info: {self.path}: {chunk}")
        # TODO

    async def update_executor_info(self, chunk):
        if chunk:
            contents = f"{self.path}: {chunk}"
            await self.executor.write_streams_to_file(
                [contents], [self.executor.log_info], self.dispatch_id, self.results_dir
            )

    async def get(self):
        transferred_size = 0
        async for chunk in self.monitored_file:
            if not chunk:
                break
            transferred_size += len(chunk)
            await self.update_node_info(chunk)
            await self.update_executor_info(chunk)

        return transferred_size

    async def watch_file(self, msg_queue: asyncio.Queue):
        app_log.debug(f"Starting to watch file {self.path}")
        self.monitored_file = self.generate_file_contents(self.path)
        msg = await msg_queue.get()
        watching = True
        if msg != "get":
            app_log.debug("watch_file: cancelled")
            watching = False

        while watching:
            size = await self.get()
            app_log.debug(f"watch_file: pulled {size} bytes from executor")
            msg = await msg_queue.get()
            if msg != "get":
                app_log.debug("watch_file_task cancelled")
                watching = False

    async def watch_file_periodically(self, msg_queue, pollfreq: int = 1):

        app_log.debug("Starting file watching timer")
        watcher_queue = asyncio.Queue()
        fut = asyncio.create_task(self.watch_file(watcher_queue))

        app_log.debug("Started file watching timer")
        while True:
            try:
                app_log.debug("watch_file_periodically: Checking for messages")
                msg = msg_queue.get_nowait()

                app_log.debug(f"watch_file_periodically: Received message {msg}")
                await watcher_queue.put("cancel")
                break
            except asyncio.QueueEmpty:
                app_log.debug("watch_file_periodically: no messages")
                pass

            app_log.debug(f"watch_file_periodically: polling {self.path}")
            await watcher_queue.put("get")
            await asyncio.sleep(pollfreq)

        app_log.debug("watch_file_periodically: cancelled")
        await fut

    def start(self, pollfreq: int = 1) -> asyncio.Future:
        self.watch_future = asyncio.create_task(
            self.watch_file_periodically(self.msg_queue, pollfreq)
        )
        return self.watch_future

    async def cancel(self):
        if self.watch_future:
            await self.msg_queue.put("cancel")
            await self.watch_future
            self.watch_future = None
