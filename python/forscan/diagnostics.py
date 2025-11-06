"""
Diagnostic session management and utilities.
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

# Constants
NO_ACTIVE_SESSION_MSG = "No active diagnostic session"


@dataclass
class DiagnosticTroubleCode:
    """Diagnostic Trouble Code information."""
    code: str
    description: str
    status: str
    freeze_frame: dict[str, str | int | float] | None = None
    timestamp: datetime | None = None


@dataclass
class LiveDataParameter:
    """Live data parameter structure."""
    pid: str
    name: str
    value: str | int | float
    unit: str
    min_value: float | None = None
    max_value: float | None = None


class DiagnosticSession:
    """
    Manages diagnostic sessions with FORScan.
    
    This class provides high-level diagnostic operations
    including DTC management, live data streaming, and
    service procedures.
    """
    
    def __init__(self, connector):
        """
        Initialize diagnostic session.
        
        Args:
            connector: FORScanConnector instance
        """
        self.connector = connector
        self.session_active = False
        self.start_time: datetime | None = None
        self.dtcs: list[DiagnosticTroubleCode] = []
        self.live_data: dict[str, LiveDataParameter] = {}
        
    def start_session(self) -> bool:
        """
        Start diagnostic session.
        
        Returns:
            True if session started successfully
        """
        if not self.connector.connected:
            logger.error("Cannot start session: not connected to vehicle")
            return False
        
        try:
            self.session_active = True
            self.start_time = datetime.now()
            
            logger.info("Diagnostic session started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            return False
    
    def end_session(self) -> None:
        """End diagnostic session."""
        if self.session_active:
            duration = (
                datetime.now() - self.start_time 
                if self.start_time else None
            )
            logger.info(f"Diagnostic session ended (duration: {duration})")
            
            self.session_active = False
            self.start_time = None
    
    def scan_dtcs(self) -> list[DiagnosticTroubleCode]:
        """
        Scan for diagnostic trouble codes.
        
        Returns:
            List of DTCs found
        """
        if not self.session_active:
            logger.error(NO_ACTIVE_SESSION_MSG)
            return []
        
        try:
            logger.info("Scanning for DTCs...")
            
            # Get DTCs from connector
            dtc_data = self.connector.read_dtcs()
            
            self.dtcs = []
            for dtc in dtc_data.get("dtcs", []):
                self.dtcs.append(DiagnosticTroubleCode(
                    code=dtc["code"],
                    description=dtc["description"],
                    status="ACTIVE",
                    timestamp=datetime.now()
                ))
            
            logger.info(f"Found {len(self.dtcs)} DTCs")
            return self.dtcs
            
        except Exception as e:
            logger.error(f"DTC scan failed: {e}")
            return []
    
    def clear_dtcs(self) -> bool:
        """
        Clear diagnostic trouble codes.
        
        Returns:
            True if clearing successful
        """
        if not self.session_active:
            logger.error(NO_ACTIVE_SESSION_MSG)
            return False
        
        try:
            logger.info("Clearing DTCs...")
            
            success = self.connector.clear_dtcs()
            if success:
                self.dtcs.clear()
                logger.info("DTCs cleared successfully")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to clear DTCs: {e}")
            return False
    
    def read_live_data(
        self, pids: list[str]
    ) -> dict[str, LiveDataParameter]:
        """
        Read live data parameters.
        
        Args:
            pids: List of Parameter IDs to read
            
        Returns:
            Dictionary of live data parameters
        """
        if not self.session_active:
            logger.error(NO_ACTIVE_SESSION_MSG)
            return {}
        
        try:
            logger.debug(f"Reading live data for PIDs: {pids}")
            
            # Placeholder for actual live data reading
            for pid in pids:
                if pid == "RPM":
                    self.live_data[pid] = LiveDataParameter(
                        pid=pid,
                        name="Engine RPM",
                        value=750.0,
                        unit="rpm",
                        min_value=0,
                        max_value=8000
                    )
                elif pid == "SPEED":
                    self.live_data[pid] = LiveDataParameter(
                        pid=pid,
                        name="Vehicle Speed",
                        value=0.0,
                        unit="mph",
                        min_value=0,
                        max_value=200
                    )
            
            return self.live_data
            
        except Exception as e:
            logger.error(f"Failed to read live data: {e}")
            return {}
    
    def perform_service_procedure(
        self, 
        procedure_name: str, 
        parameters: dict[str, str | int | float] | None = None
    ) -> bool:
        """
        Perform service procedure.
        
        Args:
            procedure_name: Name of service procedure
            parameters: Optional parameters for the procedure
            
        Returns:
            True if procedure completed successfully
        """
        if not self.session_active:
            logger.error(NO_ACTIVE_SESSION_MSG)
            return False
        
        parameters = parameters or {}
        
        try:
            logger.info(f"Performing service procedure: {procedure_name}")
            
            # Placeholder for actual service procedures
            if procedure_name == "DPF_REGEN":
                logger.info("Starting DPF regeneration...")
                time.sleep(2)  # Simulate procedure time
                logger.info("DPF regeneration completed")
                return True
            
            elif procedure_name == "OIL_RESET":
                logger.info("Resetting oil life monitor...")
                time.sleep(1)
                logger.info("Oil life reset completed")
                return True
            
            elif procedure_name == "BMS_RESET":
                logger.info("Resetting battery monitoring system...")
                time.sleep(1)
                logger.info("BMS reset completed")
                return True
            
            else:
                logger.warning(f"Unknown service procedure: {procedure_name}")
                return False
                
        except Exception as e:
            logger.error(f"Service procedure failed: {e}")
            return False
    
    def get_session_summary(self) -> dict[str, str | bool | int | None]:
        """
        Get summary of current diagnostic session.
        
        Returns:
            Dictionary containing session summary
        """
        duration = None
        if self.session_active and self.start_time:
            duration = str(datetime.now() - self.start_time)
        
        return {
            "session_active": self.session_active,
            "start_time": (
                self.start_time.isoformat() if self.start_time else None
            ),
            "duration": duration,
            "dtc_count": len(self.dtcs),
            "live_data_parameters": len(self.live_data),
            "vehicle_connected": self.connector.connected
        }