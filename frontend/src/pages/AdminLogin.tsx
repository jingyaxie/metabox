import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Eye, EyeOff, Shield, Settings, Database, Brain } from 'lucide-react'

const AdminLogin: React.FC = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [particles, setParticles] = useState<Array<{x: number, y: number, vx: number, vy: number}>>([])
  
  const navigate = useNavigate()

  // 生成粒子背景
  useEffect(() => {
    const generateParticles = () => {
      const particlesArray = []
      for (let i = 0; i < 30; i++) {
        particlesArray.push({
          x: Math.random() * window.innerWidth,
          y: Math.random() * window.innerHeight,
          vx: (Math.random() - 0.5) * 0.3,
          vy: (Math.random() - 0.5) * 0.3
        })
      }
      setParticles(particlesArray)
    }

    generateParticles()
    const interval = setInterval(() => {
      setParticles(prev => prev.map(particle => {
        const newX = particle.x + particle.vx
        const newY = particle.y + particle.vy
        return {
          ...particle,
          x: newX > window.innerWidth ? 0 : newX < 0 ? window.innerWidth : newX,
          y: newY > window.innerHeight ? 0 : newY < 0 ? window.innerHeight : newY
        }
      }))
    }, 50)

    return () => clearInterval(interval)
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/v1/admin/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      const data = await response.json()

      if (response.ok && data.success) {
        // 保存管理员token
        localStorage.setItem('admin_token', data.data.token)
        localStorage.setItem('admin_user', JSON.stringify({
          username: formData.username,
          role: 'super_admin'
        }))
        
        navigate('/admin/dashboard')
      } else {
        setError(data.message || '登录失败')
      }
    } catch (err: any) {
      setError('网络错误，请检查连接')
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleDemoLogin = () => {
    setFormData({
      username: 'admin',
      password: 'admin123'
    })
  }

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* 粒子背景 */}
      <div className="absolute inset-0">
        {particles.map((particle, index) => (
          <div
            key={index}
            className="absolute w-1 h-1 bg-purple-400 rounded-full opacity-40"
            style={{
              left: particle.x,
              top: particle.y,
              animation: 'pulse 3s infinite'
            }}
          />
        ))}
      </div>

      {/* 网格背景 */}
      <div className="absolute inset-0 opacity-10" style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='1'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
      }} />

      {/* 主要内容 */}
      <div className="relative z-10 min-h-screen flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          {/* Logo和标题 */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-r from-purple-500 to-red-600 rounded-3xl mb-6 shadow-2xl">
              <Shield className="w-12 h-12 text-white" />
            </div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-400 to-red-400 bg-clip-text text-transparent mb-3">
              超级管理员
            </h1>
            <p className="text-slate-300 text-xl font-medium">
              系统管理控制台
            </p>
            <p className="text-slate-400 text-sm mt-2">
              模型配置 · 系统管理 · 权限控制
            </p>
          </div>

          {/* 登录卡片 */}
          <Card className="bg-slate-800/60 backdrop-blur-xl border-slate-700 shadow-2xl">
            <CardHeader className="text-center pb-4">
              <CardTitle className="text-2xl font-bold text-white">
                管理员登录
              </CardTitle>
              <p className="text-slate-400">
                请输入超级管理员凭据
              </p>
            </CardHeader>
            <CardContent className="space-y-6">
              {error && (
                <Alert variant="destructive" className="bg-red-900/50 border-red-700">
                  <AlertDescription className="text-red-200">
                    {error}
                  </AlertDescription>
                </Alert>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="username" className="text-slate-300">
                    管理员用户名
                  </Label>
                  <div className="relative">
                    <Input
                      id="username"
                      name="username"
                      type="text"
                      required
                      className="bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-400 focus:border-purple-500 focus:ring-purple-500"
                      value={formData.username}
                      onChange={handleInputChange}
                      placeholder="请输入管理员用户名"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password" className="text-slate-300">
                    管理员密码
                  </Label>
                  <div className="relative">
                    <Input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      required
                      className="bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-400 focus:border-purple-500 focus:ring-purple-500 pr-10"
                      value={formData.password}
                      onChange={handleInputChange}
                      placeholder="请输入管理员密码"
                    />
                    <button
                      type="button"
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-300"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                <div className="space-y-3 pt-2">
                  <Button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-purple-600 to-red-600 hover:from-purple-700 hover:to-red-700 text-white font-medium py-3 rounded-lg transition-all duration-200 transform hover:scale-105 disabled:opacity-50 disabled:transform-none"
                  >
                    {loading ? (
                      <div className="flex items-center">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        登录中...
                      </div>
                    ) : (
                      <div className="flex items-center">
                        <Shield className="w-4 h-4 mr-2" />
                        管理员登录
                      </div>
                    )}
                  </Button>

                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleDemoLogin}
                    className="w-full border-slate-600 text-slate-300 hover:bg-slate-700 hover:text-white"
                  >
                    使用演示账号
                  </Button>
                </div>
              </form>

              <div className="text-center pt-4 border-t border-slate-700">
                <button 
                  onClick={() => navigate('/login')}
                  className="text-purple-400 hover:text-purple-300 transition-colors duration-200"
                >
                  返回普通用户登录
                </button>
              </div>
            </CardContent>
          </Card>

          {/* 功能展示 */}
          <div className="mt-8 grid grid-cols-3 gap-4 text-center">
            <div className="p-4 rounded-lg bg-slate-800/30 backdrop-blur-sm border border-slate-700">
              <Settings className="w-6 h-6 text-purple-400 mx-auto mb-2" />
              <p className="text-xs text-slate-400">系统配置</p>
            </div>
            <div className="p-4 rounded-lg bg-slate-800/30 backdrop-blur-sm border border-slate-700">
              <Database className="w-6 h-6 text-red-400 mx-auto mb-2" />
              <p className="text-xs text-slate-400">模型管理</p>
            </div>
            <div className="p-4 rounded-lg bg-slate-800/30 backdrop-blur-sm border border-slate-700">
              <Brain className="w-6 h-6 text-blue-400 mx-auto mb-2" />
              <p className="text-xs text-slate-400">AI配置</p>
            </div>
          </div>
        </div>
      </div>

      {/* 动画样式 */}
      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes pulse {
            0%, 100% { opacity: 0.4; }
            50% { opacity: 0.8; }
          }
        `
      }} />
    </div>
  )
}

export default AdminLogin 