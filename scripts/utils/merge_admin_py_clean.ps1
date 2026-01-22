#!/usr/bin/env pwsh
# merge_admin_py_clean.ps1
# Merge duplicate admin.py files, preserve login interface and route registration functionality

Write-Host "=== Merge admin.py duplicate files script ===" -ForegroundColor Green

# Define file paths
$pathA = "C:\Users\11581\Downloads\sport-lottery-sweeper\Users\11581\Downloads\sport-lottery-sweeper\backend\api\v1\admin.py"
$pathB = "C:\Users\11581\Downloads\sport-lottery-sweeper\backend\api\v1\admin.py"

# Check if files exist
$fileAExists = Test-Path $pathA
$fileBExists = Test-Path $pathB

if (-not $fileAExists -and -not $fileBExists) {
    Write-Host "Error: Both admin.py files do not exist!" -ForegroundColor Red
    exit 1
}

# Read file contents
$contentA = if ($fileAExists) { Get-Content $pathA -Raw } else { "" }
$contentB = if ($fileBExists) { Get-Content $pathB -Raw } else { "" }

Write-Host "`nFile status:" -ForegroundColor Cyan
Write-Host "  Path A exists: $fileAExists"
Write-Host "  Path B exists: $fileBExists"

# Analyze content - use simple string contains check instead of regex
$hasLoginFunctionA = $contentA.Contains('@router.post("/login"')
$hasRegisterSubRoutersB = $contentB.Contains('def register_sub_routers')

Write-Host "`nContent analysis:" -ForegroundColor Cyan
Write-Host "  Path A contains login interface: $hasLoginFunctionA"
Write-Host "  Path B contains route registrar: $hasRegisterSubRoutersB"

# Check if Path A file actually exists (the duplicate one)
if ($fileAExists) {
    Write-Host "`nPath A file found at: $pathA" -ForegroundColor Yellow
    Write-Host "File size: $((Get-Item $pathA).Length) bytes"
} else {
    Write-Host "`nPath A file does not exist (this is good - no duplicate)" -ForegroundColor Green
}

# Target file path (use normal backend/api/v1/admin.py)
$targetPath = $pathB

# Check current target file content
if ($fileBExists) {
    Write-Host "`nCurrent target file analysis:" -ForegroundColor Cyan
    if ($contentB.Contains('@router.post("/login"')) {
        Write-Host "  Contains login interface: YES"
    } else {
        Write-Host "  Contains login interface: NO"
    }
    if ($contentB.Contains('def register_sub_routers')) {
        Write-Host "  Contains route registrar: YES"
    } else {
        Write-Host "  Contains route registrar: NO"
    }
}

# Since Path A doesn't exist, we'll create a merged version based on analysis
# Let's check what we need to merge
$needMerge = $false

if ($fileBExists) {
    $hasLogin = $contentB.Contains('@router.post("/login"')
    $hasRegister = $contentB.Contains('def register_sub_routers')
    
    if ($hasLogin -and $hasRegister) {
        Write-Host "`nTarget file already contains both functionalities. No merge needed." -ForegroundColor Green
        $needMerge = $false
    } elseif ($hasLogin -xor $hasRegister) {
        Write-Host "`nTarget file missing one functionality. Merge needed." -ForegroundColor Yellow
        $needMerge = $true
    } else {
        Write-Host "`nTarget file missing both functionalities. Creating complete version." -ForegroundColor Yellow
        $needMerge = $true
    }
} else {
    Write-Host "`nTarget file doesn't exist. Cannot proceed." -ForegroundColor Red
    exit 1
}

if ($needMerge) {
    Write-Host "`nCreating backup and merged file..." -ForegroundColor Cyan
    
    # Backup original file
    $backupPath = "$pathB.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $pathB $backupPath
    Write-Host "Backup created: $backupPath" -ForegroundColor Green
    
    # Create complete merged content
    $mergedContent = @'
""""
Admin API routes
Complete version: contains login interface and sub-route registration functionality
""""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

# Import models and schemas
from ...schemas.auth import LoginRequest, LoginResponse
from ...core.auth import authenticate_user, create_access_token, get_current_user
from ...models.user import User
from ...config import settings
from ...database import get_db

logger = logging.getLogger("api.v1.admin")

router = APIRouter()

# ===== Login interface =====
@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """"
    User login interface
    """"
    user = await authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or password error"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at.isoformat()
        }
    }

# ===== Sub-route registration functionality =====
def register_sub_routers():
    """"
    Register sub-routes
    """"
    try:
        from .admin_user_management import router as admin_user_router
        router.include_router(admin_user_router, prefix="/users", tags=["admin-users"])
        logger.info("Admin - Admin user management routes registered")
    except Exception as e:
        logger.error(f"Admin - Admin user management route registration failed: {e}")
    
    try:
        from .frontend_user_management import router as frontend_user_router
        router.include_router(frontend_user_router, prefix="/frontend-users", tags=["frontend-users"])
        logger.info("Admin - Frontend user management routes registered")
    except Exception as e:
        logger.error(f"Admin - Frontend user management route registration failed: {e}")

# Register sub-routes
register_sub_routers()
'@

    # Write merged content
    try {
        [System.IO.File]::WriteAllText($targetPath, $mergedContent, [System.Text.UTF8Encoding]::new($false))
        Write-Host "Merge completed, result saved to: $targetPath" -ForegroundColor Green
    } catch {
        Write-Host "Error: Failed to write file - $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# Final verification
Write-Host "`nFinal verification:" -ForegroundColor Cyan
if (Test-Path $targetPath) {
    $finalContent = Get-Content $targetPath -Raw
    $hasLoginFinal = $finalContent.Contains('@router.post("/login"')
    $hasRegisterFinal = $finalContent.Contains('def register_sub_routers')
    
    Write-Host "  Login interface present: $hasLoginFinal"
    Write-Host "  Route registrar present: $hasRegisterFinal"
    
    if ($hasLoginFinal -and $hasRegisterFinal) {
        Write-Host "`nSUCCESS: Merged file contains all required functionality!" -ForegroundColor Green
    } else {
        Write-Host "`nWARNING: Merged file may be incomplete!" -ForegroundColor Yellow
    }
}

Write-Host "`nMerge script testing completed!" -ForegroundColor Green