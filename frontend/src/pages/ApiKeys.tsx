import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Copy, Plus, Trash2, Eye, EyeOff } from 'lucide-react';
import { Label } from '@/components/ui/label';

interface ApiKey {
  id: string;
  app_id: string;
  app_name: string;
  key_prefix: string;
  permissions: any;
  status: string;
  created_at: string;
  expires_at?: string;
  last_used_at?: string;
  total_calls: number;
  total_tokens: number;
}

interface ApiKeyCreate {
  app_id: string;
  app_name: string;
  permissions: {
    operations: string[];
    kb_ids: string[];
    rate_limit: number;
    quota_daily: number;
    quota_monthly: number;
    max_tokens: number;
  };
  expires_at?: string;
}

export default function ApiKeys() {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newApiKey, setNewApiKey] = useState<ApiKeyCreate>({
    app_id: '',
    app_name: '',
    permissions: {
      operations: ['query', 'search', 'read'],
      kb_ids: [],
      rate_limit: 1000,
      quota_daily: 10000,
      quota_monthly: 300000,
      max_tokens: 4000
    }
  });
  const [createdKey, setCreatedKey] = useState<string>('');
  const [showKey, setShowKey] = useState(false);

  useEffect(() => {
    fetchApiKeys();
  }, []);

  const fetchApiKeys = async () => {
    try {
      const response = await fetch('/api/v1/api-keys');
      if (response.ok) {
        const data = await response.json();
        setApiKeys(data.api_keys || []);
      }
    } catch (error) {
      alert('获取API密钥列表失败');
    } finally {
      setLoading(false);
    }
  };

  const createApiKey = async () => {
    try {
      const response = await fetch('/api/v1/api-keys', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newApiKey),
      });

      if (response.ok) {
        const data = await response.json();
        setCreatedKey(data.data.api_key);
        setShowCreateForm(false);
        setNewApiKey({
          app_id: '',
          app_name: '',
          permissions: {
            operations: ['query', 'search', 'read'],
            kb_ids: [],
            rate_limit: 1000,
            quota_daily: 10000,
            quota_monthly: 300000,
            max_tokens: 4000
          }
        });
        fetchApiKeys();
        alert('API密钥创建成功');
      } else {
        alert('创建API密钥失败');
      }
    } catch (error) {
      alert('创建API密钥失败');
    }
  };

  const deleteApiKey = async (id: string) => {
    if (!confirm('确定要删除这个API密钥吗？')) return;

    try {
      const response = await fetch(`/api/v1/api-keys/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        fetchApiKeys();
        alert('API密钥删除成功');
      } else {
        alert('删除API密钥失败');
      }
    } catch (error) {
      alert('删除API密钥失败');
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert('已复制到剪贴板');
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('zh-CN');
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge variant="default">活跃</Badge>;
      case 'inactive':
        return <Badge variant="secondary">停用</Badge>;
      case 'expired':
        return <Badge variant="destructive">过期</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">加载中...</div>;
  }

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">API密钥管理</h1>
        <Button onClick={() => setShowCreateForm(true)}>
          <Plus className="w-4 h-4 mr-2" />
          创建API密钥
        </Button>
      </div>

      {showCreateForm && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>创建新的API密钥</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="app_id">应用ID</Label>
                <Input
                  id="app_id"
                  value={newApiKey.app_id}
                  onChange={(e) => setNewApiKey({...newApiKey, app_id: e.target.value})}
                  placeholder="my_app"
                />
              </div>
              <div>
                <Label htmlFor="app_name">应用名称</Label>
                <Input
                  id="app_name"
                  value={newApiKey.app_name}
                  onChange={(e) => setNewApiKey({...newApiKey, app_name: e.target.value})}
                  placeholder="我的应用"
                />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4 mt-4">
              <div>
                <Label htmlFor="rate_limit">每分钟限制</Label>
                <Input
                  id="rate_limit"
                  type="number"
                  value={newApiKey.permissions.rate_limit}
                  onChange={(e) => setNewApiKey({
                    ...newApiKey, 
                    permissions: {...newApiKey.permissions, rate_limit: parseInt(e.target.value)}
                  })}
                />
              </div>
              <div>
                <Label htmlFor="quota_daily">每日配额</Label>
                <Input
                  id="quota_daily"
                  type="number"
                  value={newApiKey.permissions.quota_daily}
                  onChange={(e) => setNewApiKey({
                    ...newApiKey, 
                    permissions: {...newApiKey.permissions, quota_daily: parseInt(e.target.value)}
                  })}
                />
              </div>
              <div>
                <Label htmlFor="max_tokens">最大Token数</Label>
                <Input
                  id="max_tokens"
                  type="number"
                  value={newApiKey.permissions.max_tokens}
                  onChange={(e) => setNewApiKey({
                    ...newApiKey, 
                    permissions: {...newApiKey.permissions, max_tokens: parseInt(e.target.value)}
                  })}
                />
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <Button onClick={createApiKey}>创建</Button>
              <Button variant="outline" onClick={() => setShowCreateForm(false)}>取消</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {createdKey && (
        <Card className="mb-6 border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="text-green-800">API密钥创建成功</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Input
                value={showKey ? createdKey : '••••••••••••••••••••••••••••••••'}
                readOnly
                className="font-mono"
              />
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowKey(!showKey)}
              >
                {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => copyToClipboard(createdKey)}
              >
                <Copy className="w-4 h-4" />
              </Button>
            </div>
            <p className="text-sm text-green-600 mt-2">
              请保存好这个密钥，它只会显示一次
            </p>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4">
        {apiKeys.map((apiKey) => (
          <Card key={apiKey.id}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-lg">{apiKey.app_name}</CardTitle>
                  <p className="text-sm text-gray-500">ID: {apiKey.app_id}</p>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusBadge(apiKey.status)}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => deleteApiKey(apiKey.id)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-gray-500">密钥前缀</p>
                  <p className="font-mono">{apiKey.key_prefix}</p>
                </div>
                <div>
                  <p className="text-gray-500">创建时间</p>
                  <p>{formatDate(apiKey.created_at)}</p>
                </div>
                <div>
                  <p className="text-gray-500">总调用次数</p>
                  <p>{apiKey.total_calls.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-gray-500">总Token数</p>
                  <p>{apiKey.total_tokens.toLocaleString()}</p>
                </div>
              </div>
              {apiKey.last_used_at && (
                <div className="mt-2 text-sm">
                  <p className="text-gray-500">最后使用时间</p>
                  <p>{formatDate(apiKey.last_used_at)}</p>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {apiKeys.length === 0 && !loading && (
        <Card>
          <CardContent className="text-center py-8">
            <p className="text-gray-500">暂无API密钥</p>
            <Button onClick={() => setShowCreateForm(true)} className="mt-2">
              <Plus className="w-4 h-4 mr-2" />
              创建第一个API密钥
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 