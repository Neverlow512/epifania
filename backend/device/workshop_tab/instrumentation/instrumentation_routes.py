from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from pathlib import Path
import json
import shutil
import subprocess
import platform
import os
from core.logger import get_logger
from device.workshop_tab.session.workshop_session import workshop_session
from device.workshop_tab.frida_session.session_manager import frida_session_manager
from device.workshop_tab.instrumentation.tools.observer.observer import Observer
from device.workshop_tab.instrumentation.tools.observer.hook_manager import observer_hook_manager
from device.workshop_tab.instrumentation.tools.observer.logging.observer_logger import read_observer_logs

logger = get_logger(__name__, "device")
router = APIRouter()


def validate_session_ownership(device_id: str, client_id: str):
    if not workshop_session.is_owner(device_id, client_id):
        raise HTTPException(
            status_code=403,
            detail="Workshop session not owned by this client"
        )


class ObserverStartRequest(BaseModel):
    client_id: str
    app_package: str
    hooks: List[Dict[str, Any]]
    time_limit: Optional[int] = None


class ObserverStopRequest(BaseModel):
    client_id: str


class ObserverLogsRequest(BaseModel):
    client_id: str
    log_files: List[str]


class SaveScriptRequest(BaseModel):
    client_id: str


class OpenFolderRequest(BaseModel):
    path: str


@router.post("/{device_id}/observer/start")
async def start_observer(device_id: str, request: ObserverStartRequest):
    try:
        validate_session_ownership(device_id, request.client_id)
        
        session = frida_session_manager.get_session(device_id)
        if not session:
            raise HTTPException(status_code=400, detail="No active Frida session")
        
        java_hooks = [h for h in request.hooks if h.get("type") == "java"]
        native_hooks = [h for h in request.hooks if h.get("type") == "native"]
        
        logger.info(f"Starting observer for {device_id}: {len(java_hooks)} Java hooks, {len(native_hooks)} Native hooks")
        
        observer = Observer(device_id, session)
        result = observer.start_observation(
            request.app_package,
            request.hooks,
            request.time_limit
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start observer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/observer/stop")
async def stop_observer(device_id: str, request: ObserverStopRequest):
    try:
        validate_session_ownership(device_id, request.client_id)
        result = observer_hook_manager.stop_observer_session(device_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop observer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/observer/status")
async def get_observer_status(device_id: str, client_id: str):
    try:
        validate_session_ownership(device_id, client_id)
        status = observer_hook_manager.get_session_status(device_id)
        
        if not status:
            return {
                "active": False,
                "message": "No active observer session"
            }
        
        return {
            "active": True,
            **status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get observer status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/observer/logs")
async def get_observer_logs(device_id: str, request: ObserverLogsRequest):
    try:
        validate_session_ownership(device_id, request.client_id)
        
        session_info = observer_hook_manager.get_session_status(device_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="No active observer session")
        
        session_path_str = session_info.get("session_path")
        if not session_path_str:
            raise HTTPException(status_code=500, detail="Session path not found")
        
        session_path = Path(session_path_str)
        
        results = {}
        for log_file in request.log_files:
            try:
                results[log_file] = await read_observer_logs(session_path, log_file)
            except Exception as e:
                logger.error(f"Failed to read log file {log_file}: {e}")
                results[log_file] = {"error": str(e)}
        
        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get observer logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/observer/save_script")
async def save_observer_script(device_id: str, request: SaveScriptRequest):
    try:
        validate_session_ownership(device_id, request.client_id)
        
        session_info = observer_hook_manager.get_session_status(device_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="No active observer session")
        
        script_code = observer_hook_manager.get_script_code(device_id)
        if not script_code:
            raise HTTPException(status_code=500, detail="Script code not available")
        
        session_name = session_info.get("session_name")
        if not session_name:
            raise HTTPException(status_code=500, detail="Session name not found")
        
        script_vault_path = Path("device/workshop_tab/script_vault/personal/observer") / session_name
        script_vault_path.mkdir(parents=True, exist_ok=True)
        
        hooks = session_info.get("hooks", {})
        hooks_list = []
        for hook_id, hook_data in hooks.items():
            hooks_list.append({
                "id": hook_id,
                "type": hook_data.get("type", "java"),
                "class_name": hook_data.get("class_name", ""),
                "method_name": hook_data.get("method_name", ""),
                "signature": hook_data.get("signature", ""),
                "return_type": hook_data.get("return_type", ""),
                "parameters": hook_data.get("parameters", [])
            })
        
        hooks_file = script_vault_path / "hooks.json"
        with open(hooks_file, 'w') as f:
            json.dump(hooks_list, f, indent=2)
        
        template_path = Path("device/workshop_tab/instrumentation/tools/observer/README_TEMPLATE.md")
        hooks_sample = json.dumps([{
            "id": h["id"],
            "class_name": h["class_name"],
            "method_name": h["method_name"],
            "signature": h["signature"]
        } for h in hooks_list[:2]], indent=2)
        
        if template_path.exists():
            with open(template_path, 'r') as f:
                readme_content = f.read()
            
            readme_content = readme_content.format(
                session_name=session_name,
                app_package=session_info.get('app_package', 'N/A'),
                device_id=device_id,
                session_path=session_info.get('session_path', 'N/A'),
                hooks_count=len(hooks_list),
                hooks_sample=hooks_sample
            )
        else:
            readme_content = f"# Observer Session: {session_name}\n\nREADME template not found."
            logger.warning(f"README template not found at {template_path}")
        
        readme_file = script_vault_path / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        hook_type = hooks_list[0].get('type', 'java') if hooks_list else 'java'
        template_source = Path(f"device/workshop_tab/script_vault/instrumentation/observer/{hook_type}/observer_{hook_type}.ts")
        if template_source.exists():
            template_dest = script_vault_path / "observer_template.ts"
            shutil.copy(template_source, template_dest)
            logger.info(f"Copied template from {template_source} to {template_dest}")
        else:
            logger.warning(f"Template not found at {template_source}")
        
        compiled_file = script_vault_path / "compiled_script.js"
        with open(compiled_file, 'w') as f:
            f.write(script_code)
        
        logger.info(f"Saved observer script bundle to {script_vault_path}")
        
        return {
            "success": True,
            "message": "Script saved successfully",
            "path": str(script_vault_path.absolute()),
            "session_name": session_name
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save observer script: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/open_folder")
async def open_folder(request: OpenFolderRequest):
    try:
        folder_path = Path(request.path).resolve()
        if not folder_path.exists():
            raise HTTPException(status_code=404, detail=f"Folder not found: {request.path}")
        
        system = platform.system()
        
        if system == "Linux":
            env = os.environ.copy()
            
            if 'DISPLAY' not in env:
                env['DISPLAY'] = ':0'
            
            if 'XAUTHORITY' not in env:
                user_home = os.path.expanduser('~')
                xauth_path = os.path.join(user_home, '.Xauthority')
                if os.path.exists(xauth_path):
                    env['XAUTHORITY'] = xauth_path
            
            if 'DBUS_SESSION_BUS_ADDRESS' not in env:
                dbus_path = os.path.join(os.path.expanduser('~'), '.dbus', 'session-bus', f'{os.environ.get("DISPLAY", ":0").replace(":", "")}-0')
                if os.path.exists(dbus_path):
                    with open(dbus_path, 'r') as f:
                        for line in f:
                            if line.startswith('DBUS_SESSION_BUS_ADDRESS='):
                                env['DBUS_SESSION_BUS_ADDRESS'] = line.split('=', 1)[1].strip()
                                break
            
            commands_to_try = [
                (['xdg-open', str(folder_path)], 'xdg-open'),
                (['gio', 'open', str(folder_path)], 'gio'),
                (['nautilus', '--no-desktop', str(folder_path)], 'nautilus'),
                (['dolphin', '--select', str(folder_path)], 'dolphin'),
                (['thunar', str(folder_path)], 'thunar')
            ]
            
            last_error = None
            for cmd, name in commands_to_try:
                if not shutil.which(cmd[0]):
                    continue
                    
                try:
                    logger.info(f"Attempting to open folder with: {' '.join(cmd)}")
                    subprocess.Popen(
                        cmd,
                        env=env,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        start_new_session=True,
                        close_fds=True
                    )
                    logger.info(f"Successfully executed: {name} for {folder_path}")
                    return {
                        "success": True,
                        "message": f"Folder opened with {name}"
                    }
                except Exception as e:
                    last_error = e
                    logger.warning(f"Failed to open with {name}: {e}")
                    continue
            
            if last_error:
                raise last_error
            else:
                raise Exception("No file manager command found")
                
        elif system == "Darwin":
            subprocess.Popen(
                ["open", str(folder_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            logger.info(f"Opened folder in file manager: {folder_path}")
            
        elif system == "Windows":
            subprocess.Popen(
                ["explorer", str(folder_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            logger.info(f"Opened folder in file manager: {folder_path}")
        else:
            raise HTTPException(status_code=500, detail=f"Unsupported platform: {system}")
        
        return {
            "success": True,
            "message": "Folder opened successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to open folder: {e}")
        raise HTTPException(status_code=500, detail=str(e))
