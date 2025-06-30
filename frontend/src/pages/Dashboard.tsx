import React from 'react'

const Dashboard: React.FC = () => {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">仪表板</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-2">知识库</h3>
          <p className="text-3xl font-bold text-primary-600">0</p>
          <p className="text-gray-600">个知识库</p>
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold mb-2">文档</h3>
          <p className="text-3xl font-bold text-primary-600">0</p>
          <p className="text-gray-600">个文档</p>
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold mb-2">聊天</h3>
          <p className="text-3xl font-bold text-primary-600">0</p>
          <p className="text-gray-600">次对话</p>
        </div>
      </div>
    </div>
  )
}

export default Dashboard 