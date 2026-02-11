#!/usr/bin/env python3
"""测试端点，验证FastAPI是否正常工作"""

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from backend.database import get_db

app = FastAPI()

@app.get("/test")
def test_endpoint(db: Session = Depends(get_db)):
    """测试端点"""
    return {"message": "Hello World", "status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)