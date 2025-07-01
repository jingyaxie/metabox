#!/usr/bin/env python3
"""
管理员系统初始化脚本
用于创建超级管理员账号和基础系统配置
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.admin import SuperAdmin, ModelProvider, ModelConfig, SystemConfig
from app.services.admin_service import AdminService
from app.schemas.admin import SuperAdminCreate
import bcrypt
import uuid
from datetime import datetime

def init_database():
    """初始化数据库表"""
    from app.models.admin import Base
    Base.metadata.create_all(bind=engine)

def create_super_admin():
    """创建超级管理员"""
    db = SessionLocal()
    try:
        admin_service = AdminService(db)
        
        # 检查是否已存在超级管理员
        existing_admin = db.query(SuperAdmin).first()
        if existing_admin:
            print("超级管理员已存在，跳过创建")
            return existing_admin
        
        # 创建超级管理员
        admin_data = SuperAdminCreate(
            username="admin",
            password="admin123",
            email="admin@metabox.local"
        )
        
        admin = admin_service.create_super_admin(admin_data)
        print(f"超级管理员创建成功: {admin.username}")
        return admin
        
    except Exception as e:
        print(f"创建超级管理员失败: {e}")
        return None
    finally:
        db.close()

def create_default_providers():
    """创建默认的模型供应商"""
    db = SessionLocal()
    try:
        # OpenAI
        openai_provider = ModelProvider(
            id=str(uuid.uuid4()),
            name="openai",
            display_name="OpenAI",
            provider_type="openai",
            api_base_url="https://api.openai.com/v1",
            api_key="",  # 需要用户配置
            config={
                "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                "embedding_models": ["text-embedding-ada-002"]
            },
            is_active=True
        )
        
        # 通义千问
        qwen_provider = ModelProvider(
            id=str(uuid.uuid4()),
            name="qwen",
            display_name="阿里云通义千问",
            provider_type="qwen",
            api_base_url="https://dashscope.aliyuncs.com/api/v1",
            api_key="",  # 需要用户配置
            config={
                "models": ["qwen-turbo", "qwen-plus", "qwen-max"],
                "embedding_models": ["text-embedding-v1"]
            },
            is_active=True
        )
        
        # 检查是否已存在
        existing_openai = db.query(ModelProvider).filter(ModelProvider.name == "openai").first()
        if not existing_openai:
            db.add(openai_provider)
            print("OpenAI供应商创建成功")
        
        existing_qwen = db.query(ModelProvider).filter(ModelProvider.name == "qwen").first()
        if not existing_qwen:
            db.add(qwen_provider)
            print("通义千问供应商创建成功")
        
        db.commit()
        
    except Exception as e:
        print(f"创建默认供应商失败: {e}")
        db.rollback()
    finally:
        db.close()

def create_system_configs():
    """创建系统配置"""
    db = SessionLocal()
    try:
        configs = [
            {
                "key": "system_name",
                "value": "MetaBox智能知识库系统",
                "description": "系统名称",
                "is_encrypted": False
            },
            {
                "key": "max_file_size",
                "value": "100",
                "description": "最大文件上传大小(MB)",
                "is_encrypted": False
            },
            {
                "key": "max_concurrent_requests",
                "value": "10",
                "description": "最大并发请求数",
                "is_encrypted": False
            },
            {
                "key": "default_chunk_size",
                "value": "1000",
                "description": "默认文本分块大小",
                "is_encrypted": False
            },
            {
                "key": "vector_dimension",
                "value": "1536",
                "description": "向量维度",
                "is_encrypted": False
            }
        ]
        
        for config_data in configs:
            existing = db.query(SystemConfig).filter(SystemConfig.key == config_data["key"]).first()
            if not existing:
                config = SystemConfig(
                    id=str(uuid.uuid4()),
                    key=config_data["key"],
                    value=config_data["value"],
                    description=config_data["description"],
                    is_encrypted=config_data["is_encrypted"]
                )
                db.add(config)
                print(f"系统配置创建成功: {config_data['key']}")
        
        db.commit()
        
    except Exception as e:
        print(f"创建系统配置失败: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """主函数"""
    print("开始初始化管理员系统...")
    
    # 初始化数据库表
    print("1. 创建数据库表...")
    init_database()
    
    # 创建超级管理员
    print("2. 创建超级管理员...")
    create_super_admin()
    
    # 创建默认供应商
    print("3. 创建默认模型供应商...")
    create_default_providers()
    
    # 创建系统配置
    print("4. 创建系统配置...")
    create_system_configs()
    
    print("管理员系统初始化完成！")
    print("\n默认登录信息:")
    print("用户名: admin")
    print("密码: admin123")
    print("请及时修改默认密码！")

if __name__ == "__main__":
    main() 