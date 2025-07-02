#!/usr/bin/env python3
from app.core.database import engine
from app.models.user import User
from app.services.auth_service import AuthService
from app.schemas.auth import UserRegister
from sqlalchemy.orm import sessionmaker

def create_test_user():
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        auth_service = AuthService(db)
        existing_user = auth_service.get_user_by_username("demo")
        if existing_user:
            print("用户 demo 已存在")
            return
        user_data = UserRegister(
            username="demo",
            email="demo@example.com",
            password="demo123",
            full_name="Demo User"
        )
        user = auth_service.create_user(user_data)
        print(f"成功创建用户: {user.username}")
    except Exception as e:
        print(f"创建用户失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
