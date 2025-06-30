import React from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const Layout: React.FC = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const isActive = (path: string) => {
    return location.pathname.startsWith(path)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 导航栏 */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-xl font-bold text-primary-600">MetaBox</h1>
              </div>
              
              <div className="ml-10 flex items-baseline space-x-4">
                <button
                  onClick={() => navigate('/dashboard')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    isActive('/dashboard')
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  仪表盘
                </button>
                
                <button
                  onClick={() => navigate('/kb')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    isActive('/kb')
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  知识库
                </button>
                
                <button
                  onClick={() => navigate('/chat')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    isActive('/chat')
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  聊天
                </button>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-700">{user?.username}</span>
                <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-medium">
                    {user?.username?.charAt(0).toUpperCase()}
                  </span>
                </div>
              </div>
              
              <div className="relative">
                <button
                  onClick={() => navigate('/settings')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    isActive('/settings')
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  设置
                </button>
              </div>
              
              <button
                onClick={handleLogout}
                className="px-3 py-2 rounded-md text-sm font-medium text-gray-500 hover:text-gray-700 hover:bg-gray-100"
              >
                退出
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* 主内容区域 */}
      <main>
        <Outlet />
      </main>
    </div>
  )
}

export default Layout 