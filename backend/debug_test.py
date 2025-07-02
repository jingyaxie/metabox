#!/usr/bin/env python3
"""
调试测试脚本
"""
import uuid
from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models.user import User
from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.api_key_service import ApiKeyService

# 创建数据库会话
Session = sessionmaker(bind=engine)
db = Session()

try:
    # 测试用户查询
    print("=== 测试用户查询 ===")
    users = db.query(User).all()
    print(f"用户数量: {len(users)}")
    for user in users:
        print(f"用户ID: {user.id}, 用户名: {user.username}")
    
    if users:
        test_user = users[0]
        print(f"测试用户ID: {test_user.id}")
        print(f"测试用户ID类型: {type(test_user.id)}")
        
        # 测试知识库服务
        print("\n=== 测试知识库服务 ===")
        kb_service = KnowledgeBaseService(db)
        try:
            kb_list = kb_service.get_user_knowledge_bases(str(test_user.id))
            print(f"知识库数量: {len(kb_list)}")
        except Exception as e:
            print(f"知识库服务错误: {e}")
            import traceback
            traceback.print_exc()
        
        # 测试API密钥服务
        print("\n=== 测试API密钥服务 ===")
        try:
            api_key_service = ApiKeyService(db)
            api_keys = api_key_service.get_api_keys_by_user(str(test_user.id))
            print(f"API密钥数量: {len(api_keys)}")
        except Exception as e:
            print(f"API密钥服务错误: {e}")
            import traceback
            traceback.print_exc()

except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()

finally:
    db.close() 