# Cleanup utility for operation logs
import shutil
from pathlib import Path
from core.log_paths import LOGS_WORKSHOP_OPERATIONS
from core.logger import get_logger

logger = get_logger(__name__, "device")


def cleanup_old_sessions(keep_per_package: int = 10):
    """
    Keep only the latest N session folders per package.
    Groups by package prefix, sorts by modification time, deletes oldest.
    """
    if not LOGS_WORKSHOP_OPERATIONS.exists():
        return
    
    # Group folders by package
    packages = {}
    
    for folder in LOGS_WORKSHOP_OPERATIONS.iterdir():
        if not folder.is_dir():
            continue
        
        # Extract package from folder name: com_bumble_app_session_20251230_193500
        if "_session_" not in folder.name:
            continue
        
        package = folder.name.split("_session_")[0]
        
        if package not in packages:
            packages[package] = []
        packages[package].append(folder)
    
    # For each package, keep only latest N folders
    total_deleted = 0
    for package, folders in packages.items():
        if len(folders) > keep_per_package:
            # Sort by modification time (newest first)
            folders.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            # Delete old folders
            for old_folder in folders[keep_per_package:]:
                try:
                    shutil.rmtree(old_folder)
                    logger.info(f"Cleaned up old session: {old_folder.name}")
                    total_deleted += 1
                except Exception as e:
                    logger.error(f"Failed to delete session folder {old_folder.name}: {e}")
    
    if total_deleted > 0:
        logger.info(f"Operation logs cleanup complete: deleted {total_deleted} old session(s)")
    else:
        logger.info("Operation logs cleanup complete: no old sessions to delete")
