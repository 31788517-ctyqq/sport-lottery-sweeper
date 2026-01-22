#!/usr/bin/env pwsh
# merge_admin_py.ps1
# 合并重复的 admin.py 文件，保留登录接口功能和路由注册功能

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

# Target file path (use normal backend/api/v1/admin.py)
$targetPath = $pathB

# Merge logic
$mergedContent = @'
"""
Admin API routes
Merged version: contains login interface and sub-route registration functionality
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

# Import models and schemas
from ...schemas.auth import LoginRequest, LoginResponse
from ...core.auth import authenticate_user, create_access_token, get_current_user
from ...models.user import User
from ...config import settings
from ...database import get_db  # Add missing get_db import

logger = logging.getLogger("api.v1.admin")

router = APIRouter()

# ===== Login interface (from file A) =====
@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    User login interface
    
    Args:
        login_data: Login credentials
        db: Database session
        
    Returns:
        LoginResponse: Login result
    """
    user = await authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or password error"
        )
    
    # Create access token
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


# ===== Sub-route registration functionality (from file B) =====
def register_sub_routers():
    """
    Register sub-routes
    """
    try:
        # Admin user management
        from .admin_user_management import router as admin_user_router
        router.include_router(admin_user_router, prefix="/users", tags=["admin-users"])
        logger.info("Admin - Admin user management routes registered")
    except Exception as e:
        logger.error(f"Admin - Admin user management route registration failed: {e}")
    
    try:
        # Frontend user management
        from .frontend_user_management import router as frontend_user_router
        router.include_router(frontend_user_router, prefix="/frontend-users", tags=["frontend-users"])
        logger.info("Admin - Frontend user management routes registered")
    except Exception as e:
        logger.error(f"Admin - Frontend user management route registration failed: {e}")

# Register sub-routes
register_sub_routers()
'@

# Backup original file
if ($fileBExists) {
    $backupPath = "$pathB.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $pathB $backupPath
    Write-Host "`nBackup created: $backupPath" -ForegroundColor Green
}

# Write merged content
try {
    # Save as UTF-8 without BOM
    [System.IO.File]::WriteAllText($targetPath, $mergedContent, [System.Text.UTF8Encoding]::new($false))
    Write-Host "Merge completed, result saved to: $targetPath" -ForegroundColor Green
} catch {
    Write-Host "Error: Failed to write file - $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Delete duplicate wrong path file (if exists)
if ($fileAExists) {
    try {
        Remove-Item $pathA -Force
        Write-Host "Duplicate file deleted: $pathA" -ForegroundColor Green
    } catch {
        Write-Host "Warning: Cannot delete duplicate file $pathA - $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host "`nMerge script completed successfully!" -ForegroundColor Green
Write-Host "Please check if the merged file works normally." -ForegroundColor Yellow
Write-Host "Note: If runtime prompts missing get_db, please ensure database.py has corresponding dependency definitions." -ForegroundColor Yellow
