"""
安全相关功能
"""
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from app.core.config import settings

def get_encryption_key() -> bytes:
    """获取加密密钥"""
    # 使用配置中的密钥或生成新密钥
    if hasattr(settings, 'ENCRYPTION_KEY') and settings.ENCRYPTION_KEY:
        return base64.urlsafe_b64encode(settings.ENCRYPTION_KEY.encode()[:32].ljust(32, b'0'))
    else:
        # 生成默认密钥
        return Fernet.generate_key()

def encrypt_text(text: str) -> str:
    """加密文本"""
    try:
        key = get_encryption_key()
        f = Fernet(key)
        encrypted_data = f.encrypt(text.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    except Exception as e:
        # 如果加密失败，返回原文本
        return text

def decrypt_text(encrypted_text: str) -> str:
    """解密文本"""
    try:
        key = get_encryption_key()
        f = Fernet(key)
        encrypted_data = base64.urlsafe_b64decode(encrypted_text.encode())
        decrypted_data = f.decrypt(encrypted_data)
        return decrypted_data.decode()
    except Exception as e:
        # 如果解密失败，返回原文本
        return encrypted_text

def hash_password(password: str) -> str:
    """哈希密码"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)

def generate_api_key() -> str:
    """生成API密钥"""
    return base64.urlsafe_b64encode(os.urandom(32)).decode()

def generate_token() -> str:
    """生成令牌"""
    return base64.urlsafe_b64encode(os.urandom(32)).decode() 