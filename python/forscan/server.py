#!/usr/bin/env python3
"""
REST API server for FORScan Python automation tools.

Provides HTTP endpoints for diagnostic operations, vehicle scanning,
and configuration management.
"""

import logging
import uvicorn
from contextlib import asynccontextmanager
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from forscan import FORScanConnector, DiagnosticSession, Config
from forscan.adapters import ELM327Adapter, J2534Adapter

logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
class ConnectionRequest(BaseModel):
    """Request model for vehicle connection."""
    adapter_type: str = Field(default="ELM327", description="Adapter type (ELM327, J2534, STN)")
    port: str = Field(default="COM1", description="Communication port")
    baudrate: int = Field(default=38400, description="Baud rate for serial communication")


class ConfigUpdate(BaseModel):
    """Request model for configuration updates."""
    adapter: Optional[Dict[str, Any]] = None
    logging: Optional[Dict[str, Any]] = None
    forscan: Optional[Dict[str, Any]] = None


class VehicleInfoResponse(BaseModel):
    """Response model for vehicle information."""
    make: str
    model: str
    year: int
    vin: Optional[str] = None
    engine: Optional[str] = None


class DTCResponse(BaseModel):
    """Response model for diagnostic trouble codes."""
    dtcs: List[Dict[str, str]]
    count: int


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str
    connected: bool


# Global state
_config: Optional[Config] = None
_connector: Optional[FORScanConnector] = None
_session: Optional[DiagnosticSession] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan (startup and shutdown)."""
    global _config, _connector, _session
    
    # Startup
    logger.info("Starting FORScan API server")
    
    # Load configuration
    _config = Config()
    _config.setup_logging()
    
    # Initialize connector
    _connector = FORScanConnector(_config.get_forscan_config())
    
    logger.info("FORScan API server started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FORScan API server")
    
    # End session if active
    if _session and _session.session_active:
        _session.end_session()
    
    # Disconnect from vehicle
    if _connector and _connector.connected:
        _connector.disconnect()
    
    logger.info("FORScan API server stopped")


# Initialize FastAPI app
app = FastAPI(
    title="FORScan Python API",
    description="REST API for FORScan diagnostic automation",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "FORScan Python API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    global _connector
    
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        connected=_connector.connected if _connector else False
    )


@app.get("/config", response_model=Dict[str, Any])
async def get_config():
    """Get current configuration."""
    global _config
    
    if not _config:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configuration not initialized"
        )
    
    return {
        "adapter": _config.get_adapter_config(),
        "logging": _config.get_logging_config(),
        "forscan": _config.get_forscan_config()
    }


@app.put("/config", response_model=Dict[str, str])
async def update_config(config_update: ConfigUpdate):
    """Update configuration."""
    global _config
    
    if not _config:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configuration not initialized"
        )
    
    try:
        if config_update.adapter:
            _config.update_adapter_config(**config_update.adapter)
        
        if config_update.logging:
            _config.update_logging_config(**config_update.logging)
        
        if config_update.forscan:
            _config.update_forscan_config(**config_update.forscan)
        
        # Save configuration
        _config.save()
        
        return {"message": "Configuration updated successfully"}
        
    except Exception as e:
        logger.error(f"Failed to update configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Configuration update failed: {str(e)}"
        )


@app.post("/connect", response_model=Dict[str, str])
async def connect_vehicle(connection: ConnectionRequest):
    """Connect to vehicle via specified adapter."""
    global _connector, _config
    
    if not _connector:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Connector not initialized"
        )
    
    if _connector.connected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already connected to vehicle"
        )
    
    try:
        # Update adapter configuration
        _config.update_adapter_config(
            type=connection.adapter_type,
            port=connection.port,
            baudrate=connection.baudrate
        )
        
        # Attempt connection
        if _connector.connect(connection.adapter_type, connection.port):
            return {"message": "Successfully connected to vehicle"}
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to connect to vehicle"
            )
            
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Connection failed: {str(e)}"
        )


@app.post("/disconnect", response_model=Dict[str, str])
async def disconnect_vehicle():
    """Disconnect from vehicle."""
    global _connector, _session
    
    if not _connector:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Connector not initialized"
        )
    
    if not _connector.connected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not connected to vehicle"
        )
    
    try:
        # End session if active
        if _session and _session.session_active:
            _session.end_session()
            _session = None
        
        # Disconnect
        _connector.disconnect()
        
        return {"message": "Disconnected from vehicle"}
        
    except Exception as e:
        logger.error(f"Disconnect failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Disconnect failed: {str(e)}"
        )


@app.get("/vehicle/info", response_model=VehicleInfoResponse)
async def get_vehicle_info():
    """Get vehicle information."""
    global _connector
    
    if not _connector:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Connector not initialized"
        )
    
    if not _connector.connected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not connected to vehicle"
        )
    
    try:
        vehicle_info = _connector.get_vehicle_info()
        
        if not vehicle_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle information not available"
            )
        
        return VehicleInfoResponse(
            make=vehicle_info.make,
            model=vehicle_info.model,
            year=vehicle_info.year,
            vin=vehicle_info.vin,
            engine=vehicle_info.engine
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get vehicle info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get vehicle info: {str(e)}"
        )


@app.get("/dtcs", response_model=DTCResponse)
async def read_dtcs():
    """Read diagnostic trouble codes."""
    global _connector
    
    if not _connector:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Connector not initialized"
        )
    
    if not _connector.connected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not connected to vehicle"
        )
    
    try:
        dtc_data = _connector.read_dtcs()
        
        return DTCResponse(
            dtcs=dtc_data.get("dtcs", []),
            count=dtc_data.get("count", 0)
        )
        
    except Exception as e:
        logger.error(f"Failed to read DTCs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read DTCs: {str(e)}"
        )


@app.delete("/dtcs", response_model=Dict[str, str])
async def clear_dtcs():
    """Clear diagnostic trouble codes."""
    global _connector
    
    if not _connector:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Connector not initialized"
        )
    
    if not _connector.connected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not connected to vehicle"
        )
    
    try:
        if _connector.clear_dtcs():
            return {"message": "DTCs cleared successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear DTCs"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear DTCs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear DTCs: {str(e)}"
        )


@app.post("/session/start", response_model=Dict[str, str])
async def start_session():
    """Start diagnostic session."""
    global _connector, _session
    
    if not _connector:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Connector not initialized"
        )
    
    if not _connector.connected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not connected to vehicle"
        )
    
    if _session and _session.session_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already active"
        )
    
    try:
        _session = DiagnosticSession(_connector)
        
        if _session.start_session():
            return {"message": "Diagnostic session started"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to start session"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start session: {str(e)}"
        )


@app.post("/session/end", response_model=Dict[str, str])
async def end_session():
    """End diagnostic session."""
    global _session
    
    if not _session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active session"
        )
    
    if not _session.session_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session not active"
        )
    
    try:
        _session.end_session()
        _session = None
        
        return {"message": "Diagnostic session ended"}
        
    except Exception as e:
        logger.error(f"Failed to end session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end session: {str(e)}"
        )


def main(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """
    Start the FORScan API server.
    
    Args:
        host: Host to bind to (default: 127.0.0.1 for localhost only)
             Use 0.0.0.0 to expose on all network interfaces (not recommended for production)
        port: Port to bind to (default: 8000)
        reload: Enable auto-reload for development (default: False)
    """
    logger.info(f"Starting FORScan API server on {host}:{port}")
    
    uvicorn.run(
        "forscan.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
