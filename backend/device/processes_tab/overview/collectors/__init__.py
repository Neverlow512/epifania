# Process data collectors

from device.processes_tab.overview.collectors.identity import IdentityCollector
from device.processes_tab.overview.collectors.memory import MemoryCollector
from device.processes_tab.overview.collectors.threads import ThreadsCollector
from device.processes_tab.overview.collectors.files import FilesCollector
from device.processes_tab.overview.collectors.network import NetworkCollector
from device.processes_tab.overview.collectors.io_stats import IOStatsCollector
from device.processes_tab.overview.collectors.relationships import RelationshipsCollector

__all__ = [
    "IdentityCollector",
    "MemoryCollector",
    "ThreadsCollector",
    "FilesCollector",
    "NetworkCollector",
    "IOStatsCollector",
    "RelationshipsCollector",
]

