from __future__ import annotations

import asyncio
import datetime
import json
import time
from dataclasses import asdict, dataclass
from multiprocessing import Process
from typing import List

import psutil
import websockets

from covalent_dispatcher._cli.service import UI_PIDFILE


@dataclass(order=True, repr=True)
class CPUTimes:
    user: float
    system: float
    children_user: float
    children_system: float


@dataclass(repr=True, order=True)
class IOCounters:
    read_count: int
    write_count: int
    read_bytes: int
    write_bytes: int
    read_chars: int
    write_chars: int


@dataclass(repr=True, order=True)
class MemoryInfo:
    rss: int
    vms: int
    shared: int
    text: int
    lib: int
    data: int
    dirty: int
    uss: int
    pss: int
    swap: int


@dataclass(order=True, repr=True)
class ProcessStat:
    status: str
    cpu_percent: float
    cpu_times: CPUTimes
    io_counters: IOCounters
    mem_info: MemoryInfo
    mem_percent: float
    timestamp: float


class ResourceTracker(Process):
    """Track the resource utilization by Covalent server"""

    def __init__(self, pid: int, update_interval: int, logger):
        self.update_interval = update_interval
        self.proc = psutil.Process(pid)
        self.proc_children = self.proc.children()
        self.logger = logger
        super().__init__()

    def parse_cpu_times(self, proc: psutil.Process) -> CPUTimes:
        """Yield CPUTimes for the process"""
        pcputime = proc.cpu_times()
        return CPUTimes(
            user=pcputime.user,
            system=pcputime.system,
            children_user=pcputime.children_user,
            children_system=pcputime.children_system,
        )

    def parse_io_counters(self, proc: psutil.Process) -> MemoryInfo:
        """Yield IOCounters for the process"""
        piocnt = proc.io_counters()
        return IOCounters(
            read_count=piocnt.read_count,
            write_count=piocnt.write_count,
            read_bytes=piocnt.read_bytes,
            write_bytes=piocnt.write_bytes,
            read_chars=piocnt.read_chars,
            write_chars=piocnt.write_chars,
        )

    def parse_mem_info(self, proc: psutil.Process) -> MemoryInfo:
        """Yield memory info for the process"""
        meminfo = proc.memory_full_info()
        return MemoryInfo(
            rss=meminfo.rss,
            vms=meminfo.vms,
            shared=meminfo.shared,
            text=meminfo.text,
            lib=meminfo.lib,
            data=meminfo.data,
            dirty=meminfo.dirty,
            uss=meminfo.uss,
            pss=meminfo.pss,
            swap=meminfo.swap,
        )

    def parse_stat_info(self) -> ProcessStat:
        """Extract the process stat info"""
        cpu_times = self.parse_cpu_times(self.proc)
        io_counters = self.parse_io_counters(self.proc)
        mem_info = self.parse_mem_info(self.proc)
        return ProcessStat(
            timestamp=time.mktime(datetime.datetime.now().timetuple()),
            status=self.proc.status(),
            cpu_percent=self.proc.cpu_percent(),
            cpu_times=cpu_times,
            io_counters=io_counters,
            mem_info=mem_info,
            mem_percent=self.proc.memory_percent(),
        )

    async def scrape_metrics(self, websocket):
        """Create a instance of the process data class and broadcast it as a message"""
        while True:
            try:
                proc_stat = self.parse_stat_info()
            except Exception as ce:
                self.logger.exception(ce)

            self.logger.debug(f"ProcessStat: {asdict(proc_stat)}")
            await websocket.send(json.dumps(asdict(proc_stat)))
            await asyncio.sleep(self.update_interval)

    async def server(self):
        async with websockets.serve(self.scrape_metrics, "0.0.0.0", 8995):
            await asyncio.Future()

    def run(self):
        self.logger.warning("here")
        asyncio.run(self.server())
