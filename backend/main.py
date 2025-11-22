from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from core.device_manager import DeviceManager
from core.logger import get_logger

logger = get_logger(__name__, "backend")

app = FastAPI(title="Epifania API", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    logger.info("Epifania backend starting up")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

device_manager = DeviceManager()


@app.get("/health")
async def health_check():
    logger.debug("Health check requested")
    return {"status": "healthy"}


@app.get("/api/devices")
async def get_devices():
    try:
        logger.info("Device enumeration requested")
        devices = device_manager.list_devices()
        logger.info(f"Found {len(devices)} device(s)")
        return {"devices": devices}
    except Exception as e:
        logger.error(f"Failed to enumerate devices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

