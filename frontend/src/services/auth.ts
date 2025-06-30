import apiClient from './api'

// 用户类型
export interface User {
  id: string
  username: string
  email: string
  role: string
}

// 登录请求
export interface LoginRequest {
  username: string
  password: string
}

// 注册请求
export interface RegisterRequest {
  username: string
  email: string
  password: string
  full_name?: string
}

// 登录响应
export interface LoginResponse {
  access_token: string
  token_type: string
  user_id: string
  username: string
  role: string
}

// 认证 API 服务
export const authApi = {
  // 用户登录
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post('/auth/login', data)
    return response.data
  },

  // 用户注册
  async register(data: RegisterRequest): Promise<LoginResponse> {
    const response = await apiClient.post('/auth/register', data)
    return response.data
  },

  // 获取当前用户信息
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get('/auth/me')
    return response.data
  },

  // 刷新令牌
  async refreshToken(): Promise<LoginResponse> {
    const response = await apiClient.post('/auth/refresh')
    return response.data
  },
} 