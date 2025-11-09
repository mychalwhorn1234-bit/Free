#!/usr/bin/env python3
"""
Example automation script for FORScan.

This script demonstrates how to use the FORScan Python library
to automate common diagnostic tasks.
"""

import logging
import time
from forscan import FORScanConnector, DiagnosticSession, Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def automated_health_check():
    """
    Perform automated vehicle health check.
    
    This function demonstrates a complete diagnostic workflow:
    1. Connect to vehicle
    2. Read vehicle information  
    3. Scan for diagnostic trouble codes
    4. Read live data parameters
    5. Generate health report
    """
    
    # Load configuration
    config = Config()
    
    # Create connector
    connector = FORScanConnector(config.get_forscan_config())
    
    try:
        # Connect to vehicle
        logger.info("Connecting to vehicle...")
        if not connector.connect(
            adapter_type=config.adapter.type,
            port=config.adapter.port
        ):
            logger.error("Failed to connect to vehicle")
            return False
        
        # Get vehicle information
        vehicle_info = connector.get_vehicle_info()
        if vehicle_info:
            logger.info(f"Connected to: {vehicle_info.year} {vehicle_info.make} {vehicle_info.model}")
        
        # Start diagnostic session
        session = DiagnosticSession(connector)
        if not session.start_session():
            logger.error("Failed to start diagnostic session")
            return False
        
        # Scan for DTCs
        logger.info("Scanning for diagnostic trouble codes...")
        dtcs = session.scan_dtcs()
        
        if dtcs:
            logger.warning(f"Found {len(dtcs)} diagnostic trouble codes:")
            for dtc in dtcs:
                logger.warning(f"  {dtc.code}: {dtc.description}")
        else:
            logger.info("No diagnostic trouble codes found")
        
        # Read live data
        logger.info("Reading live data...")
        live_data = session.read_live_data(["RPM", "SPEED"])
        
        for pid, param in live_data.items():
            logger.info(f"  {param.name}: {param.value} {param.unit}")
        
        # Generate session summary
        summary = session.get_session_summary()
        logger.info(f"Health check completed in {summary.get('duration', 'unknown')}")
        
        # End session
        session.end_session()
        
        return True
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False
    
    finally:
        # Always disconnect
        connector.disconnect()


def automated_dtc_clear():
    """
    Automated DTC clearing procedure.
    
    Demonstrates how to safely clear diagnostic trouble codes
    after repairs have been completed.
    """
    
    config = Config()
    connector = FORScanConnector(config.get_forscan_config())
    
    try:
        # Connect and start session
        if not connector.connect(config.adapter.type, config.adapter.port):
            logger.error("Failed to connect to vehicle")
            return False
        
        session = DiagnosticSession(connector)
        if not session.start_session():
            logger.error("Failed to start diagnostic session")
            return False
        
        # First scan to see what DTCs exist
        logger.info("Scanning for existing DTCs...")
        dtcs = session.scan_dtcs()
        
        if not dtcs:
            logger.info("No DTCs found to clear")
            return True
        
        logger.info(f"Found {len(dtcs)} DTCs to clear:")
        for dtc in dtcs:
            logger.info(f"  {dtc.code}: {dtc.description}")
        
        # Clear DTCs
        logger.info("Clearing DTCs...")
        if session.clear_dtcs():
            logger.info("DTCs cleared successfully")
            
            # Verify clearing was successful
            time.sleep(2)
            remaining_dtcs = session.scan_dtcs()
            
            if remaining_dtcs:
                logger.warning(f"{len(remaining_dtcs)} DTCs remain after clearing")
            else:
                logger.info("All DTCs cleared successfully")
        else:
            logger.error("Failed to clear DTCs")
            return False
        
        session.end_session()
        return True
        
    except Exception as e:
        logger.error(f"DTC clearing failed: {e}")
        return False
    
    finally:
        connector.disconnect()


def main():
    """Main script entry point."""
    
    logger.info("FORScan Automation Script Starting...")
    
    # Perform automated health check
    logger.info("=== Automated Health Check ===")
    health_check_success = automated_health_check()
    
    if not health_check_success:
        logger.error("Health check failed, aborting further operations")
        return
    
    # Ask user if they want to clear DTCs
    try:
        response = input("\nDo you want to clear any existing DTCs? (y/N): ")
        if response.lower() in ['y', 'yes']:
            logger.info("=== Automated DTC Clearing ===")
            automated_dtc_clear()
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
    
    logger.info("Automation script completed")


if __name__ == "__main__":
    main()