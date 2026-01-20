import React, { useState } from 'react'
import './ProjectFilters.css'

const ProjectFilters = ({ filters, users, tags, onFilterChange }) => {
  const [localFilters, setLocalFilters] = useState(filters)

  const handleChange = (field, value) => {
    const newFilters = { ...localFilters, [field]: value }
    setLocalFilters(newFilters)
    onFilterChange(newFilters)
  }

  return (
    <div className="project-filters">
      <div className="filter-group">
        <label>Search</label>
        <input
          type="text"
          placeholder="Search projects..."
          value={localFilters.search_query || ''}
          onChange={(e) => handleChange('search_query', e.target.value)}
        />
      </div>

      <div className="filter-group">
        <label>Status</label>
        <select
          value={localFilters.status || ''}
          onChange={(e) => handleChange('status', e.target.value)}
        >
          <option value="">All</option>
          <option value="planning">Planning</option>
          <option value="active">Active</option>
          <option value="on_hold">On Hold</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>

      <div className="filter-group">
        <label>Owner</label>
        <select
          value={localFilters.owner_id || ''}
          onChange={(e) => handleChange('owner_id', e.target.value ? parseInt(e.target.value) : '')}
        >
          <option value="">All</option>
          {users.map(user => (
            <option key={user.id} value={user.id}>
              {user.name}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>Tag</label>
        <select
          value={localFilters.tag_name || ''}
          onChange={(e) => handleChange('tag_name', e.target.value)}
        >
          <option value="">All</option>
          {tags.map(tag => (
            <option key={tag.id} value={tag.name}>
              {tag.name}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>Health</label>
        <select
          value={localFilters.health || ''}
          onChange={(e) => handleChange('health', e.target.value)}
        >
          <option value="">All (Active)</option>
          <option value="healthy">Healthy</option>
          <option value="at_risk">At Risk</option>
          <option value="critical">Critical</option>
          <option value="deleted">Deleted</option>
        </select>
      </div>
    </div>
  )
}

export default ProjectFilters
