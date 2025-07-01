from fastapi import Depends, HTTPException, status
from typing import Optional

def get_current_user():
    # 占位依赖，实际应从 token/session 获取用户
    # 这里返回模拟用户
    return {"id": "test-user-id", "username": "testuser", "role": "admin"} 