# Process inspector - orchestrates all collectors for comprehensive process overview

from typing import Dict, Optional
from core.logger import get_logger
from core.adb_manager import ADBManager
from device.contexts import InspectionContext
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
        self.identity_collector = IdentityCollector()
        self.memory_collector = MemoryCollector()
        self.threads_collector = ThreadsCollector()
        self.files_collector = FilesCollector()
        self.network_collector = NetworkCollector()
        self.io_collector = IOStatsCollector()
        self.relationships_collector = RelationshipsCollector()
        logger.info("ProcessInspector initialized")

    def inspect(self, device_serial: str, pid: int, has_root: bool = False) -> Optional[Dict]:
        try:
            logger.info(f"[ADB INSPECTION START] Process {pid} on {device_serial} (root: {has_root})")

            ctx = InspectionContext(self.adb_manager, device_serial, pid, has_root)

            identity = self.identity_collector.collect(ctx)
            if not identity:
                logger.warning(f"Process {pid} not found or inaccessible")
                return None

            memory = self.memory_collector.collect(ctx)
            threads = self.threads_collector.collect(ctx)
            files = self.files_collector.collect(ctx)
            network = self.network_collector.collect(ctx)
            io_stats = self.io_collector.collect(ctx)
            relationships = self.relationships_collector.collect(ctx)
            
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

