import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Settings, Database, Users, Activity, Shield, 
  Plus, Edit, Trash2, TestTube, Eye,
  Server, Cpu, HardDrive, Network, AlertCircle,
  CheckCircle, Clock, BarChart3
} from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'

interface DashboardStats {
  total_providers: number
  active_providers: number
  total_models: number
  active_models: number
  total_configs: number
  system_status: {
    database: string
    vector_db: string
    model_services: string
  }
}

interface ModelProvider {
  id: string
  name: string
  display_name: string
  provider_type: string
  api_base_url: string
  is_active: boolean
  created_at: string
  updated_at: string
}

interface SystemConfig {
  id: string
  key: string
  value: string
  description: string
  is_encrypted: boolean
  created_at: string
  updated_at: string
}

const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [providers, setProviders] = useState<ModelProvider[]>([])
  const [configs, setConfigs] = useState<SystemConfig[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('overview')
  
  const navigate = useNavigate()

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('admin_token')
      
      if (!token) {
        navigate('/admin/login')
        return
      }

      // 加载仪表板统计
      const statsResponse = await fetch('/api/v1/admin/dashboard', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        setStats(statsData)
      }

      // 加载模型供应商
      const providersResponse = await fetch('/api/v1/admin/model-providers', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (providersResponse.ok) {
        const providersData = await providersResponse.json()
        setProviders(providersData)
      }

      // 加载系统配置
      const configsResponse = await fetch('/api/v1/admin/system-configs', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (configsResponse.ok) {
        const configsData = await configsResponse.json()
        setConfigs(configsData)
      }

    } catch (err: any) {
      setError('加载数据失败')
      console.error('加载仪表板数据失败:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_user')
    navigate('/admin/login')
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'warning':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />
      default:
        return <Clock className="w-4 h-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-100'
      case 'warning':
        return 'text-yellow-600 bg-yellow-100'
      case 'error':
        return 'text-red-600 bg-red-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">加载中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航栏 */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Shield className="w-8 h-8 text-blue-600 mr-3" />
              <h1 className="text-xl font-bold text-gray-900">超级管理员控制台</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                欢迎，管理员
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={handleLogout}
                className="text-red-600 border-red-300 hover:bg-red-50"
              >
                退出登录
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview" className="flex items-center space-x-2">
              <BarChart3 className="w-4 h-4" />
              <span>系统概览</span>
            </TabsTrigger>
            <TabsTrigger value="providers" className="flex items-center space-x-2">
              <Database className="w-4 h-4" />
              <span>模型供应商</span>
            </TabsTrigger>
            <TabsTrigger value="configs" className="flex items-center space-x-2">
              <Settings className="w-4 h-4" />
              <span>系统配置</span>
            </TabsTrigger>
            <TabsTrigger value="users" className="flex items-center space-x-2">
              <Users className="w-4 h-4" />
              <span>用户管理</span>
            </TabsTrigger>
          </TabsList>

          {/* 系统概览 */}
          <TabsContent value="overview" className="space-y-6">
            {/* 统计卡片 */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">模型供应商</CardTitle>
                  <Database className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.total_providers || 0}</div>
                  <p className="text-xs text-muted-foreground">
                    活跃: {stats?.active_providers || 0}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">模型配置</CardTitle>
                  <Cpu className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.total_models || 0}</div>
                  <p className="text-xs text-muted-foreground">
                    活跃: {stats?.active_models || 0}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">系统配置</CardTitle>
                  <Settings className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.total_configs || 0}</div>
                  <p className="text-xs text-muted-foreground">
                    配置项总数
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">系统状态</CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(stats?.system_status.database || 'unknown')}
                    <span className="text-sm font-medium">正常</span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    所有服务运行正常
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* 系统状态详情 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Server className="w-5 h-5" />
                  <span>系统服务状态</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Database className="w-5 h-5 text-blue-500" />
                      <div>
                        <p className="font-medium">数据库</p>
                        <p className="text-sm text-gray-500">PostgreSQL</p>
                      </div>
                    </div>
                    <Badge className={getStatusColor(stats?.system_status.database || 'unknown')}>
                      {stats?.system_status.database || 'unknown'}
                    </Badge>
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <HardDrive className="w-5 h-5 text-green-500" />
                      <div>
                        <p className="font-medium">向量数据库</p>
                        <p className="text-sm text-gray-500">Qdrant</p>
                      </div>
                    </div>
                    <Badge className={getStatusColor(stats?.system_status.vector_db || 'unknown')}>
                      {stats?.system_status.vector_db || 'unknown'}
                    </Badge>
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Network className="w-5 h-5 text-purple-500" />
                      <div>
                        <p className="font-medium">模型服务</p>
                        <p className="text-sm text-gray-500">AI APIs</p>
                      </div>
                    </div>
                    <Badge className={getStatusColor(stats?.system_status.model_services || 'unknown')}>
                      {stats?.system_status.model_services || 'unknown'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* 模型供应商管理 */}
          <TabsContent value="providers" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">模型供应商管理</h2>
              <Button className="flex items-center space-x-2">
                <Plus className="w-4 h-4" />
                <span>添加供应商</span>
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {providers.map((provider) => (
                <Card key={provider.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{provider.display_name}</CardTitle>
                      <Badge variant={provider.is_active ? "default" : "secondary"}>
                        {provider.is_active ? '活跃' : '停用'}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-500">{provider.provider_type}</p>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div>
                        <p className="text-sm font-medium">API地址</p>
                        <p className="text-sm text-gray-600 truncate">{provider.api_base_url}</p>
                      </div>
                      
                      <div className="flex space-x-2">
                        <Button size="sm" variant="outline" className="flex-1">
                          <Edit className="w-3 h-3 mr-1" />
                          编辑
                        </Button>
                        <Button size="sm" variant="outline" className="flex-1">
                          <TestTube className="w-3 h-3 mr-1" />
                          测试
                        </Button>
                        <Button size="sm" variant="outline" className="text-red-600">
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* 系统配置管理 */}
          <TabsContent value="configs" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">系统配置管理</h2>
              <Button className="flex items-center space-x-2">
                <Plus className="w-4 h-4" />
                <span>添加配置</span>
              </Button>
            </div>

            <Card>
              <CardContent className="p-6">
                <div className="space-y-4">
                  {configs.map((config) => (
                    <div key={config.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3">
                          <h3 className="font-medium">{config.key}</h3>
                          {config.is_encrypted && (
                            <Badge variant="outline" className="text-xs">
                              加密
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-500 mt-1">{config.description}</p>
                        <p className="text-sm text-gray-600 mt-1">
                          {config.is_encrypted ? '••••••••' : config.value}
                        </p>
                      </div>
                      <div className="flex space-x-2">
                        <Button size="sm" variant="outline">
                          <Edit className="w-3 h-3 mr-1" />
                          编辑
                        </Button>
                        <Button size="sm" variant="outline">
                          <Eye className="w-3 h-3 mr-1" />
                          查看
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* 用户管理 */}
          <TabsContent value="users" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">用户管理</h2>
              <Button className="flex items-center space-x-2">
                <Plus className="w-4 h-4" />
                <span>添加用户</span>
              </Button>
            </div>

            <Card>
              <CardContent className="p-6">
                <div className="text-center py-8">
                  <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">用户管理功能</h3>
                  <p className="text-gray-500 mb-4">
                    用户管理功能正在开发中，将支持用户列表、权限分配、角色管理等功能。
                  </p>
                  <Button variant="outline">
                    查看开发进度
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default AdminDashboard 