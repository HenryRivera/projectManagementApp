import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { createProject, getUsers, getTags } from '../api/projects'
import './ProjectForm.css'

const ProjectForm = () => {
  const navigate = useNavigate()
  const [users, setUsers] = useState([])
  const [existingTags, setExistingTags] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    short_description: '',
    owner_id: '',
    status: 'planning',
    health: 'healthy',
    tag_names: []
  })

  const [tagInput, setTagInput] = useState('')

  useEffect(() => {
    fetchUsers()
    fetchTags()
  }, [])

  const fetchUsers = async () => {
    try {
      const data = await getUsers()
      setUsers(data)
    } catch (err) {
      console.error('Error fetching users:', err)
    }
  }

  const fetchTags = async () => {
    try {
      const data = await getTags()
      setExistingTags(data)
    } catch (err) {
      console.error('Error fetching tags:', err)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleAddTag = (tagName) => {
    const tag = tagName.trim().toLowerCase()
    if (tag && !formData.tag_names.includes(tag)) {
      setFormData(prev => ({
        ...prev,
        tag_names: [...prev.tag_names, tag]
      }))
    }
    setTagInput('')
  }

  const handleRemoveTag = (tagToRemove) => {
    setFormData(prev => ({
      ...prev,
      tag_names: prev.tag_names.filter(tag => tag !== tagToRemove)
    }))
  }

  const handleTagKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAddTag(tagInput)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const projectData = {
        ...formData,
        owner_id: formData.owner_id ? parseInt(formData.owner_id) : null
      }

      const newProject = await createProject(projectData)
      navigate(`/projects/${newProject.id}`)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="project-form-container">
      <div className="project-form-header">
        <button onClick={() => navigate('/')} className="btn-back">
          ← Back to Projects
        </button>
        <h2>Create New Project</h2>
      </div>

      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleSubmit} className="project-form">
        <div className="form-group">
          <label htmlFor="title">Title *</label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            placeholder="Enter project title"
          />
        </div>

        <div className="form-group">
          <label htmlFor="short_description">Short Description</label>
          <input
            type="text"
            id="short_description"
            name="short_description"
            value={formData.short_description}
            onChange={handleChange}
            placeholder="Brief summary of the project"
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows={5}
            placeholder="Detailed project description"
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="owner_id">Owner</label>
            <select
              id="owner_id"
              name="owner_id"
              value={formData.owner_id}
              onChange={handleChange}
            >
              <option value="">Select Owner</option>
              {users.map(user => (
                <option key={user.id} value={user.id}>
                  {user.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="status">Status</label>
            <select
              id="status"
              name="status"
              value={formData.status}
              onChange={handleChange}
            >
              <option value="planning">Planning</option>
              <option value="in_progress">In Progress</option>
              <option value="on_hold">On Hold</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="health">Health</label>
            <select
              id="health"
              name="health"
              value={formData.health}
              onChange={handleChange}
            >
              <option value="healthy">Healthy</option>
              <option value="at_risk">At Risk</option>
              <option value="critical">Critical</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label>Tags</label>
          <div className="tags-input-container">
            <div className="selected-tags">
              {formData.tag_names.map(tag => (
                <span key={tag} className="tag">
                  {tag}
                  <button
                    type="button"
                    onClick={() => handleRemoveTag(tag)}
                    className="tag-remove"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            <input
              type="text"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={handleTagKeyDown}
              placeholder="Type and press Enter to add tags"
            />
            {existingTags.length > 0 && (
              <div className="existing-tags">
                <span className="existing-tags-label">Existing tags:</span>
                {existingTags
                  .filter(tag => !formData.tag_names.includes(tag.name))
                  .map(tag => (
                    <button
                      key={tag.id}
                      type="button"
                      onClick={() => handleAddTag(tag.name)}
                      className="existing-tag-btn"
                    >
                      + {tag.name}
                    </button>
                  ))}
              </div>
            )}
          </div>
        </div>

        <div className="form-actions">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="btn-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading || !formData.title}
            className="btn-primary"
          >
            {loading ? 'Creating...' : 'Create Project'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default ProjectForm
