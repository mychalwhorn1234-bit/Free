#!/usr/bin/env powershell
<#
.SYNOPSIS
    Install and setup Docker Desktop for Windows with FORScan support.

.DESCRIPTION
    This script helps install Docker Desktop for Windows and sets up the environment
    for running FORScan containers with both Windows and Linux container support.

.EXAMPLE
    .\docker-install.ps1
    
.NOTES
    Requires administrator privileges for Docker Desktop installation.
#>

param(
    [Switch]$Force,
    [Switch]$SkipInstall,
    [Switch]$ConfigureOnly
)

# Require administrator privileges
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script requires administrator privileges. Please run as Administrator."
    exit 1
}

Write-Host "=== FORScan Docker Setup Script ===" -ForegroundColor Green
Write-Host ""

# Function to check if Docker is installed
function Test-DockerInstalled {
    try {
        $null = Get-Command docker -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

# Function to check if Docker is running
function Test-DockerRunning {
    try {
        docker version > $null 2>&1
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

# Function to download and install Docker Desktop
function Install-DockerDesktop {
    Write-Host "Downloading Docker Desktop for Windows..." -ForegroundColor Yellow
    
    $dockerUrl = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
    $installer = "$env:TEMP\DockerDesktopInstaller.exe"
    
    try {
        Invoke-WebRequest -Uri $dockerUrl -OutFile $installer -UseBasicParsing
        Write-Host "Downloaded Docker Desktop installer" -ForegroundColor Green
        
        Write-Host "Installing Docker Desktop..." -ForegroundColor Yellow
        Start-Process -FilePath $installer -ArgumentList "install", "--quiet", "--accept-license" -Wait
        
        Write-Host "Docker Desktop installation completed" -ForegroundColor Green
        Write-Host "Please restart your computer and then re-run this script with -ConfigureOnly flag" -ForegroundColor Yellow
        
    }
    catch {
        Write-Error "Failed to download or install Docker Desktop: $($_.Exception.Message)"
        exit 1
    }
    finally {
        if (Test-Path $installer) {
            Remove-Item $installer -Force
        }
    }
}

# Function to enable required Windows features
function Enable-WindowsFeatures {
    Write-Host "Enabling required Windows features..." -ForegroundColor Yellow
    
    $features = @(
        "Microsoft-Windows-Subsystem-Linux",
        "VirtualMachinePlatform",
        "Microsoft-Hyper-V-All"
    )
    
    foreach ($feature in $features) {
        try {
            $featureState = Get-WindowsOptionalFeature -Online -FeatureName $feature -ErrorAction SilentlyContinue
            if ($featureState -and $featureState.State -ne "Enabled") {
                Write-Host "Enabling $feature..." -ForegroundColor Cyan
                Enable-WindowsOptionalFeature -Online -FeatureName $feature -All -NoRestart
            }
            else {
                Write-Host "$feature is already enabled" -ForegroundColor Green
            }
        }
        catch {
            Write-Warning "Could not enable $feature. You may need to enable it manually."
        }
    }
}

# Function to create required directories
function New-ProjectDirectories {
    Write-Host "Creating required directories..." -ForegroundColor Yellow
    
    $directories = @(
        ".\data",
        ".\config", 
        ".\logs"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "Created directory: $dir" -ForegroundColor Green
        }
        else {
            Write-Host "Directory already exists: $dir" -ForegroundColor Cyan
        }
    }
}

# Function to configure Docker settings
function Set-DockerConfiguration {
    Write-Host "Configuring Docker settings..." -ForegroundColor Yellow
    
    # Create Docker daemon configuration
    $dockerConfigDir = "$env:ProgramData\Docker\config"
    $daemonConfigFile = "$dockerConfigDir\daemon.json"
    
    if (-not (Test-Path $dockerConfigDir)) {
        New-Item -ItemType Directory -Path $dockerConfigDir -Force | Out-Null
    }
    
    $daemonConfig = @{
        "experimental" = $true
        "features" = @{
            "buildkit" = $true
        }
        "storage-driver" = "windowsfilter"
    } | ConvertTo-Json -Depth 3
    
    $daemonConfig | Out-File -FilePath $daemonConfigFile -Encoding UTF8
    Write-Host "Created Docker daemon configuration" -ForegroundColor Green
}

# Function to test Docker setup
function Test-DockerSetup {
    Write-Host "Testing Docker setup..." -ForegroundColor Yellow
    
    if (-not (Test-DockerInstalled)) {
        Write-Error "Docker is not installed or not in PATH"
        return $false
    }
    
    if (-not (Test-DockerRunning)) {
        Write-Host "Starting Docker Desktop..." -ForegroundColor Cyan
        Start-Process -FilePath "C:\Program Files\Docker\Docker\Docker Desktop.exe"
        
        # Wait for Docker to start
        $timeout = 60
        $elapsed = 0
        while (-not (Test-DockerRunning) -and $elapsed -lt $timeout) {
            Start-Sleep -Seconds 5
            $elapsed += 5
            Write-Host "Waiting for Docker to start... ($elapsed/$timeout seconds)" -ForegroundColor Cyan
        }
        
        if (-not (Test-DockerRunning)) {
            Write-Error "Docker failed to start within $timeout seconds"
            return $false
        }
    }
    
    # Test basic Docker functionality
    try {
        Write-Host "Testing Docker with hello-world container..." -ForegroundColor Cyan
        docker run --rm hello-world | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Docker is working correctly!" -ForegroundColor Green
            return $true
        }
        else {
            Write-Error "Docker test failed"
            return $false
        }
    }
    catch {
        Write-Error "Docker test failed: $($_.Exception.Message)"
        return $false
    }
}

# Main execution
try {
    # Check current Docker status
    if (Test-DockerInstalled) {
        Write-Host "Docker is already installed" -ForegroundColor Green
        
        if (Test-DockerRunning) {
            Write-Host "Docker is running" -ForegroundColor Green
        }
        else {
            Write-Host "Docker is installed but not running" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "Docker is not installed" -ForegroundColor Red
        
        if (-not $SkipInstall -and -not $ConfigureOnly) {
            if ($Force -or (Read-Host "Would you like to install Docker Desktop? (y/N)").ToLower() -eq 'y') {
                Enable-WindowsFeatures
                Install-DockerDesktop
                exit 0  # Require restart after installation
            }
            else {
                Write-Host "Skipping Docker installation" -ForegroundColor Yellow
            }
        }
    }
    
    # Configure environment
    if (-not $SkipInstall) {
        New-ProjectDirectories
        
        if (Test-DockerInstalled) {
            Set-DockerConfiguration
        }
    }
    
    # Test setup if Docker is available
    if (Test-DockerInstalled) {
        if (Test-DockerSetup) {
            Write-Host ""
            Write-Host "=== Docker Setup Complete ===" -ForegroundColor Green
            Write-Host "You can now run FORScan containers using:" -ForegroundColor Cyan
            Write-Host "  docker-compose up -d" -ForegroundColor White
            Write-Host "  docker-compose up forscan-python" -ForegroundColor White
            Write-Host ""
            Write-Host "For development:" -ForegroundColor Cyan
            Write-Host "  docker-compose --profile development up -d" -ForegroundColor White
        }
        else {
            Write-Error "Docker setup test failed"
            exit 1
        }
    }
    else {
        Write-Host ""
        Write-Host "=== Manual Installation Required ===" -ForegroundColor Yellow
        Write-Host "Please install Docker Desktop manually from:" -ForegroundColor Cyan
        Write-Host "https://www.docker.com/products/docker-desktop/" -ForegroundColor White
        Write-Host ""
        Write-Host "After installation, run this script again with -ConfigureOnly flag" -ForegroundColor Cyan
    }
}
catch {
    Write-Error "Setup failed: $($_.Exception.Message)"
    exit 1
}