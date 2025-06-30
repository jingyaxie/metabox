import React from 'react'
import { useAuth } from '../contexts/AuthContext'

const Dashboard: React.FC = () => {
  const { user } = useAuth()

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">仪表板</h1>
        <p className="text-gray-600 mt-2">欢迎回来，{user?.username}！</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-2 text-gray-900">知识库</h3>
          <p className="text-3xl font-bold text-blue-600">0</p>
          <p className="text-gray-600">个知识库</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-2 text-gray-900">文档</h3>
          <p className="text-3xl font-bold text-green-600">0</p>
          <p className="text-gray-600">个文档</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-2 text-gray-900">聊天</h3>
          <p className="text-3xl font-bold text-purple-600">0</p>
          <p className="text-gray-600">次对话</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-900">快速开始</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
            <h3 className="font-medium text-gray-900 mb-2">创建知识库</h3>
            <p className="text-gray-600 text-sm mb-3">上传文档，构建您的专属知识库</p>
            <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
              开始创建 →
            </button>
          </div>
          <div className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
            <h3 className="font-medium text-gray-900 mb-2">开始聊天</h3>
            <p className="text-gray-600 text-sm mb-3">与您的知识库进行智能对话</p>
            <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
              开始聊天 →
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard 