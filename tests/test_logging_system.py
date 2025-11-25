#!/usr/bin/env python3
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "backend"))

from core.log_paths import (
    ensure_log_directories,
    LOGS_ROOT,
    LOGS_APPLICATION,
    LOGS_DEVICES,
    LOGS_DIAGNOSTICS,
    LOGS_SERVICES,
    LOGS_FRIDA_ACTIVATION,
    LOG_CENTRAL,
    LOG_BACKEND,
    LOG_ERRORS,
)
from core.logger import get_logger
from utils.frida_debug import FridaDebugLogger


def test_log_paths_exist():
    print("Testing log path constants...")
    
    paths_to_check = {
        "LOGS_ROOT": LOGS_ROOT,
        "LOGS_APPLICATION": LOGS_APPLICATION,
        "LOGS_DEVICES": LOGS_DEVICES,
        "LOGS_DIAGNOSTICS": LOGS_DIAGNOSTICS,
        "LOGS_SERVICES": LOGS_SERVICES,
        "LOGS_FRIDA_ACTIVATION": LOGS_FRIDA_ACTIVATION,
    }
    
    for name, path in paths_to_check.items():
        print(f"  {name}: {path}")
        assert isinstance(path, Path), f"{name} should be a Path object"
    
    print("✓ All log path constants are defined correctly\n")


def test_directory_creation():
    print("Testing directory creation...")
    
    ensure_log_directories()
    
    directories_to_check = [
        LOGS_APPLICATION,
        LOGS_DEVICES,
        LOGS_DIAGNOSTICS,
        LOGS_SERVICES,
        LOGS_FRIDA_ACTIVATION,
    ]
    
    for directory in directories_to_check:
        assert directory.exists(), f"Directory {directory} was not created"
        assert directory.is_dir(), f"{directory} is not a directory"
        print(f"  ✓ {directory.relative_to(project_root)} exists")
    
    print("✓ All log directories created successfully\n")


def test_logger_initialization():
    print("Testing logger initialization...")
    
    logger_backend = get_logger("test_module", "backend")
    logger_device = get_logger("test_device_module", "device")
    
    assert logger_backend is not None, "Backend logger should not be None"
    assert logger_device is not None, "Device logger should not be None"
    
    print("  ✓ Backend logger initialized")
    print("  ✓ Device logger initialized")
    print("✓ Logger initialization successful\n")


def test_logger_writes():
    print("Testing logger file writes...")
    
    logger = get_logger("test_write_module", "backend")
    
    test_message = "TEST_LOG_CENTRALIZATION_MESSAGE"
    logger.info(test_message)
    logger.error("TEST_ERROR_MESSAGE")
    
    assert LOG_CENTRAL.exists(), f"Central log {LOG_CENTRAL} not created"
    assert LOG_BACKEND.exists(), f"Backend log {LOG_BACKEND} not created"
    assert LOG_ERRORS.exists(), f"Error log {LOG_ERRORS} not created"
    
    central_content = LOG_CENTRAL.read_text()
    backend_content = LOG_BACKEND.read_text()
    errors_content = LOG_ERRORS.read_text()
    
    assert test_message in central_content, "Test message not found in central.log"
    assert test_message in backend_content, "Test message not found in backend.log"
    assert "TEST_ERROR_MESSAGE" in errors_content, "Error message not found in errors.log"
    
    print(f"  ✓ Central log: {LOG_CENTRAL.relative_to(project_root)}")
    print(f"  ✓ Backend log: {LOG_BACKEND.relative_to(project_root)}")
    print(f"  ✓ Error log: {LOG_ERRORS.relative_to(project_root)}")
    print("✓ Logger writes to correct files\n")


def test_frida_debug_logger():
    print("Testing FridaDebugLogger...")
    
    device_serial = "test_device_123"
    device_info = {
        "serial": device_serial,
        "model": "Test Device",
        "android_version": "11",
        "architecture": "x86_64",
        "has_root": True
    }
    
    debug_logger = FridaDebugLogger(device_serial, device_info)
    
    debug_logger.add_device_info("Test Key", "Test Value")
    debug_logger.add_frida_config("Test Config", "/test/path")
    debug_logger.add_permission_info("Test permission info")
    debug_logger.add_adb_operation("test command", "test output")
    debug_logger.add_startup_info("Test startup info")
    debug_logger.set_result(False, "Test failure message")
    
    log_file_path = debug_logger.write()
    
    if log_file_path is None:
        raise AssertionError("Debug log file path should not be None")
    
    log_file = Path(log_file_path)
    
    if not log_file.exists():
        raise AssertionError(f"Debug log file {log_file} was not created")
    
    if log_file.parent != LOGS_FRIDA_ACTIVATION:
        raise AssertionError(f"Debug log should be in {LOGS_FRIDA_ACTIVATION}, but is in {log_file.parent}")
    
    content = log_file.read_text()
    
    if "FRIDA SERVER ACTIVATION DEBUG LOG" not in content:
        raise AssertionError("Debug log should contain header 'FRIDA SERVER ACTIVATION DEBUG LOG'")
    if "Test Key: Test Value" not in content:
        raise AssertionError("Debug log should contain device info 'Test Key: Test Value'")
    if "Test failure message" not in content:
        raise AssertionError("Debug log should contain failure message 'Test failure message'")
    
    log_file.unlink()
    
    print(f"  ✓ Debug log created in: {LOGS_FRIDA_ACTIVATION.relative_to(project_root)}")
    print(f"  ✓ Debug log contains correct information")
    print("✓ FridaDebugLogger works correctly\n")


def test_no_old_directories():
    print("Testing that old log directories don't exist...")
    
    old_directories = [
        LOGS_ROOT / "backend",
        LOGS_ROOT / "device",
        LOGS_ROOT / "server",
        LOGS_ROOT / "errors" / "frida-server",
    ]
    
    for old_dir in old_directories:
        if old_dir.exists():
            print(f"  ⚠ Warning: Old directory still exists: {old_dir.relative_to(project_root)}")
        else:
            print(f"  ✓ Old directory removed: {old_dir.relative_to(project_root)}")
    
    print("✓ Old directory check complete\n")


def test_log_structure():
    print("Testing complete log structure...")
    
    expected_structure = {
        "application": ["central.log", "backend.log", "errors.log"],
        "devices": ["device.log"],
        "diagnostics/frida/activation": [],
        "services": [],
    }
    
    for rel_path, expected_files in expected_structure.items():
        dir_path = LOGS_ROOT / rel_path
        assert dir_path.exists(), f"Expected directory {rel_path} does not exist"
        
        for expected_file in expected_files:
            file_path = dir_path / expected_file
            if file_path.exists():
                print(f"  ✓ {rel_path}/{expected_file} exists")
            else:
                print(f"  ℹ {rel_path}/{expected_file} not yet created (will be created on first write)")
    
    print("✓ Log structure is correct\n")


def main():
    print("=" * 70)
    print("CENTRALIZED LOGGING SYSTEM TEST")
    print("=" * 70)
    print()
    
    tests = [
        ("Log Paths", test_log_paths_exist),
        ("Directory Creation", test_directory_creation),
        ("Logger Initialization", test_logger_initialization),
        ("Logger Writes", test_logger_writes),
        ("FridaDebugLogger", test_frida_debug_logger),
        ("Old Directories", test_no_old_directories),
        ("Log Structure", test_log_structure),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_name} FAILED: {e}\n")
            failed += 1
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}\n")
            failed += 1
    
    print("=" * 70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("\n✓ All tests passed! Centralized logging system is working correctly.")
        return 0
    else:
        print(f"\n✗ {failed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

