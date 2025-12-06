# Process inspector - orchestrates all collectors for comprehensive process overview

from typing import Dict, Optional
from core.logger import get_logger
from core.adb_manager import ADBManager
from device.processes_tab.overview.collectors.identity import IdentityCollector
from device.processes_tab.overview.collectors.memory import MemoryCollector
from device.processes_tab.overview.collectors.threads import ThreadsCollector
from device.processes_tab.overview.collectors.files import FilesCollector
from device.processes_tab.overview.collectors.network import NetworkCollector
from device.processes_tab.overview.collectors.io_stats import IOStatsCollector
from device.processes_tab.overview.collectors.relationships import RelationshipsCollector

logger = get_logger(__name__, "device")


class ProcessInspector:
    def __init__(self, adb_manager: ADBManager):
        self.adb_manager = adb_manager
        self.identity_collector = IdentityCollector(adb_manager)
        self.memory_collector = MemoryCollector(adb_manager)
        self.threads_collector = ThreadsCollector(adb_manager)
        self.files_collector = FilesCollector(adb_manager)
        self.network_collector = NetworkCollector(adb_manager)
        self.io_collector = IOStatsCollector(adb_manager)
        self.relationships_collector = RelationshipsCollector(adb_manager)
        logger.info("ProcessInspector initialized")

    def inspect(self, device_serial: str, pid: int, has_root: bool = False) -> Optional[Dict]:
        try:
            logger.info(f"[ADB INSPECTION START] Process {pid} on {device_serial} (root: {has_root})")

            identity = self.identity_collector.collect(device_serial, pid)
            if not identity:
                logger.warning(f"Process {pid} not found or inaccessible")
                return None

            memory = self.memory_collector.collect(device_serial, pid)
            threads = self.threads_collector.collect(device_serial, pid)
            files = self.files_collector.collect(device_serial, pid, has_root)
            network = self.network_collector.collect(device_serial, pid)
            io_stats = self.io_collector.collect(device_serial, pid, has_root)
            relationships = self.relationships_collector.collect(device_serial, pid)
            
            logger.info(f"[ADB INSPECTION COMPLETE] Process {pid} - collected all data")

            permissions = self._build_permissions(
                has_root=has_root,
                memory=memory,
                io_stats=io_stats,
                files=files,
            )

            return {
                "pid": pid,
                "identity": identity,
                "memory": memory,
                "threads": threads,
                "files": files,
                "network": network,
                "io": io_stats,
                "relationships": relationships,
                "permissions": permissions,
            }

        except Exception as e:
            logger.error(f"Failed to inspect process {pid} on {device_serial}: {str(e)}")
            return None

    def _build_permissions(
        self,
        has_root: bool,
        memory: Optional[Dict],
        io_stats: Optional[Dict],
        files: Optional[Dict],
    ) -> Dict:
        return {
            "has_root": has_root,
            "io_stats_available": io_stats is not None,
            "detailed_memory_available": (
                memory is not None and memory.get("smaps_available", False)
            ),
            "dumpsys_memory_available": (
                memory is not None and memory.get("dumpsys_available", False)
            ),
            "full_fd_access": files is not None and files.get("full_access", False),
        }

