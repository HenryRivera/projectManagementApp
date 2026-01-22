import React from 'react';

export interface Project {
  id: number;
  title: string;
  description?: string;
  status: 'planning' | 'active' | 'on_hold' | 'completed' | 'cancelled';
  progress: number;
  start_date?: string;
  end_date?: string;
  owner_id?: number;
}

export interface ProjectCardProps {
  project: Project;
  onEdit?: (project: Project) => void;
  onDelete?: (projectId: number) => void;
  onClick?: (project: Project) => void;
  className?: string;
}

const statusColors: Record<string, string> = {
  planning: '#6b7280',
  active: '#10b981',
  on_hold: '#f59e0b',
  completed: '#3b82f6',
  cancelled: '#ef4444',
};

export const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  onEdit,
  onDelete,
  onClick,
  className = '',
}) => {
  const statusColor = statusColors[project.status] || '#6b7280';

  const cardStyle: React.CSSProperties = {
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    padding: '16px',
    backgroundColor: '#ffffff',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    cursor: onClick ? 'pointer' : 'default',
    transition: 'box-shadow 0.2s ease',
  };

  return (
    <div
      className={`project-card ${className}`}
      style={cardStyle}
      onClick={() => onClick?.(project)}
      onMouseEnter={(e) => {
        if (onClick) {
          e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        }
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';
      }}
    >
      <h3 style={{ margin: '0 0 8px 0', fontSize: '18px', fontWeight: 600 }}>
        {project.title}
      </h3>

      {project.description && (
        <p style={{ margin: '0 0 12px 0', color: '#6b7280', fontSize: '14px' }}>
          {project.description.length > 100
            ? `${project.description.substring(0, 100)}...`
            : project.description}
        </p>
      )}

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '12px' }}>
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '12px',
            textTransform: 'capitalize',
          }}
        >
          <span
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: statusColor,
            }}
          />
          {project.status.replace('_', ' ')}
        </span>

        <div style={{ flex: 1 }}>
          <div
            style={{
              height: '6px',
              backgroundColor: '#e5e7eb',
              borderRadius: '3px',
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                height: '100%',
                width: `${project.progress}%`,
                backgroundColor: '#3b82f6',
                borderRadius: '3px',
                transition: 'width 0.3s ease',
              }}
            />
          </div>
        </div>
        <span style={{ fontSize: '12px', color: '#6b7280' }}>{project.progress}%</span>
      </div>

      {(onEdit || onDelete) && (
        <div style={{ display: 'flex', gap: '8px' }} onClick={(e) => e.stopPropagation()}>
          {onEdit && (
            <button
              onClick={() => onEdit(project)}
              style={{
                padding: '6px 12px',
                fontSize: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '4px',
                backgroundColor: '#ffffff',
                cursor: 'pointer',
              }}
            >
              Edit
            </button>
          )}
          {onDelete && (
            <button
              onClick={() => onDelete(project.id)}
              style={{
                padding: '6px 12px',
                fontSize: '12px',
                border: '1px solid #fecaca',
                borderRadius: '4px',
                backgroundColor: '#fef2f2',
                color: '#dc2626',
                cursor: 'pointer',
              }}
            >
              Delete
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default ProjectCard;
