import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Login.css'

const Login = () => {
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [showSSOSimulation, setShowSSOSimulation] = useState(false)

  const { login, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  // Get the intended destination
  const from = location.state?.from?.pathname || '/'

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true })
    }
  }, [isAuthenticated, navigate, from])

  const handleSSOLogin = async () => {
    if (!email.trim()) {
      setError('Please enter your email address')
      return
    }

    if (!email.includes('@')) {
      setError('Please enter a valid email address')
      return
    }

    setError('')
    setIsLoading(true)
    setShowSSOSimulation(true)

    try {
      // Simulate SSO redirect and callback
      await new Promise(resolve => setTimeout(resolve, 1500))

      await login(email)
      navigate(from, { replace: true })
    } catch (err) {
      setError('SSO authentication failed. Please try again.')
      setShowSSOSimulation(false)
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSSOLogin()
    }
  }

  // Show SSO simulation overlay
  if (showSSOSimulation) {
    return (
      <div className="login-container">
        <div className="sso-simulation">
          <div className="sso-popup">
            <div className="sso-header">
              <div className="sso-logo">🔐</div>
              <h2>Corporate SSO</h2>
            </div>
            <div className="sso-content">
              <div className="sso-spinner"></div>
              <p>Authenticating with SSO provider...</p>
              <p className="sso-email">{email}</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="login-logo">📊</div>
          <h1>Project Management</h1>
          <p>Sign in to access your projects</p>
        </div>

        <div className="login-form">
          <div className="form-group">
            <label htmlFor="email">Corporate Email</label>
            <input
              id="email"
              type="email"
              placeholder="you@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
              autoFocus
            />
          </div>

          {error && (
            <div className="login-error">
              {error}
            </div>
          )}

          <button
            onClick={handleSSOLogin}
            disabled={isLoading}
            className="sso-button"
          >
            {isLoading ? 'Connecting...' : 'Continue with SSO 🔒'}
          </button>

          <div className="login-divider">
            <span>Demo Accounts</span>
          </div>

          <div className="demo-accounts">
            <button onClick={() => setEmail('sarah.chen@company.com')} className="demo-account">
              <span className="demo-name">Sarah Chen</span>
              <span className="demo-role">Admin</span>
            </button>
            <button onClick={() => setEmail('john.smith@company.com')} className="demo-account">
              <span className="demo-name">John Smith</span>
              <span className="demo-role">Manager</span>
            </button>
            <button onClick={() => setEmail('demo@company.com')} className="demo-account">
              <span className="demo-name">Demo User</span>
              <span className="demo-role">Viewer</span>
            </button>
          </div>
        </div>

        <div className="login-footer">
          <p>Internal Platform • SSO Authentication Required</p>
        </div>
      </div>
    </div>
  )
}

export default Login
