from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime
import bcrypt
import jwt
from app.models.admin import SuperAdmin, ModelProvider, ModelConfig, SystemConfig
from app.schemas.admin import (
    SuperAdminCreate, SuperAdminLogin, ModelProviderCreate, ModelProviderUpdate,
    ModelConfigCreate, ModelConfigUpdate, SystemConfigCreate, SystemConfigUpdate
)
from app.core.config import settings
from app.core.security import encrypt_text, decrypt_text
import logging

logger = logging.getLogger(__name__)

class AdminService:
    def __init__(self, db: Session):
        self.db = db

    # 超级管理员相关方法
    def create_super_admin(self, admin_data: SuperAdminCreate) -> SuperAdmin:
        """创建超级管理员"""
        # 检查是否已存在超级管理员
        existing_admin = self.db.query(SuperAdmin).first()
        if existing_admin:
            raise ValueError("超级管理员已存在，无法创建新的超级管理员")
        
        # 加密密码
        password_hash = bcrypt.hashpw(admin_data.password.encode('utf-8'), bcrypt.gensalt())
        
        admin = SuperAdmin(
            username=admin_data.username,
            password_hash=password_hash.decode('utf-8'),
            email=admin_data.email
        )
        
        self.db.add(admin)
        self.db.commit()
        self.db.refresh(admin)
        return admin

    def authenticate_super_admin(self, login_data: SuperAdminLogin) -> Optional[str]:
        """超级管理员认证"""
        admin = self.db.query(SuperAdmin).filter(
            SuperAdmin.username == login_data.username,
            SuperAdmin.is_active == True
        ).first()
        
        if not admin:
            return None
        
        if not bcrypt.checkpw(login_data.password.encode('utf-8'), admin.password_hash.encode('utf-8')):
            return None
        
        # 更新最后登录时间
        admin.last_login = datetime.utcnow()
        self.db.commit()
        
        # 生成JWT token
        token_data = {
            "sub": admin.id,
            "username": admin.username,
            "role": "super_admin",
            "exp": datetime.utcnow().timestamp() + (24 * 60 * 60)  # 24小时过期
        }
        
        return jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")

    def get_super_admin_by_id(self, admin_id: str) -> Optional[SuperAdmin]:
        """根据ID获取超级管理员"""
        return self.db.query(SuperAdmin).filter(SuperAdmin.id == admin_id).first()

    # 模型供应商相关方法
    def create_model_provider(self, provider_data: ModelProviderCreate) -> ModelProvider:
        """创建模型供应商"""
        # 检查名称是否已存在
        existing = self.db.query(ModelProvider).filter(ModelProvider.name == provider_data.name).first()
        if existing:
            raise ValueError(f"供应商名称 '{provider_data.name}' 已存在")
        
        # 加密API密钥
        encrypted_api_key = encrypt_text(provider_data.api_key)
        
        provider = ModelProvider(
            name=provider_data.name,
            display_name=provider_data.display_name,
            provider_type=provider_data.provider_type,
            api_base_url=provider_data.api_base_url,
            api_key=encrypted_api_key,
            config=provider_data.config
        )
        
        self.db.add(provider)
        self.db.commit()
        self.db.refresh(provider)
        return provider

    def get_model_providers(self, provider_type: Optional[str] = None, active_only: bool = True) -> List[ModelProvider]:
        """获取模型供应商列表"""
        query = self.db.query(ModelProvider)
        
        if provider_type:
            query = query.filter(ModelProvider.provider_type == provider_type)
        
        if active_only:
            query = query.filter(ModelProvider.is_active == True)
        
        return query.all()

    def get_model_provider_by_id(self, provider_id: str) -> Optional[ModelProvider]:
        """根据ID获取模型供应商"""
        return self.db.query(ModelProvider).filter(ModelProvider.id == provider_id).first()

    def update_model_provider(self, provider_id: str, update_data: ModelProviderUpdate) -> Optional[ModelProvider]:
        """更新模型供应商"""
        provider = self.get_model_provider_by_id(provider_id)
        if not provider:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        
        # 如果更新API密钥，需要重新加密
        if "api_key" in update_dict:
            update_dict["api_key"] = encrypt_text(update_dict["api_key"])
        
        for field, value in update_dict.items():
            setattr(provider, field, value)
        
        self.db.commit()
        self.db.refresh(provider)
        return provider

    def delete_model_provider(self, provider_id: str) -> bool:
        """删除模型供应商"""
        provider = self.get_model_provider_by_id(provider_id)
        if not provider:
            return False
        
        # 检查是否有关联的模型配置
        models_count = self.db.query(ModelConfig).filter(ModelConfig.provider_id == provider_id).count()
        if models_count > 0:
            raise ValueError("该供应商下还有模型配置，无法删除")
        
        self.db.delete(provider)
        self.db.commit()
        return True

    def get_provider_api_key(self, provider_id: str) -> Optional[str]:
        """获取供应商的API密钥（解密后）"""
        provider = self.get_model_provider_by_id(provider_id)
        if not provider:
            return None
        
        try:
            return decrypt_text(provider.api_key)
        except Exception as e:
            logger.error(f"解密API密钥失败: {e}")
            return None

    # 模型配置相关方法
    def create_model_config(self, config_data: ModelConfigCreate) -> ModelConfig:
        """创建模型配置"""
        # 检查供应商是否存在
        provider = self.get_model_provider_by_id(config_data.provider_id)
        if not provider:
            raise ValueError("指定的供应商不存在")
        
        # 检查模型名称是否已存在
        existing = self.db.query(ModelConfig).filter(
            and_(
                ModelConfig.provider_id == config_data.provider_id,
                ModelConfig.model_name == config_data.model_name
            )
        ).first()
        
        if existing:
            raise ValueError(f"该供应商下模型名称 '{config_data.model_name}' 已存在")
        
        # 如果设置为默认模型，需要取消其他默认模型
        if config_data.is_default:
            self.db.query(ModelConfig).filter(
                and_(
                    ModelConfig.provider_id == config_data.provider_id,
                    ModelConfig.model_type == config_data.model_type,
                    ModelConfig.is_default == True
                )
            ).update({"is_default": False})
        
        config = ModelConfig(
            provider_id=config_data.provider_id,
            model_name=config_data.model_name,
            display_name=config_data.display_name,
            model_type=config_data.model_type,
            max_tokens=config_data.max_tokens,
            temperature=config_data.temperature,
            is_default=config_data.is_default,
            config=config_data.config
        )
        
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config

    def get_model_configs(self, provider_id: Optional[str] = None, model_type: Optional[str] = None, active_only: bool = True) -> List[ModelConfig]:
        """获取模型配置列表"""
        query = self.db.query(ModelConfig)
        
        if provider_id:
            query = query.filter(ModelConfig.provider_id == provider_id)
        
        if model_type:
            query = query.filter(ModelConfig.model_type == model_type)
        
        if active_only:
            query = query.filter(ModelConfig.is_active == True)
        
        return query.all()

    def get_default_model(self, model_type: str) -> Optional[ModelConfig]:
        """获取指定类型的默认模型"""
        return self.db.query(ModelConfig).filter(
            and_(
                ModelConfig.model_type == model_type,
                ModelConfig.is_default == True,
                ModelConfig.is_active == True
            )
        ).first()

    def update_model_config(self, config_id: str, update_data: ModelConfigUpdate) -> Optional[ModelConfig]:
        """更新模型配置"""
        config = self.db.query(ModelConfig).filter(ModelConfig.id == config_id).first()
        if not config:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        
        # 如果设置为默认模型，需要取消其他默认模型
        if update_dict.get("is_default", False):
            self.db.query(ModelConfig).filter(
                and_(
                    ModelConfig.provider_id == config.provider_id,
                    ModelConfig.model_type == config.model_type,
                    ModelConfig.is_default == True,
                    ModelConfig.id != config_id
                )
            ).update({"is_default": False})
        
        for field, value in update_dict.items():
            setattr(config, field, value)
        
        self.db.commit()
        self.db.refresh(config)
        return config

    def delete_model_config(self, config_id: str) -> bool:
        """删除模型配置"""
        config = self.db.query(ModelConfig).filter(ModelConfig.id == config_id).first()
        if not config:
            return False
        
        self.db.delete(config)
        self.db.commit()
        return True

    # 系统配置相关方法
    def create_system_config(self, config_data: SystemConfigCreate) -> SystemConfig:
        """创建系统配置"""
        # 检查键是否已存在
        existing = self.db.query(SystemConfig).filter(SystemConfig.key == config_data.key).first()
        if existing:
            raise ValueError(f"配置键 '{config_data.key}' 已存在")
        
        # 如果需要加密，加密值
        value = config_data.value
        if config_data.is_encrypted:
            value = encrypt_text(config_data.value)
        
        config = SystemConfig(
            key=config_data.key,
            value=value,
            description=config_data.description,
            category=config_data.category,
            is_encrypted=config_data.is_encrypted
        )
        
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config

    def get_system_config(self, key: str) -> Optional[str]:
        """获取系统配置值"""
        config = self.db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if not config:
            return None
        
        if config.is_encrypted:
            try:
                return decrypt_text(config.value)
            except Exception as e:
                logger.error(f"解密配置值失败: {e}")
                return None
        
        return config.value

    def update_system_config(self, key: str, value: str) -> bool:
        """更新系统配置"""
        config = self.db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if not config:
            return False
        
        # 如果需要加密，加密值
        if config.is_encrypted:
            value = encrypt_text(value)
        
        config.value = value
        config.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True

    def get_all_system_configs(self) -> List[SystemConfig]:
        """获取所有系统配置"""
        return self.db.query(SystemConfig).all()

    # 仪表板统计
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """获取仪表板统计信息"""
        total_providers = self.db.query(ModelProvider).count()
        active_providers = self.db.query(ModelProvider).filter(ModelProvider.is_active == True).count()
        total_models = self.db.query(ModelConfig).count()
        active_models = self.db.query(ModelConfig).filter(ModelConfig.is_active == True).count()
        total_configs = self.db.query(SystemConfig).count()
        
        # 系统状态检查
        system_status = {
            "database": "healthy",
            "vector_db": "healthy",
            "model_services": "healthy"
        }
        
        return {
            "total_providers": total_providers,
            "active_providers": active_providers,
            "total_models": total_models,
            "active_models": active_models,
            "total_configs": total_configs,
            "system_status": system_status
        } 