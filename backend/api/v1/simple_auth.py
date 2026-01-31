from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import bcrypt
import sqlite3
import os

router = APIRouter()

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 7200

class UserLogin(BaseModel):
    username: str
    password: str

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_by_username(username: str):
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    db_path = os.path.join(project_root, "sport_lottery.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, password_hash, role, status FROM admin_users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "username": row[1], "email": row[2], "password_hash": row[3], "role": row[4], "status": row[5]}
    return None

@router.post("/login")
async def login(login_data: UserLogin):
    user = get_user_by_username(login_data.username)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    if not bcrypt.checkpw(login_data.password.encode('utf-8'), user["password_hash"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    if user["status"] != "active":
        raise HTTPException(status_code=401, detail="用户账户已被禁用")
    
    token = create_access_token({"user_id": user["id"], "username": user["username"], "role": user["role"]})
    
    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "access_token": token,
            "token_type": "bearer",
            "user_info": {
                "userId": user["id"],
                "username": user["username"],
                "email": user["email"],
                "roles": [user["role"]],
                "status": user["status"]
            }
        }
    }
