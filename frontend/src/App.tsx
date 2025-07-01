import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import KnowledgeBases from './pages/KnowledgeBase'
import KnowledgeBaseDetail from './pages/KnowledgeBaseDetail'
import Chat from './pages/Chat'
import Settings from './pages/Settings'
import Plugins from './pages/Plugins'
import EnhancedRetrieval from './pages/EnhancedRetrieval'

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <Routes>
          {/* 公开路由 */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* 受保护的路由 */}
          <Route path="/" element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="kb" element={<KnowledgeBases />} />
            <Route path="kb/:id" element={<KnowledgeBaseDetail />} />
            <Route path="chat" element={<Chat />} />
            <Route path="settings" element={<Settings />} />
            <Route path="plugins" element={<Plugins />} />
            <Route path="enhanced-retrieval" element={<EnhancedRetrieval />} />
          </Route>
          
          {/* 404 页面 */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </div>
    </AuthProvider>
  )
}

export default App 