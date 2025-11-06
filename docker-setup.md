# Windows Docker Setup for FORScan Portable

This directory contains Windows-compatible Docker configurations for the FORScan Portable project, including Python automation support.

## Prerequisites

- Windows 10/11 with Docker Desktop
- Windows containers enabled for FORScan service
- Linux containers support for Python services
- PowerShell 5.1 or later

## Quick Start

### Windows FORScan Container
```powershell
# Build and run Windows FORScan container
docker-compose up forscan

# Run in development mode
docker-compose --profile development up forscan-dev
```

### Python Automation Container
```powershell
# Build and run Python automation service
docker-compose up forscan-python

# Run Python development environment
docker-compose --profile development up python-dev
```

### Combined Setup
```powershell
# Run both Windows FORScan and Python services
docker-compose up forscan forscan-python

# Build all services
docker-compose build
```

## Files Overview

- `Dockerfile` - Windows Server Core based container for FORScan
- `Dockerfile.python` - Multi-stage Python container for automation
- `docker-compose.yml` - Multi-service configuration with both Windows and Python services
- `.dockerignore` - Excludes unnecessary files from build context
- `docker-setup.md` - This documentation file

## Services Architecture

### Windows Services (platform: windows/amd64)

- **forscan** - Main FORScan portable application container
- **forscan-dev** - Development environment for FORScan (development profile)

### Python Services (platform: linux/amd64)

- **forscan-python** - Python automation and API service
- **python-dev** - Python development environment (development profile)

## Container Communication

The Python service can communicate with the Windows FORScan service through:

- Shared volume mounts (`./data`, `./config`, `./logs`)
- Network communication (if FORScan exposes network interfaces)
- File-based data exchange

## Windows Container Considerations

1. **Base Image**: Uses `mcr.microsoft.com/windows/servercore:ltsc2022` for Windows compatibility
2. **Path Syntax**: All paths use Windows conventions (`C:\app\forscan`)
3. **PowerShell**: Default shell for better Windows integration
4. **Volume Mounts**: Uses Docker-compatible forward slash syntax for bind mounts
5. **Platform**: Explicitly set to `windows/amd64`

## Volume Mounts

The container expects these local directories:

- `./data` - Maps to `C:/app/forscan/data` (FORScan data files)
- `./config` - Maps to `C:/app/forscan/config` (Configuration files)

Create these directories before running:

```powershell
New-Item -ItemType Directory -Force -Path "data", "config"
```

## Environment Variables

- `FORSCAN_PORTABLE=true` - Enables portable mode
- `FORSCAN_DATA_DIR=C:/app/forscan/data` - Data directory path
- `FORSCAN_CONFIG_DIR=C:/app/forscan/config` - Config directory path
- `FORSCAN_DEBUG=true` - Enable debug mode (development only)

## Development Profile

Use the development profile for testing and debugging:

```powershell
docker-compose --profile development up forscan-dev
```

This mounts the entire source directory and enables debug mode.

## Troubleshooting

1. **Windows containers not enabled**: Enable Windows containers in Docker Desktop settings
2. **Permission issues**: Run PowerShell as Administrator
3. **Path issues**: Ensure Docker volume paths use forward slashes for compatibility
4. **Build failures**: Check that Windows containers are selected in Docker Desktop

## Security Notes

- Container runs with standard user privileges
- No network ports exposed by default
- Data and config directories are isolated via volume mounts
- Follows principle of least privilege for Windows containers
