# Docker Troubleshooting Guide for FORScan

This guide helps resolve common Docker issues when setting up the FORScan containerized environment.

## Quick Fixes

### 1. Docker Not Installed
```powershell
# Run the Docker installation script
.\docker-install.ps1

# Or install manually:
# 1. Download Docker Desktop from https://www.docker.com/products/docker-desktop/
# 2. Run installer as Administrator
# 3. Restart computer
# 4. Start Docker Desktop
```

### 2. Docker Not Running
```powershell
# Start Docker Desktop
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Or check service status
Get-Service -Name "*docker*"

# If service is stopped, start it
Start-Service docker
```

### 3. Windows Containers Not Available
```powershell
# Switch to Windows containers in Docker Desktop
& "C:\Program Files\Docker\Docker\DockerCli.exe" -SwitchDaemon

# Or from Docker Desktop tray icon: Right-click -> Switch to Windows containers
```

## Common Issues and Solutions

### Issue: "The term 'docker' is not recognized"
**Solution:**
```powershell
# Add Docker to PATH
$env:PATH += ";C:\Program Files\Docker\Docker\resources\bin"

# Or restart PowerShell/Command Prompt after Docker installation
```

### Issue: "Cannot connect to Docker daemon"
**Solutions:**
1. **Start Docker Desktop:**
   ```powershell
   Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
   ```

2. **Check Docker service:**
   ```powershell
   Get-Service docker
   Start-Service docker
   ```

3. **Reset Docker:**
   ```powershell
   # From Docker Desktop: Settings -> Troubleshoot -> Reset to factory defaults
   ```

### Issue: "Platform not supported" or Windows container errors
**Solutions:**
1. **Enable Windows containers:**
   - Right-click Docker Desktop tray icon
   - Select "Switch to Windows containers"

2. **Enable required Windows features:**
   ```powershell
   Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All
   Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform
   ```

### Issue: "No space left on device" or build context too large
**Solutions:**
1. **Clean Docker:**
   ```powershell
   docker system prune -a
   docker volume prune
   ```

2. **Optimize .dockerignore:**
   ```
   # Add to .dockerignore
   .git
   *.log
   node_modules/
   __pycache__/
   ```

### Issue: Port conflicts (ports already in use)
**Solutions:**
1. **Check what's using the port:**
   ```powershell
   netstat -ano | findstr :8000
   ```

2. **Change ports in docker-compose.yml:**
   ```yaml
   ports:
     - "8080:8000"  # Changed from 8000:8000
   ```

### Issue: Volume mount failures
**Solutions:**
1. **Use volume mounts instead of bind mounts:**
   ```yaml
   volumes:
     - type: volume
       source: forscan-data
       target: /app/data
   ```

2. **Create directories first:**
   ```powershell
   New-Item -ItemType Directory -Force data, config, logs
   ```

### Issue: Container exits immediately
**Solutions:**
1. **Check container logs:**
   ```powershell
   docker-compose logs forscan-python
   docker logs forscan-python
   ```

2. **Run container interactively:**
   ```powershell
   docker run -it forscan-python /bin/bash
   ```

## Running FORScan Containers

### Production Setup
```powershell
# Create required directories
New-Item -ItemType Directory -Force data, config, logs

# Start Python automation only (recommended)
docker-compose up -d forscan-python

# Or start both Windows and Python containers
docker-compose up -d
```

### Development Setup
```powershell
# Start development environment
docker-compose --profile development up -d

# Connect to development container
docker exec -it forscan-python-dev /bin/bash
```

### Testing Setup
```powershell
# Test Python environment only
docker run --rm -v ${PWD}/python:/app/python forscan-python python -c "import forscan; print('Success!')"

# Run tests in container
docker-compose exec forscan-python python -m pytest python/tests/ -v
```

## Container Management

### View running containers
```powershell
docker ps
docker-compose ps
```

### View logs
```powershell
docker-compose logs -f forscan-python
docker logs forscan-python --follow
```

### Stop containers
```powershell
docker-compose down
docker-compose down --volumes  # Also remove volumes
```

### Rebuild containers
```powershell
docker-compose build --no-cache
docker-compose up -d --force-recreate
```

## Performance Optimization

### Resource Limits
Edit `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 1G      # Reduce from 2G
      cpus: '1.0'     # Reduce from 2.0
```

### Image Size Optimization
1. **Multi-stage builds** (already implemented)
2. **Use .dockerignore** (already configured)
3. **Clean package caches:**
   ```dockerfile
   RUN apt-get update && apt-get install -y package \
       && rm -rf /var/lib/apt/lists/*
   ```

## Windows-Specific Issues

### Hyper-V Not Available
**For Windows Home users:**
```powershell
# Enable WSL 2 backend instead
wsl --install
wsl --set-default-version 2

# Use WSL 2 backend in Docker Desktop settings
```

### Firewall Issues
```powershell
# Allow Docker through Windows Firewall
New-NetFirewallRule -DisplayName "Docker Desktop" -Direction Inbound -Protocol TCP -LocalPort 2375-2376 -Action Allow
```

### Antivirus Interference
- Add Docker directories to antivirus exclusions:
  - `C:\Program Files\Docker\`
  - `C:\ProgramData\Docker\`
  - `%USERPROFILE%\.docker\`

## Alternative Solutions

### If Docker Desktop fails to work:

1. **Use Podman:**
   ```powershell
   # Install Podman (Docker alternative)
   winget install RedHat.Podman
   
   # Use with docker-compose
   podman-compose up -d
   ```

2. **Use WSL 2 + Docker CE:**
   ```bash
   # Inside WSL 2 Ubuntu
   sudo apt update
   sudo apt install docker.io docker-compose
   sudo service docker start
   ```

3. **Run Python directly (without containers):**
   ```powershell
   # Install Python dependencies locally
   pip install -r requirements.txt
   
   # Run FORScan Python tools
   python -m forscan.cli --help
   ```

## Getting Help

If issues persist:

1. **Check Docker Desktop logs:**
   - Docker Desktop -> Settings -> Troubleshoot -> Export logs

2. **Check system requirements:**
   - Windows 10/11 Pro, Enterprise, or Education
   - 4GB RAM minimum, 8GB recommended
   - Hyper-V and Containers features enabled

3. **Docker Community:**
   - [Docker Desktop Issues](https://github.com/docker/for-win/issues)
   - [Docker Forums](https://forums.docker.com/)

4. **FORScan Python Issues:**
   - Check logs: `docker-compose logs forscan-python`
   - Test Python environment: `python -m forscan.cli info`