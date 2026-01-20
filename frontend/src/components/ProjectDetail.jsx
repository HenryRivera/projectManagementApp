import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getProject, getUsers, getTags, updateProject, deleteProject, recoverProject, createMilestone, updateMilestone, addTeamMember, updateTeamMember, removeTeamMember } from '../api/projects'
import { useWebSocket } from '../hooks/useWebSocket'
import './ProjectDetail.css'

// Helper to format error messages
const formatError = (err) => {
  const detail = err.response?.data?.detail
  if (typeof detail === 'string') {
    return detail
  }
  if (Array.isArray(detail)) {
    // Pydantic validation errors
    return detail.map(e => e.msg || e.message || JSON.stringify(e)).join(', ')
  }
  if (typeof detail === 'object' && detail !== null) {
    return JSON.stringify(detail)
  }
  return err.message || 'An error occurred'
}

const ProjectDetail = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [users, setUsers] = useState([])
  const [availableTags, setAvailableTags] = useState([])
  const [showAddMilestone, setShowAddMilestone] = useState(false)
  const [showAddMember, setShowAddMember] = useState(false)
  const [showEditProject, setShowEditProject] = useState(false)
  const [newMilestone, setNewMilestone] = useState({ title: '', description: '', due_date: '' })
  const [newMember, setNewMember] = useState({ user_id: '', role: 'developer', capacity: 1.0 })
  const [editForm, setEditForm] = useState({})
  const [newTagInput, setNewTagInput] = useState('')
  const [showFullDescription, setShowFullDescription] = useState(false)
  const [editingMember, setEditingMember] = useState(null)

  const DESCRIPTION_CHAR_LIMIT = 200

  useEffect(() => {
    fetchProject()
    fetchUsers()
    fetchTags()
  }, [id])

  const fetchProject = async () => {
    try {
      setLoading(true)
      const data = await getProject(id)
      setProject(data)
      setEditForm({
        title: data.title,
        description: data.description || '',
        short_description: data.short_description || '',
        owner_id: data.owner_id || '',
        status: data.status,
        health: data.health,
        tag_names: data.tags?.map(t => t.name) || [],
        version: data.version
      })
      setError(null)
    } catch (err) {
      setError(err.message)
      console.error('Error fetching project:', err)
    } finally {
      setLoading(false)
    }
  }

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
      setAvailableTags(data)
    } catch (err) {
      console.error('Error fetching tags:', err)
    }
  }

  // WebSocket for real-time updates
  const handleWebSocketMessage = (data) => {
    if (data.type === 'project_update' && data.project_id === parseInt(id)) {
      fetchProject()
    }
  }

  useWebSocket(handleWebSocketMessage)

  const handleUpdateProject = async (e) => {
    e.preventDefault()
    try {
      const updateData = {
        title: editForm.title,
        description: editForm.description,
        short_description: editForm.short_description,
        owner_id: editForm.owner_id ? parseInt(editForm.owner_id) : null,
        status: editForm.status,
        health: editForm.health,
        tag_names: editForm.tag_names || []
      }
      console.log('Updating project with:', updateData)
      await updateProject(id, updateData)
      setShowEditProject(false)
      fetchProject()
    } catch (err) {
      console.error('Update error:', err)
      alert(`Error: ${formatError(err)}`)
    }
  }

  const handleDeleteProject = async () => {
    if (window.confirm('Are you sure you want to delete this project? It can be recovered later.')) {
      try {
        await deleteProject(id)
        navigate('/')
      } catch (err) {
        alert(`Error: ${formatError(err)}`)
      }
    }
  }

  const handleRecoverProject = async () => {
    try {
      await recoverProject(id)
      fetchProject()
    } catch (err) {
      alert(`Error: ${formatError(err)}`)
    }
  }

  const handleAddTag = (tagName) => {
    const tag = tagName.trim().toLowerCase()
    if (tag && !editForm.tag_names?.includes(tag)) {
      setEditForm(prev => ({
        ...prev,
        tag_names: [...(prev.tag_names || []), tag]
      }))
    }
    setNewTagInput('')
  }

  const handleRemoveTag = (tagToRemove) => {
    setEditForm(prev => ({
      ...prev,
      tag_names: prev.tag_names?.filter(tag => tag !== tagToRemove) || []
    }))
  }

  const handleTagKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAddTag(newTagInput)
    }
  }

  const unselectedTags = availableTags.filter(
    tag => !editForm.tag_names?.includes(tag.name)
  )

  const handleToggleMilestone = async (milestone) => {
    try {
      await updateMilestone(milestone.id, {
        ...milestone,
        completed: !milestone.completed
      })
      fetchProject()
    } catch (err) {
      alert(`Error: ${formatError(err)}`)
    }
  }

  const handleAddMilestone = async (e) => {
    e.preventDefault()
    try {
      // Format the due_date as a datetime if provided (backend expects datetime format)
      const milestoneData = {
        title: newMilestone.title,
        description: newMilestone.description || null,
        due_date: newMilestone.due_date ? `${newMilestone.due_date}T00:00:00` : null
      }
      await createMilestone(id, milestoneData)
      setNewMilestone({ title: '', description: '', due_date: '' })
      setShowAddMilestone(false)
      fetchProject()
    } catch (err) {
      alert(`Error: ${formatError(err)}`)
    }
  }

  const handleAddMember = async (e) => {
    e.preventDefault()
    try {
      await addTeamMember(id, {
        ...newMember,
        user_id: parseInt(newMember.user_id)
      })
      setNewMember({ user_id: '', role: 'developer', capacity: 1.0 })
      setShowAddMember(false)
      fetchProject()
    } catch (err) {
      alert(`Error: ${formatError(err)}`)
    }
  }

  const handleRemoveMember = async (memberId) => {
    if (window.confirm('Remove this team member?')) {
      try {
        await removeTeamMember(memberId)
        fetchProject()
      } catch (err) {
        alert(`Error: ${formatError(err)}`)
      }
    }
  }

  const handleUpdateMember = async (memberId, updates) => {
    try {
      await updateTeamMember(memberId, updates)
      setEditingMember(null)
      fetchProject()
    } catch (err) {
      alert(`Error: ${formatError(err)}`)
    }
  }

  if (loading) {
    return <div className="loading">Loading project...</div>
  }

  if (error || !project) {
    return (
      <div className="error-container">
        <div className="error">Error: {error || 'Project not found'}</div>
        <button onClick={() => navigate('/')} className="btn-primary">
          Back to Projects
        </button>
      </div>
    )
  }

  const completedMilestones = project.milestones?.filter(m => m.completed).length || 0
  const totalMilestones = project.milestones?.length || 0
  const progressFromMilestones = totalMilestones > 0
    ? (completedMilestones / totalMilestones) * 100
    : 0

  return (
    <div className="project-detail">
      <div className="detail-header">
        <div className="header-left">
          <button onClick={() => navigate('/')} className="btn-back">
            ← Back to Projects
          </button>
          <h1>
            {project.title}
            {project.deleted_at && (
              <span className="deleted-badge">Deleted</span>
            )}
          </h1>
          <div className="header-actions">
            {project.deleted_at ? (
              <button onClick={handleRecoverProject} className="btn-success">
                Recover Project
              </button>
            ) : (
              <>
                <button onClick={() => setShowEditProject(true)} className="btn-secondary">
                  Edit
                </button>
                <button onClick={handleDeleteProject} className="btn-danger">
                  Delete
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {showEditProject && (
        <div className="modal-overlay" onClick={() => setShowEditProject(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Edit Project</h2>
            <form onSubmit={handleUpdateProject}>
              <div className="form-group">
                <label>Title</label>
                <input
                  type="text"
                  value={editForm.title}
                  onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Short Description</label>
                <input
                  type="text"
                  value={editForm.short_description}
                  onChange={(e) => setEditForm({ ...editForm, short_description: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={editForm.description}
                  onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                  rows={4}
                />
              </div>
              <div className="form-group">
                <label>Owner</label>
                <select
                  value={editForm.owner_id}
                  onChange={(e) => setEditForm({ ...editForm, owner_id: e.target.value })}
                >
                  <option value="">Unassigned</option>
                  {users.map(user => (
                    <option key={user.id} value={user.id}>{user.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Status</label>
                  <select
                    value={editForm.status}
                    onChange={(e) => setEditForm({ ...editForm, status: e.target.value })}
                  >
                    <option value="planning">Planning</option>
                    <option value="active">Active</option>
                    <option value="on_hold">On Hold</option>
                    <option value="completed">Completed</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Health</label>
                  <select
                    value={editForm.health}
                    onChange={(e) => setEditForm({ ...editForm, health: e.target.value })}
                  >
                    <option value="healthy">Healthy</option>
                    <option value="at_risk">At Risk</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label>Tags</label>
                <div className="tags-section">
                  <div className="selected-tags">
                    {editForm.tag_names?.map(tag => (
                      <span key={tag} className="tag-chip">
                        {tag}
                        <button
                          type="button"
                          className="tag-remove"
                          onClick={() => handleRemoveTag(tag)}
                        >
                          ×
                        </button>
                      </span>
                    ))}
                    {(!editForm.tag_names || editForm.tag_names.length === 0) && (
                      <span className="no-tags">No tags selected</span>
                    )}
                  </div>

                  {unselectedTags.length > 0 && (
                    <div className="available-tags">
                      <span className="tags-label">Add existing:</span>
                      {unselectedTags.map(tag => (
                        <button
                          key={tag.id}
                          type="button"
                          className="tag-add-btn"
                          onClick={() => handleAddTag(tag.name)}
                        >
                          + {tag.name}
                        </button>
                      ))}
                    </div>
                  )}

                  <div className="new-tag-input">
                    <input
                      type="text"
                      placeholder="Create new tag..."
                      value={newTagInput}
                      onChange={(e) => setNewTagInput(e.target.value)}
                      onKeyDown={handleTagKeyDown}
                    />
                    <button
                      type="button"
                      onClick={() => handleAddTag(newTagInput)}
                      disabled={!newTagInput.trim()}
                      className="btn-add-tag"
                    >
                      Add
                    </button>
                  </div>
                </div>
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowEditProject(false)} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="detail-content">
        <div className="detail-main">
          <section className="detail-section">
            <h2>Summary</h2>
            <div className="summary-info">
              <div className="info-row">
                <strong>Description:</strong>
                <div className="description-content">
                  {(() => {
                    const fullText = project.description || project.short_description || 'No description'
                    const isLong = fullText.length > DESCRIPTION_CHAR_LIMIT
                    const displayText = isLong && !showFullDescription
                      ? fullText.slice(0, DESCRIPTION_CHAR_LIMIT) + '...'
                      : fullText
                    return (
                      <>
                        <p>{displayText}</p>
                        {isLong && (
                          <button
                            className="btn-show-more"
                            onClick={() => setShowFullDescription(!showFullDescription)}
                          >
                            {showFullDescription ? 'Show less' : 'Show more'}
                          </button>
                        )}
                      </>
                    )
                  })()}
                </div>
              </div>
              <div className="info-row">
                <strong>Owner:</strong>
                <span>{project.owner?.name || 'Unassigned'}</span>
              </div>
              <div className="info-row">
                <strong>Status:</strong>
                <span className={`badge status-${project.status}`}>{project.status}</span>
              </div>
              <div className="info-row">
                <strong>Health:</strong>
                <span className={`badge health-${project.health}`}>{project.health}</span>
              </div>
              <div className="info-row">
                <strong>Progress:</strong>
                <span>{project.progress.toFixed(1)}%</span>
              </div>
              <div className="info-row">
                <strong>Tags:</strong>
                <div className="tags">
                  {project.tags?.map(tag => (
                    <span key={tag.id} className="tag">{tag.name}</span>
                  ))}
                </div>
              </div>
              <div className="info-row">
                <strong>Last Updated:</strong>
                <span>{new Date(project.updated_at).toLocaleString()}</span>
              </div>
            </div>
          </section>

          <section className="detail-section">
            <div className="section-header">
              <h2>Milestones ({completedMilestones}/{totalMilestones})</h2>
              <button onClick={() => setShowAddMilestone(!showAddMilestone)} className="btn-small">
                {showAddMilestone ? 'Cancel' : '+ Add Milestone'}
              </button>
            </div>
            {showAddMilestone && (
              <form onSubmit={handleAddMilestone} className="add-form">
                <input
                  type="text"
                  placeholder="Milestone title"
                  value={newMilestone.title}
                  onChange={(e) => setNewMilestone({ ...newMilestone, title: e.target.value })}
                  required
                />
                <textarea
                  placeholder="Description"
                  value={newMilestone.description}
                  onChange={(e) => setNewMilestone({ ...newMilestone, description: e.target.value })}
                />
                <input
                  type="date"
                  value={newMilestone.due_date}
                  onChange={(e) => setNewMilestone({ ...newMilestone, due_date: e.target.value })}
                />
                <button type="submit" className="btn-primary">Add</button>
              </form>
            )}
            <div className="milestones">
              {project.milestones && project.milestones.length > 0 ? (
                project.milestones.map(milestone => (
                  <div key={milestone.id} className="milestone-item">
                    <input
                      type="checkbox"
                      checked={milestone.completed}
                      onChange={() => handleToggleMilestone(milestone)}
                    />
                    <div className="milestone-content">
                      <h4>{milestone.title}</h4>
                      {milestone.description && <p>{milestone.description}</p>}
                      {milestone.due_date && (
                        <span className="due-date">
                          Due: {new Date(milestone.due_date).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <p className="empty">No milestones yet</p>
              )}
            </div>
            <div className="progress-summary">
              <strong>Progress from milestones: {progressFromMilestones.toFixed(1)}%</strong>
            </div>
          </section>

          <section className="detail-section">
            <div className="section-header">
              <h2>Team Roster</h2>
              <button onClick={() => setShowAddMember(!showAddMember)} className="btn-small">
                {showAddMember ? 'Cancel' : '+ Add Member'}
              </button>
            </div>
            {showAddMember && (
              <form onSubmit={handleAddMember} className="add-form">
                <select
                  value={newMember.user_id}
                  onChange={(e) => setNewMember({ ...newMember, user_id: e.target.value })}
                  required
                >
                  <option value="">Select user</option>
                  {users.map(user => (
                    <option key={user.id} value={user.id}>{user.name}</option>
                  ))}
                </select>
                <select
                  value={newMember.role}
                  onChange={(e) => setNewMember({ ...newMember, role: e.target.value })}
                >
                  <option value="owner">Owner</option>
                  <option value="manager">Manager</option>
                  <option value="developer">Developer</option>
                  <option value="designer">Designer</option>
                  <option value="qa">QA</option>
                </select>
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.1"
                  placeholder="Capacity (0.0-1.0)"
                  value={newMember.capacity}
                  onChange={(e) => setNewMember({ ...newMember, capacity: parseFloat(e.target.value) })}
                  required
                />
                <button type="submit" className="btn-primary">Add</button>
              </form>
            )}
            <div className="team-members">
              {project.team_members && project.team_members.length > 0 ? (
                project.team_members.map(member => (
                  <div key={member.id} className="team-member-item">
                    <div className="member-info">
                      <strong>{member.user?.name}</strong>
                      <span className="role">{member.role}</span>
                      {editingMember === member.id ? (
                        <div className="capacity-edit">
                          <input
                            type="range"
                            min="0"
                            max="100"
                            step="10"
                            defaultValue={member.capacity * 100}
                            onChange={(e) => {
                              const newCapacity = parseInt(e.target.value) / 100
                              handleUpdateMember(member.id, { capacity: newCapacity })
                            }}
                            className="capacity-slider"
                          />
                          <span className="capacity-value">{(member.capacity * 100).toFixed(0)}%</span>
                        </div>
                      ) : (
                        <span
                          className="capacity editable"
                          onClick={() => setEditingMember(member.id)}
                          title="Click to edit capacity"
                        >
                          Capacity: {(member.capacity * 100).toFixed(0)}%
                        </span>
                      )}
                    </div>
                    <div className="member-actions">
                      {editingMember === member.id && (
                        <button
                          onClick={() => setEditingMember(null)}
                          className="btn-small"
                        >
                          Done
                        </button>
                      )}
                      <button
                        onClick={() => handleRemoveMember(member.id)}
                        className="btn-remove"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <p className="empty">No team members yet</p>
              )}
            </div>
          </section>
        </div>

        <div className="detail-sidebar">
          <section className="detail-section">
            <h2>Recent Activity</h2>
            <div className="activity-list">
              {project.recent_events && project.recent_events.length > 0 ? (
                project.recent_events.map(event => (
                  <div key={event.id} className="activity-item">
                    <div className="activity-type">{event.event_type}</div>
                    <div className="activity-description">{event.description}</div>
                    <div className="activity-time">
                      {new Date(event.created_at).toLocaleString()}
                    </div>
                  </div>
                ))
              ) : (
                <p className="empty">No recent activity</p>
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}

export default ProjectDetail
