import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { apiClient } from '@/lib/api.ts'

interface User {
  id: string
  name: string
  email: string
  role: string
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (name: string, email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // トークンから現在のユーザー情報を取得
  const getCurrentUser = async () => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        setIsLoading(false)
        return
      }

      const response = await apiClient.get('/api/v1/users/me')
      setUser(response.data)
    } catch (error) {
      console.error('Failed to get current user:', error)
      localStorage.removeItem('token')
    } finally {
      setIsLoading(false)
    }
  }

  // ログイン関数
  const login = async (email: string, password: string) => {
    try {
      const formData = new FormData()
      formData.append('username', email) // FastAPI OAuth2PasswordRequestFormはusernameを期待
      formData.append('password', password)

      const response = await apiClient.post('/api/v1/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })

      const { access_token, user: userData } = response.data
      localStorage.setItem('token', access_token)
      setUser(userData)
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'ログインに失敗しました')
    }
  }

  // 登録関数
  const register = async (name: string, email: string, password: string) => {
    try {
      const response = await apiClient.post('/api/v1/auth/register', {
        name,
        email,
        password,
      })

      const { access_token, user: userData } = response.data
      localStorage.setItem('token', access_token)
      setUser(userData)
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '登録に失敗しました')
    }
  }

  // ログアウト関数
  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
  }

  // 初期化時にユーザー情報を取得
  useEffect(() => {
    getCurrentUser()
  }, [])

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}