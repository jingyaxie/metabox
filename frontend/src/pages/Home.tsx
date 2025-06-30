import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const Home: React.FC = () => {
  const { isAuthenticated } = useAuth()

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          欢迎使用 MetaBox
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          本地私有化部署的智能知识库系统
        </p>
        
        <div className="flex justify-center space-x-4">
          {isAuthenticated ? (
            <Link to="/dashboard" className="btn-primary">
              进入系统
            </Link>
          ) : (
            <>
              <Link to="/login" className="btn-primary">
                立即登录
              </Link>
              <Link to="/register" className="btn-secondary">
                免费注册
              </Link>
            </>
          )}
        </div>
      </div>
      
      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="card text-center">
          <div className="text-3xl mb-4">🧠</div>
          <h3 className="text-lg font-semibold mb-2">智能检索</h3>
          <p className="text-gray-600">
            支持 RAG + 多模态检索与问答
          </p>
        </div>
        
        <div className="card text-center">
          <div className="text-3xl mb-4">🖼️</div>
          <h3 className="text-lg font-semibold mb-2">多模态支持</h3>
          <p className="text-gray-600">
            文本和图片向量库，统一多模态搜索
          </p>
        </div>
        
        <div className="card text-center">
          <div className="text-3xl mb-4">🔒</div>
          <h3 className="text-lg font-semibold mb-2">私有部署</h3>
          <p className="text-gray-600">
            本地私有化部署，数据安全可控
          </p>
        </div>
      </div>
    </div>
  )
}

export default Home 