"""
认证服务
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
import uuid

from app.core.config import settings
from app.models.user import User
from app.schemas.auth import UserRegister

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """认证服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """获取密码哈希"""
        return pwd_context.hash(password)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        try:
            # 将字符串转换为UUID
            user_uuid = uuid.UUID(user_id)
            return self.db.query(User).filter(User.id == user_uuid).first()
        except ValueError:
            # 如果user_id不是有效的UUID格式，返回None
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """验证用户凭据"""
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user
    
    def create_user(self, user_data: UserRegister) -> User:
        """创建新用户"""
        hashed_password = self.get_password_hash(user_data.password)
        
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            full_name=user_data.full_name,
            role="user"
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def create_access_token(self, user_id: str) -> str:
        """创建访问令牌"""
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode = {
            "sub": str(user_id),
            "exp": expire
        }
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        
        return encoded_jwt
    
    def get_current_user(self, token: str) -> User:
        """从令牌获取当前用户"""
        try:
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM]
            )
            user_id = payload.get("sub")
            
            if user_id is None:
                raise ValueError("无效的令牌")
                
        except jwt.ExpiredSignatureError:
            raise ValueError("令牌已过期")
        except jwt.exceptions.DecodeError:
            raise ValueError("无效的令牌")
        
        user = self.get_user_by_id(user_id)
        if user is None:
            raise ValueError("用户不存在")
        
        return user
    
    def update_user_profile(self, user_id: str, username: str, email: str) -> bool:
        """更新用户信息"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.username = username
        user.email = email
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    def update_user_password(self, user_id: str, new_password: str) -> bool:
        """更新用户密码"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.password_hash = self.get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True 