import React, { useEffect, useState } from 'react'
import apiClient from '../services/api'

interface RecallTest {
  id: string
  name: string
  description: string
  status: string
  total_queries: number
  precision: number
  recall: number
  f1_score: number
  avg_response_time: number
}

interface RecallTestCase {
  id: string
  query: string
  expected_chunks: string[]
  precision: number
  recall: number
  f1_score: number
  response_time: number
  is_correct: boolean
}

interface RecallTestPanelProps {
  kbId: string
}

const RecallTestPanel: React.FC<RecallTestPanelProps> = ({ kbId }) => {
  const [tests, setTests] = useState<RecallTest[]>([])
  const [selectedTest, setSelectedTest] = useState<RecallTest | null>(null)
  const [cases, setCases] = useState<RecallTestCase[]>([])
  const [loading, setLoading] = useState(false)
  const [running, setRunning] = useState(false)
  const [report, setReport] = useState<any>(null)
  const [showCreate, setShowCreate] = useState(false)
  const [newTestName, setNewTestName] = useState('')
  const [newTestDesc, setNewTestDesc] = useState('')

  useEffect(() => {
    fetchTests()
  }, [kbId])

  const fetchTests = async () => {
    setLoading(true)
    try {
      const res = await apiClient.get(`/kb/${kbId}/recall-tests/`)
      setTests(res.data)
    } finally {
      setLoading(false)
    }
  }

  const fetchCases = async (testId: string) => {
    setLoading(true)
    try {
      const res = await apiClient.get(`/kb/${kbId}/recall-tests/${testId}/cases`)
      setCases(res.data)
    } finally {
      setLoading(false)
    }
  }

  const handleSelectTest = (test: RecallTest) => {
    setSelectedTest(test)
    fetchCases(test.id)
    setReport(null)
  }

  const handleCreateTest = async () => {
    if (!newTestName.trim()) return
    setLoading(true)
    try {
      await apiClient.post(`/kb/${kbId}/recall-tests/`, {
        name: newTestName,
        description: newTestDesc,
        test_type: 'manual',
        config: {}
      })
      setShowCreate(false)
      setNewTestName('')
      setNewTestDesc('')
      fetchTests()
    } finally {
      setLoading(false)
    }
  }

  const handleRunTest = async () => {
    if (!selectedTest) return
    setRunning(true)
    try {
      const res = await apiClient.post(`/kb/${kbId}/recall-tests/${selectedTest.id}/run`, { test_id: selectedTest.id })
      setReport(res.data)
      fetchTests()
      fetchCases(selectedTest.id)
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">召回测试</h2>
        <button className="btn-primary" onClick={() => setShowCreate(true)}>新建测试</button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {tests.map(test => (
          <div
            key={test.id}
            className={`p-4 rounded-lg border cursor-pointer ${selectedTest?.id === test.id ? 'border-primary-500 bg-primary-50' : 'border-gray-200 hover:border-primary-300'}`}
            onClick={() => handleSelectTest(test)}
          >
            <div className="font-medium text-lg mb-1">{test.name}</div>
            <div className="text-sm text-gray-500 mb-2">{test.description}</div>
            <div className="flex space-x-4 text-xs text-gray-600">
              <div>用例数: {test.total_queries}</div>
              <div>准确率: {(test.precision * 100).toFixed(1)}%</div>
              <div>召回率: {(test.recall * 100).toFixed(1)}%</div>
              <div>F1: {(test.f1_score * 100).toFixed(1)}%</div>
              <div>平均响应: {test.avg_response_time.toFixed(1)}ms</div>
            </div>
          </div>
        ))}
      </div>
      {selectedTest && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">测试用例</h3>
            <button className="btn-primary" onClick={handleRunTest} disabled={running}>
              {running ? '运行中...' : '一键运行测试'}
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-4 py-2 text-left">查询</th>
                  <th className="px-4 py-2">准确率</th>
                  <th className="px-4 py-2">召回率</th>
                  <th className="px-4 py-2">F1</th>
                  <th className="px-4 py-2">响应(ms)</th>
                  <th className="px-4 py-2">结果</th>
                </tr>
              </thead>
              <tbody>
                {cases.map(c => (
                  <tr key={c.id} className={c.is_correct ? 'bg-green-50' : 'bg-red-50'}>
                    <td className="px-4 py-2 max-w-xs truncate" title={c.query}>{c.query}</td>
                    <td className="px-4 py-2 text-center">{(c.precision * 100).toFixed(1)}%</td>
                    <td className="px-4 py-2 text-center">{(c.recall * 100).toFixed(1)}%</td>
                    <td className="px-4 py-2 text-center">{(c.f1_score * 100).toFixed(1)}%</td>
                    <td className="px-4 py-2 text-center">{c.response_time.toFixed(1)}</td>
                    <td className="px-4 py-2 text-center">{c.is_correct ? '✔️' : '❌'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      {showCreate && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">新建召回测试</h3>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">测试名称</label>
              <input
                type="text"
                value={newTestName}
                onChange={e => setNewTestName(e.target.value)}
                className="input-field w-full"
                placeholder="请输入测试名称"
              />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">描述</label>
              <input
                type="text"
                value={newTestDesc}
                onChange={e => setNewTestDesc(e.target.value)}
                className="input-field w-full"
                placeholder="可选"
              />
            </div>
            <div className="flex justify-end space-x-3">
              <button className="btn-secondary" onClick={() => setShowCreate(false)}>取消</button>
              <button className="btn-primary" onClick={handleCreateTest}>创建</button>
            </div>
          </div>
        </div>
      )}
      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-20 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 flex items-center space-x-3">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
            <span className="text-gray-700">加载中...</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default RecallTestPanel 