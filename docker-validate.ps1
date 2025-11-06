#!/usr/bin/env powershell
<#
.SYNOPSIS
    Validate Docker setup for FORScan containers.

.DESCRIPTION
    This script validates that Docker is properly configured and can run
    FORScan containers successfully.

.EXAMPLE
    .\docker-validate.ps1
    
.NOTES
    Run this script to ensure Docker setup is working correctly.
#>

param(
    [Switch]$Detailed,
    [Switch]$FixIssues
)

Write-Host "=== FORScan Docker Validation ===" -ForegroundColor Green
Write-Host ""

$script:ValidationResults = @()

# Function to add validation result
function Add-ValidationResult {
    param(
        [string]$Test,
        [bool]$Passed,
        [string]$Message,
        [string]$Fix = ""
    )
    
    $script:ValidationResults += [PSCustomObject]@{
        Test = $Test
        Passed = $Passed
        Message = $Message
        Fix = $Fix
    }
    
    $status = if ($Passed) { "✅ PASS" } else { "❌ FAIL" }
    $color = if ($Passed) { "Green" } else { "Red" }
    
    Write-Host "$status $Test" -ForegroundColor $color
    if ($Message) {
        Write-Host "   $Message" -ForegroundColor Gray
    }
}

# Test 1: Docker Installation
Write-Host "1. Checking Docker Installation..." -ForegroundColor Cyan
try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Add-ValidationResult "Docker Installation" $true "Docker is installed: $dockerVersion"
    } else {
        Add-ValidationResult "Docker Installation" $false "Docker not found in PATH" "Run: .\docker-install.ps1"
    }
} catch {
    Add-ValidationResult "Docker Installation" $false "Docker not installed" "Run: .\docker-install.ps1"
}

# Test 2: Docker Running
Write-Host "2. Checking Docker Service..." -ForegroundColor Cyan
try {
    $dockerInfo = docker info 2>$null
    if ($LASTEXITCODE -eq 0) {
        Add-ValidationResult "Docker Service" $true "Docker is running"
    } else {
        Add-ValidationResult "Docker Service" $false "Docker is not running" "Start Docker Desktop"
    }
} catch {
    Add-ValidationResult "Docker Service" $false "Cannot connect to Docker daemon" "Start Docker Desktop"
}

# Test 3: Docker Compose
Write-Host "3. Checking Docker Compose..." -ForegroundColor Cyan
try {
    $composeVersion = docker-compose --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Add-ValidationResult "Docker Compose" $true "Docker Compose available: $composeVersion"
    } else {
        Add-ValidationResult "Docker Compose" $false "Docker Compose not available" "Update Docker Desktop"
    }
} catch {
    Add-ValidationResult "Docker Compose" $false "Docker Compose not found" "Update Docker Desktop"
}

# Test 4: Required Directories
Write-Host "4. Checking Project Structure..." -ForegroundColor Cyan
$requiredDirs = @("data", "config", "logs", "python")
$missingDirs = @()

foreach ($dir in $requiredDirs) {
    if (-not (Test-Path $dir)) {
        $missingDirs += $dir
    }
}

if ($missingDirs.Count -eq 0) {
    Add-ValidationResult "Project Directories" $true "All required directories exist"
} else {
    $missing = $missingDirs -join ", "
    Add-ValidationResult "Project Directories" $false "Missing directories: $missing" "Run: New-Item -ItemType Directory -Force $missing"
    
    if ($FixIssues) {
        Write-Host "   Creating missing directories..." -ForegroundColor Yellow
        foreach ($dir in $missingDirs) {
            New-Item -ItemType Directory -Force $dir | Out-Null
        }
        Write-Host "   Directories created successfully" -ForegroundColor Green
    }
}

# Test 5: Docker Files
Write-Host "5. Checking Docker Configuration..." -ForegroundColor Cyan
$dockerFiles = @("Dockerfile", "Dockerfile.python", "docker-compose.yml", ".dockerignore")
$missingFiles = @()

foreach ($file in $dockerFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -eq 0) {
    Add-ValidationResult "Docker Configuration" $true "All Docker files present"
} else {
    $missing = $missingFiles -join ", "
    Add-ValidationResult "Docker Configuration" $false "Missing files: $missing" "Restore missing Docker files"
}

# Test 6: Python Requirements
Write-Host "6. Checking Python Requirements..." -ForegroundColor Cyan
if (Test-Path "requirements.txt") {
    Add-ValidationResult "Python Requirements" $true "requirements.txt found"
} else {
    Add-ValidationResult "Python Requirements" $false "requirements.txt missing" "Restore requirements.txt file"
}

# Test 7: Container Build Test (if Docker is working)
$dockerWorking = $false
try {
    docker info > $null 2>&1
    $dockerWorking = ($LASTEXITCODE -eq 0)
} catch {
    $dockerWorking = $false
}

if ($dockerWorking) {
    Write-Host "7. Testing Container Build..." -ForegroundColor Cyan
    try {
        # Test Python container build
        $buildOutput = docker-compose build forscan-python 2>&1
        if ($LASTEXITCODE -eq 0) {
            Add-ValidationResult "Container Build" $true "Python container builds successfully"
        } else {
            Add-ValidationResult "Container Build" $false "Container build failed" "Check Docker logs: docker-compose build forscan-python"
        }
    } catch {
        Add-ValidationResult "Container Build" $false "Build test failed" "Check Docker configuration"
    }
} else {
    Add-ValidationResult "Container Build" $false "Skipped - Docker not available" "Fix Docker issues first"
}

# Test 8: Python Import Test (if containers can run)
if ($dockerWorking) {
    Write-Host "8. Testing Python Package..." -ForegroundColor Cyan
    try {
        # Test if Python package can be imported
        $testOutput = docker run --rm -v "${PWD}/python:/app/python" python:3.11-slim python -c "import sys; sys.path.append('/app'); import forscan; print('Import successful')" 2>&1
        if ($testOutput -match "Import successful") {
            Add-ValidationResult "Python Package" $true "FORScan Python package imports correctly"
        } else {
            Add-ValidationResult "Python Package" $false "Python package import failed" "Check Python package structure"
        }
    } catch {
        Add-ValidationResult "Python Package" $false "Package test failed" "Verify Python files"
    }
} else {
    Add-ValidationResult "Python Package" $false "Skipped - Docker not available" "Fix Docker issues first"
}

# Summary
Write-Host ""
Write-Host "=== Validation Summary ===" -ForegroundColor Green

$passed = ($script:ValidationResults | Where-Object { $_.Passed }).Count
$total = $script:ValidationResults.Count
$failed = $total - $passed

Write-Host "Tests Passed: $passed/$total" -ForegroundColor Green
if ($failed -gt 0) {
    Write-Host "Tests Failed: $failed" -ForegroundColor Red
}

# Show failures and fixes
$failures = $script:ValidationResults | Where-Object { -not $_.Passed }
if ($failures.Count -gt 0) {
    Write-Host ""
    Write-Host "=== Issues Found ===" -ForegroundColor Yellow
    
    foreach ($failure in $failures) {
        Write-Host "❌ $($failure.Test): $($failure.Message)" -ForegroundColor Red
        if ($failure.Fix) {
            Write-Host "   Fix: $($failure.Fix)" -ForegroundColor Cyan
        }
    }
    
    Write-Host ""
    Write-Host "=== Quick Fix Commands ===" -ForegroundColor Cyan
    
    # Docker not installed
    if ($failures | Where-Object { $_.Test -eq "Docker Installation" }) {
        Write-Host "# Install Docker:" -ForegroundColor White
        Write-Host ".\docker-install.ps1" -ForegroundColor Gray
    }
    
    # Docker not running
    if ($failures | Where-Object { $_.Test -eq "Docker Service" }) {
        Write-Host "# Start Docker:" -ForegroundColor White
        Write-Host 'Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"' -ForegroundColor Gray
    }
    
    # Missing directories
    if ($failures | Where-Object { $_.Test -eq "Project Directories" }) {
        Write-Host "# Create directories:" -ForegroundColor White
        Write-Host "New-Item -ItemType Directory -Force data, config, logs" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "Run with -FixIssues to automatically fix some issues" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "🎉 All tests passed! Docker setup is working correctly." -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run:" -ForegroundColor Cyan
    Write-Host "  docker-compose up -d forscan-python" -ForegroundColor White
    Write-Host "  docker-compose exec forscan-python python -m forscan.cli info" -ForegroundColor White
}

# Detailed output
if ($Detailed) {
    Write-Host ""
    Write-Host "=== Detailed Results ===" -ForegroundColor Cyan
    $script:ValidationResults | Format-Table Test, Passed, Message -AutoSize
}

# Return appropriate exit code
if ($failed -gt 0) {
    exit 1
} else {
    exit 0
}