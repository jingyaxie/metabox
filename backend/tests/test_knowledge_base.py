import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def admin_token():
    # 使用默认管理员登录获取token
    resp = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]

def auth_header(token):
    return {"Authorization": f"Bearer {token}"}

def test_create_knowledge_base(admin_token):
    resp = client.post(
        "/api/kb/",
        params={"name": "测试知识库", "description": "单元测试", "kb_type": "text"},
        headers=auth_header(admin_token)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "测试知识库"
    assert data["description"] == "单元测试"
    global kb_id
    kb_id = data["id"]

def test_get_knowledge_bases(admin_token):
    resp = client.get("/api/kb/", headers=auth_header(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(kb["name"] == "测试知识库" for kb in data)

def test_get_knowledge_base_detail(admin_token):
    resp = client.get(f"/api/kb/{kb_id}", headers=auth_header(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == kb_id
    assert data["name"] == "测试知识库"

def test_delete_knowledge_base(admin_token):
    resp = client.delete(f"/api/kb/{kb_id}", headers=auth_header(admin_token))
    assert resp.status_code == 200
    assert resp.json()["message"] == "知识库删除成功" 