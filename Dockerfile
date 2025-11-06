# Use Windows Server Core as base image for better Windows compatibility
FROM mcr.microsoft.com/windows/servercore:ltsc2022

# Set PowerShell as the default shell
SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

# Set working directory using Windows path conventions
WORKDIR C:\\app

# Copy application files
COPY . .

# Install any required Windows dependencies and setup FORScan environment
RUN Write-Host 'Setting up FORScan environment...'; New-Item -ItemType Directory -Force -Path C:\\app\\forscan

# Set environment variables for Windows
ENV FORSCAN_PORTABLE=true
ENV FORSCAN_DATA_DIR=C:\\app\\forscan\\data
ENV FORSCAN_CONFIG_DIR=C:\\app\\forscan\\config

# Expose any required ports (adjust as needed for FORScan communication)
# EXPOSE 8080

# Health check using PowerShell
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD powershell -Command "if (Test-Path 'C:\\app\\forscan') { exit 0 } else { exit 1 }"

# Default command to run FORScan (would need actual executable)
# CMD ["powershell", "-Command", "& 'C:\\app\\forscan\\FORScan.exe'"]
CMD ["powershell", "-Command", "Write-Host 'FORScan container ready'; Start-Sleep -Seconds 3600"]