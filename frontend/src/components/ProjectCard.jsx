import React from 'react'
import PropTypes from 'prop-types'
import './ProjectCard.css'

const ProjectCard = ({ project, isSelected, onSelect, onClick }) => {
  const getHealthColor = (health) => {
    switch (health) {
      case 'healthy':
        return '#28a745'
      case 'at_risk':
        return '#ffc107'
      case 'critical':
        return '#dc3545'
      default:
        return '#6c757d'
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return '#007bff'
      case 'planning':
        return '#6c757d'
      case 'on_hold':
        return '#ffc107'
      case 'completed':
        return '#28a745'
      case 'cancelled':
        return '#dc3545'
      default:
        return '#6c757d'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return '►'
      case 'planning':
        return '○'
      case 'on_hold':
        return '❚❚'
      case 'completed':
        return '✓'
      case 'cancelled':
        return '✕'
      default:
        return '○'
    }
  }

  const getHealthIcon = (health) => {
    switch (health) {
      case 'healthy':
        return '●'
      case 'at_risk':
        return '●'
      case 'critical':
        return '●'
      default:
        return '●'
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  return (
    <div
      className={`project-card ${isSelected ? 'selected' : ''} ${project.deleted_at ? 'deleted' : ''}`}
      onClick={onClick}
    >
      {project.deleted_at && (
        <div className="deleted-overlay">
          <span className="deleted-badge">Deleted</span>
        </div>
      )}
      <div className="card-checkbox" onClick={(e) => e.stopPropagation()}>
        <input
          type="checkbox"
          checked={isSelected}
          onChange={onSelect}
        />
      </div>
      <div className="card-header">
        <h3 className="card-title">{project.title}</h3>
        <div className="card-badges">
          <span
            className="badge status"
            style={{ backgroundColor: getStatusColor(project.status) }}
          >
            {getStatusIcon(project.status)} {project.status}
          </span>
          <span
            className="badge health"
            style={{ backgroundColor: getHealthColor(project.health) }}
          >
            {getHealthIcon(project.health)} {project.health}
          </span>
        </div>
      </div>
      <p className="card-description">
        {project.short_description || project.description?.substring(0, 100) || 'No description'}
      </p>
      <div className="card-progress">
        <div className="progress-label">
          <span>Progress</span>
          <span>{project.progress.toFixed(1)}%</span>
        </div>
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${project.progress}%` }}
          />
        </div>
      </div>
      <div className="card-footer">
        <div className="card-info">
          <div className="info-item">
            <strong>Owner:</strong> {project.owner?.name || 'Unassigned'}
          </div>
          <div className="info-item">
            <strong>Updated:</strong> {formatDate(project.updated_at)}
          </div>
        </div>
        {project.tags && project.tags.length > 0 && (
          <div className="card-tags">
            {project.tags.map(tag => (
              <span key={tag.id} className="tag">
                {tag.name}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

ProjectCard.propTypes = {
  project: PropTypes.shape({
    id: PropTypes.number,
    title: PropTypes.string,
    short_description: PropTypes.string,
    status: PropTypes.string,
    health: PropTypes.string,
    progress: PropTypes.number,
    updated_at: PropTypes.string,
    deleted_at: PropTypes.string,
    owner: PropTypes.object,
    tags: PropTypes.array,
  }).isRequired,
  isSelected: PropTypes.bool,
  onSelect: PropTypes.func,
  onClick: PropTypes.func,
}

export default ProjectCard
