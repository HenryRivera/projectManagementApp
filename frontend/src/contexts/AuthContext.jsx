import React, { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

// Mock users that would come from SSO
const MOCK_SSO_USERS = [
  { id: 1, email: 'sarah.chen@company.com', name: 'Sarah Chen', role: 'admin' },
  { id: 2, email: 'john.smith@company.com', name: 'John Smith', role: 'manager' },
  { id: 3, email: 'maria.garcia@company.com', name: 'Maria Garcia', role: 'developer' },
  { id: 4, email: 'demo@company.com', name: 'Demo User', role: 'viewer' },
]

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // Check for existing session on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('sso_user')
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser))
      } catch (e) {
        localStorage.removeItem('sso_user')
      }
    }
    setLoading(false)
  }, [])

  // Simulate SSO login - in real implementation this would redirect to SSO provider
  const login = async (email) => {
    setLoading(true)

    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 1000))

    // Find matching user or create a guest user
    let matchedUser = MOCK_SSO_USERS.find(u => u.email.toLowerCase() === email.toLowerCase())

    if (!matchedUser) {
      // For demo, accept any email and create a temporary user
      matchedUser = {
        id: Date.now(),
        email: email,
        name: email.split('@')[0].replace(/[._]/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
        role: 'viewer'
      }
    }

    const userWithToken = {
      ...matchedUser,
      accessToken: `mock_token_${Date.now()}`,
      loginTime: new Date().toISOString()
    }

    localStorage.setItem('sso_user', JSON.stringify(userWithToken))
    setUser(userWithToken)
    setLoading(false)

    return userWithToken
  }

  const logout = () => {
    localStorage.removeItem('sso_user')
    setUser(null)
  }

  const value = {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
