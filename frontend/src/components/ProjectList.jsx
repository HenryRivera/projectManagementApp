import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getProjects, getUsers, getTags, bulkUpdateProjects } from '../api/projects'
import { useWebSocket } from '../hooks/useWebSocket'
import ProjectCard from './ProjectCard'
import ProjectFilters from './ProjectFilters'
import BulkOperations from './BulkOperations'
import './ProjectList.css'

const ProjectList = () => {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(9)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)
  const [sortBy, setSortBy] = useState('updated_at')
  const [sortOrder, setSortOrder] = useState('desc')
  const [filters, setFilters] = useState({
    status: '',
    owner_id: '',
    tag_name: '',
    health: '',
    search_query: '',
    include_deleted: false
  })
  const [users, setUsers] = useState([])
  const [tags, setTags] = useState([])
  const [selectedProjects, setSelectedProjects] = useState(new Set())
  const navigate = useNavigate()

  const fetchTags = async () => {
    try {
      const data = await getTags()
      setTags(data)
    } catch (err) {
      console.error('Error fetching tags:', err)
    }
  }

  const fetchProjects = async () => {
    try {
      setLoading(true)

      // Build params, handling special "deleted" health filter
      const apiFilters = { ...filters }
      let includeDeleted = false

      if (apiFilters.health === 'deleted') {
        // Show only deleted projects
        includeDeleted = true
        delete apiFilters.health  // Don't filter by health, filter by deleted_at on backend
        apiFilters.only_deleted = true
      }

      const params = {
        page,
        page_size: pageSize,
        sort_by: sortBy,
        sort_order: sortOrder,
        include_deleted: includeDeleted,
        ...Object.fromEntries(Object.entries(apiFilters).filter(([_, v]) => v !== '' && v !== false))
      }
      const data = await getProjects(params)
      setProjects(data.items)
      setTotal(data.total)
      setTotalPages(data.total_pages)
      setError(null)
    } catch (err) {
      setError(err.message)
      console.error('Error fetching projects:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProjects()
  }, [page, sortBy, sortOrder, filters])

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const data = await getUsers()
        setUsers(data)
      } catch (err) {
        console.error('Error fetching users:', err)
      }
    }
    fetchUsers()
  }, [])

  useEffect(() => {
    fetchTags()
  }, [])

  // WebSocket for real-time updates
  const handleWebSocketMessage = (data) => {
    if (data.type === 'project_update') {
      // Refresh the project list when updates occur
      fetchProjects()
    }
  }

  useWebSocket(handleWebSocketMessage)

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(field)
      setSortOrder('asc')
    }
  }

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters)
    setPage(1) // Reset to first page when filters change
  }

  const handleBulkUpdate = async (updateData) => {
    try {
      const projectIds = Array.from(selectedProjects)
      const result = await bulkUpdateProjects({
        project_ids: projectIds,
        ...updateData
      })
      alert(`Updated ${result.updated_count} projects. ${result.failed_count} failed.`)
      setSelectedProjects(new Set())
      fetchProjects()
      // Refresh tags in case new tags were created
      if (updateData.tag_names) {
        fetchTags()
      }
    } catch (err) {
      alert(`Error: ${err.response?.data?.detail || err.message}`)
    }
  }

  const toggleProjectSelection = (projectId) => {
    const newSelected = new Set(selectedProjects)
    if (newSelected.has(projectId)) {
      newSelected.delete(projectId)
    } else {
      newSelected.add(projectId)
    }
    setSelectedProjects(newSelected)
  }

  const selectAll = () => {
    if (selectedProjects.size === projects.length) {
      setSelectedProjects(new Set())
    } else {
      setSelectedProjects(new Set(projects.map(p => p.id)))
    }
  }

  if (loading && projects.length === 0) {
    return <div className="loading">Loading projects...</div>
  }

  return (
    <div className="project-list">
      <div className="project-list-header">
        <h2>Projects ({total})</h2>
        <button onClick={() => navigate('/projects/new')} className="btn-primary">
          New Project
        </button>
      </div>

      <ProjectFilters
        filters={filters}
        users={users}
        tags={tags}
        onFilterChange={handleFilterChange}
      />

      {selectedProjects.size > 0 && (
        <BulkOperations
          selectedCount={selectedProjects.size}
          onBulkUpdate={handleBulkUpdate}
          onClearSelection={() => setSelectedProjects(new Set())}
        />
      )}

      <div className="sort-controls">
        <span>Sort by:</span>
        <button
          className={sortBy === 'title' ? 'active' : ''}
          onClick={() => handleSort('title')}
        >
          Title {sortBy === 'title' && (sortOrder === 'asc' ? '↑' : '↓')}
        </button>
        <button
          className={sortBy === 'updated_at' ? 'active' : ''}
          onClick={() => handleSort('updated_at')}
        >
          Updated {sortBy === 'updated_at' && (sortOrder === 'asc' ? '↑' : '↓')}
        </button>
        <button
          className={sortBy === 'progress' ? 'active' : ''}
          onClick={() => handleSort('progress')}
        >
          Progress {sortBy === 'progress' && (sortOrder === 'asc' ? '↑' : '↓')}
        </button>
      </div>

      {error && <div className="error">Error: {error}</div>}

      <div className="projects-grid">
        {projects.map(project => (
          <ProjectCard
            key={project.id}
            project={project}
            isSelected={selectedProjects.has(project.id)}
            onSelect={() => toggleProjectSelection(project.id)}
            onClick={() => navigate(`/projects/${project.id}`)}
          />
        ))}
      </div>

      {projects.length === 0 && !loading && (
        <div className="empty-state">No projects found</div>
      )}

      <div className="pagination">
        <button
          disabled={page === 1}
          onClick={() => setPage(page - 1)}
        >
          Previous
        </button>
        <span>
          Page {page} of {totalPages}
        </span>
        <button
          disabled={page >= totalPages}
          onClick={() => setPage(page + 1)}
        >
          Next
        </button>
      </div>
    </div>
  )
}

export default ProjectList
