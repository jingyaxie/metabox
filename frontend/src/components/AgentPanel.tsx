import React, { useState, useEffect } from 'react'
import apiClient from '../services/api'

interface AgentTask {
  id: string
  task: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  steps: AgentStep[]
  created_at: string
  completed_at?: string
}

interface AgentStep {
  id: string
  type: 'rag' | 'plugin' | 'reasoning'
  name: string
  description: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  input: any
  output: any
  error?: string
  duration?: number
}

interface Plugin {
  name: string
  description: string
  enabled: boolean
}

const AgentPanel: React.FC = () => {
  const [tasks, setTasks] = useState<AgentTask[]>([])
  const [currentTask, setCurrentTask] = useState<AgentTask | null>(null)
  const [taskInput, setTaskInput] = useState('')
  const [availablePlugins, setAvailablePlugins] = useState<Plugin[]>([])
  const [selectedPlugins, setSelectedPlugins] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // 获取可用插件
  const fetchPlugins = async () => {
    try {
      const response = await apiClient.get('/plugins/')
      setAvailablePlugins(response.data.filter((p: Plugin) => p.enabled))
    } catch (err: any) {
      console.error('获取插件失败:', err)
    }
  }

  // 创建Agent任务
  const createTask = async () => {
    if (!taskInput.trim()) {
      setError('请输入任务描述')
      return
    }

    try {
      setLoading(true)
      setError('')
      
      const response = await apiClient.post('/plugins/agent/task', {
        task: taskInput,
        available_plugins: selectedPlugins
      })
      
      const newTask = response.data.data
      setTasks(prev => [newTask, ...prev])
      setCurrentTask(newTask)
      setTaskInput('')
      
      // 开始轮询任务状态
      pollTaskStatus(newTask.id)
    } catch (err: any) {
      setError(err.response?.data?.detail || '创建任务失败')
    } finally {
      setLoading(false)
    }
  }

  // 轮询任务状态
  const pollTaskStatus = async (taskId: string) => {
    const poll = async () => {
      try {
        const response = await apiClient.get(`/plugins/agent/task/${taskId}`)
        const updatedTask = response.data.data
        
        setTasks(prev => prev.map(task => 
          task.id === taskId ? updatedTask : task
        ))
        
        if (currentTask?.id === taskId) {
          setCurrentTask(updatedTask)
        }
        
        // 如果任务还在运行，继续轮询
        if (updatedTask.status === 'running') {
          setTimeout(poll, 2000)
        }
      } catch (err) {
        console.error('轮询任务状态失败:', err)
      }
    }
    
    poll()
  }

  useEffect(() => {
    fetchPlugins()
  }, [])

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6">
        <h2 className="text-xl font-semibold mb-6">Agent 多步推理</h2>
        
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <div className="text-red-600 text-sm">{error}</div>
          </div>
        )}

        {/* 任务输入 */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            任务描述
          </label>
          <textarea
            value={taskInput}
            onChange={(e) => setTaskInput(e.target.value)}
            placeholder="描述您想要Agent完成的任务..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            rows={3}
          />
        </div>

        {/* 插件选择 */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            可用插件
          </label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {availablePlugins.map(plugin => (
              <label key={plugin.name} className="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedPlugins.includes(plugin.name)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedPlugins(prev => [...prev, plugin.name])
                    } else {
                      setSelectedPlugins(prev => prev.filter(p => p !== plugin.name))
                    }
                  }}
                  className="mr-3"
                />
                <div>
                  <div className="font-medium text-sm">{plugin.name}</div>
                  <div className="text-xs text-gray-500">{plugin.description}</div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* 执行按钮 */}
        <div className="mb-6">
          <button
            onClick={createTask}
            disabled={loading || !taskInput.trim()}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? '创建中...' : '开始执行'}
          </button>
        </div>

        {/* 任务列表 */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium">任务历史</h3>
          {tasks.map(task => (
            <div
              key={task.id}
              className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                currentTask?.id === task.id
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setCurrentTask(task)}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="font-medium">{task.task}</div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  task.status === 'completed' ? 'bg-green-100 text-green-800' :
                  task.status === 'running' ? 'bg-blue-100 text-blue-800' :
                  task.status === 'failed' ? 'bg-red-100 text-red-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {task.status === 'completed' ? '已完成' :
                   task.status === 'running' ? '执行中' :
                   task.status === 'failed' ? '失败' : '等待中'}
                </span>
              </div>
              <div className="text-sm text-gray-500">
                {new Date(task.created_at).toLocaleString()}
              </div>
            </div>
          ))}
        </div>

        {/* 当前任务详情 */}
        {currentTask && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-medium mb-4">执行详情</h3>
            <div className="space-y-3">
              {currentTask.steps.map(step => (
                <div key={step.id} className="bg-white p-3 rounded border">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className={`w-2 h-2 rounded-full ${
                        step.status === 'completed' ? 'bg-green-500' :
                        step.status === 'running' ? 'bg-blue-500' :
                        step.status === 'failed' ? 'bg-red-500' :
                        'bg-gray-400'
                      }`}></span>
                      <span className="font-medium">{step.name}</span>
                    </div>
                    <span className="text-xs text-gray-500">
                      {step.type === 'rag' ? 'RAG检索' :
                       step.type === 'plugin' ? '插件调用' : '推理'}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 mb-2">{step.description}</div>
                  
                  {step.status === 'completed' && step.output && (
                    <div className="bg-gray-50 p-2 rounded text-xs">
                      <div className="font-medium mb-1">输出:</div>
                      <pre className="whitespace-pre-wrap text-gray-700">
                        {typeof step.output === 'object' 
                          ? JSON.stringify(step.output, null, 2)
                          : step.output}
                      </pre>
                    </div>
                  )}
                  
                  {step.status === 'failed' && step.error && (
                    <div className="bg-red-50 p-2 rounded text-xs">
                      <div className="font-medium mb-1 text-red-700">错误:</div>
                      <div className="text-red-600">{step.error}</div>
                    </div>
                  )}
                  
                  {step.duration && (
                    <div className="text-xs text-gray-500 mt-1">
                      耗时: {step.duration}ms
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default AgentPanel 