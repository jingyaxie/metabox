#!/usr/bin/env python3
"""
管理员功能测试脚本
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_admin_login():
    """测试管理员登录"""
    print("测试管理员登录...")
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 200:
            token = response.json()["data"]["token"]
            return token
        else:
            print("登录失败")
            return None
            
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def test_dashboard_stats(token):
    """测试仪表板统计"""
    print("\n测试仪表板统计...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/admin/dashboard",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
    except Exception as e:
        print(f"请求失败: {e}")

def test_model_providers(token):
    """测试模型供应商列表"""
    print("\n测试模型供应商列表...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/admin/model-providers",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
    except Exception as e:
        print(f"请求失败: {e}")

def test_system_configs(token):
    """测试系统配置列表"""
    print("\n测试系统配置列表...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/admin/system-configs",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
    except Exception as e:
        print(f"请求失败: {e}")

def main():
    """主函数"""
    print("开始测试管理员功能...")
    
    # 测试登录
    token = test_admin_login()
    
    if token:
        # 测试仪表板
        test_dashboard_stats(token)
        
        # 测试模型供应商
        test_model_providers(token)
        
        # 测试系统配置
        test_system_configs(token)
        
        print("\n测试完成！")
    else:
        print("登录失败，无法继续测试")

if __name__ == "__main__":
    main() 