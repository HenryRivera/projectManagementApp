import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './components/Login'
import ProjectList from './components/ProjectList'
import ProjectDetail from './components/ProjectDetail'
import ProjectForm from './components/ProjectForm'
import './App.css'

// Header component with user info and logout
const AppHeader = () => {
  const { user, logout, isAuthenticated } = useAuth()

  if (!isAuthenticated) return null

  return (
    <header className="App-header">
      <h1>Project Management</h1>
      <div className="header-user">
        <span className="user-name">{user?.name}</span>
        <span className="user-role">{user?.role}</span>
        <button onClick={logout} className="logout-btn">
          Logout
        </button>
      </div>
    </header>
  )
}

// Main app content with routing
const AppContent = () => {
  return (
    <Router>
      <div className="App">
        <AppHeader />
        <main>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={
              <ProtectedRoute>
                <ProjectList />
              </ProtectedRoute>
            } />
            <Route path="/projects/new" element={
              <ProtectedRoute>
                <ProjectForm />
              </ProtectedRoute>
            } />
            <Route path="/projects/:id" element={
              <ProtectedRoute>
                <ProjectDetail />
              </ProtectedRoute>
            } />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App
