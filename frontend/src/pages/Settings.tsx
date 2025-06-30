import React, { useState, useEffect } from 'react'
import apiClient from '../services/api'

interface User {
  id: string
  username: string
  email: string
  created_at: string
}

const Settings: React.FC = () => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState<'success' | 'error'>('success')
  
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })

  useEffect(() => {
    fetchUserProfile()
  }, [])

  const fetchUserProfile = async () => {
    try {
      const res = await apiClient.get('/auth/profile')
      setUser(res.data)
      setFormData(prev => ({
        ...prev,
        username: res.data.username,
        email: res.data.email
      }))
    } catch (error) {
      console.error('获取用户信息失败:', error)
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

  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setMessage('')

    try {
      await apiClient.put('/auth/profile', {
        username: formData.username,
        email: formData.email
      })
      
      setMessage('个人信息更新成功')
      setMessageType('success')
      fetchUserProfile()
    } catch (error: any) {
      setMessage(error.response?.data?.message || '更新失败，请重试')
      setMessageType('error')
    } finally {
      setSaving(false)
    }
  }

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (formData.newPassword !== formData.confirmPassword) {
      setMessage('新密码与确认密码不匹配')
      setMessageType('error')
      return
    }

    if (formData.newPassword.length < 6) {
      setMessage('新密码长度至少6位')
      setMessageType('error')
      return
    }

    setSaving(true)
    setMessage('')

    try {
      await apiClient.put('/auth/password', {
        current_password: formData.currentPassword,
        new_password: formData.newPassword
      })
      
      setMessage('密码修改成功')
      setMessageType('success')
      setFormData(prev => ({
        ...prev,
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }))
    } catch (error: any) {
      setMessage(error.response?.data?.message || '密码修改失败，请重试')
      setMessageType('error')
    } finally {
      setSaving(false)
    }
  }

  const handleLogout = async () => {
    try {
      await apiClient.post('/auth/logout')
      localStorage.removeItem('token')
      window.location.href = '/login'
    } catch (error) {
      console.error('退出登录失败:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">设置</h1>
          <p className="text-gray-600 mt-2">管理您的账户信息和系统设置</p>
        </div>

        {message && (
          <div className={`mb-6 p-4 rounded-lg ${
            messageType === 'success' 
              ? 'bg-green-50 border border-green-200 text-green-700'
              : 'bg-red-50 border border-red-200 text-red-700'
          }`}>
            {message}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 个人信息 */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-6">个人信息</h2>
            <form onSubmit={handleProfileUpdate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  用户名
                </label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  className="input-field w-full"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  邮箱
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="input-field w-full"
                  required
                />
              </div>

              <div className="pt-4">
                <button
                  type="submit"
                  disabled={saving}
                  className="btn-primary w-full"
                >
                  {saving ? '保存中...' : '保存更改'}
                </button>
              </div>
            </form>
          </div>

          {/* 修改密码 */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-6">修改密码</h2>
            <form onSubmit={handlePasswordChange} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  当前密码
                </label>
                <input
                  type="password"
                  name="currentPassword"
                  value={formData.currentPassword}
                  onChange={handleInputChange}
                  className="input-field w-full"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  新密码
                </label>
                <input
                  type="password"
                  name="newPassword"
                  value={formData.newPassword}
                  onChange={handleInputChange}
                  className="input-field w-full"
                  required
                  minLength={6}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  确认新密码
                </label>
                <input
                  type="password"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  className="input-field w-full"
                  required
                />
              </div>

              <div className="pt-4">
                <button
                  type="submit"
                  disabled={saving}
                  className="btn-primary w-full"
                >
                  {saving ? '修改中...' : '修改密码'}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* 账户信息 */}
        <div className="mt-8 bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-6">账户信息</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="text-sm font-medium text-gray-500">用户ID</div>
              <div className="text-sm text-gray-900 mt-1">{user?.id}</div>
            </div>
            <div>
              <div className="text-sm font-medium text-gray-500">注册时间</div>
              <div className="text-sm text-gray-900 mt-1">
                {user?.created_at ? new Date(user.created_at).toLocaleString() : '-'}
              </div>
            </div>
          </div>
        </div>

        {/* 危险操作 */}
        <div className="mt-8 bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-red-900 mb-4">危险操作</h2>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-red-900">退出登录</div>
              <div className="text-sm text-red-700 mt-1">
                退出当前账户，需要重新登录
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="btn-danger"
            >
              退出登录
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings 