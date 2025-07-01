import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Copy, Plus, Trash2, Edit, Eye, EyeOff } from 'lucide-react';
import { toast } from 'sonner';

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
      toast.error('获取API密钥列表失败');
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
        toast.success('API密钥创建成功');
      } else {
        toast.error('创建API密钥失败');
      }
    } catch (error) {
      toast.error('创建API密钥失败');
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
        toast.success('API密钥删除成功');
      } else {
        toast.error('删除API密钥失败');
      }
    } catch (error) {
      toast.error('删除API密钥失败');
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('已复制到剪贴板');
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
            <CardDescription>
              创建一个新的API密钥用于外部系统调用
            </CardDescription>
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
                <Label htmlFor="quota_monthly">每月配额</Label>
                <Input
                  id="quota_monthly"
                  type="number"
                  value={newApiKey.permissions.quota_monthly}
                  onChange={(e) => setNewApiKey({
                    ...newApiKey, 
                    permissions: {...newApiKey.permissions, quota_monthly: parseInt(e.target.value)}
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
        <Alert className="mb-6">
          <AlertDescription>
            <div className="flex items-center justify-between">
              <span>API密钥创建成功！请保存以下密钥，创建后将无法再次查看完整密钥。</span>
              <div className="flex gap-2">
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
            </div>
            {showKey && (
              <div className="mt-2 p-2 bg-gray-100 rounded font-mono text-sm break-all">
                {createdKey}
              </div>
            )}
          </AlertDescription>
        </Alert>
      )}

      <div className="grid gap-4">
        {apiKeys.map((apiKey) => (
          <Card key={apiKey.id}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    {apiKey.app_name}
                    {getStatusBadge(apiKey.status)}
                  </CardTitle>
                  <CardDescription>
                    应用ID: {apiKey.app_id} | 密钥前缀: {apiKey.key_prefix}
                  </CardDescription>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => deleteApiKey(apiKey.id)}
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="font-medium">创建时间:</span>
                  <div>{formatDate(apiKey.created_at)}</div>
                </div>
                <div>
                  <span className="font-medium">总调用次数:</span>
                  <div>{apiKey.total_calls.toLocaleString()}</div>
                </div>
                <div>
                  <span className="font-medium">总Token消耗:</span>
                  <div>{apiKey.total_tokens.toLocaleString()}</div>
                </div>
                <div>
                  <span className="font-medium">最后使用:</span>
                  <div>{apiKey.last_used_at ? formatDate(apiKey.last_used_at) : '从未使用'}</div>
                </div>
              </div>
              {apiKey.expires_at && (
                <div className="mt-2 text-sm">
                  <span className="font-medium">过期时间:</span> {formatDate(apiKey.expires_at)}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {apiKeys.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <p className="text-gray-500 mb-4">暂无API密钥</p>
            <Button onClick={() => setShowCreateForm(true)}>
              <Plus className="w-4 h-4 mr-2" />
              创建第一个API密钥
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 