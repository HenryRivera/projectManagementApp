import React from 'react';

export interface ProgressBarProps {
  progress: number;
  color?: string;
  backgroundColor?: string;
  height?: number;
  showLabel?: boolean;
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  color = '#3b82f6',
  backgroundColor = '#e5e7eb',
  height = 8,
  showLabel = true,
  className = '',
}) => {
  const clampedProgress = Math.min(100, Math.max(0, progress));

  return (
    <div
      className={`progress-bar-container ${className}`}
      style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
    >
      <div
        style={{
          flex: 1,
          height: `${height}px`,
          backgroundColor,
          borderRadius: `${height / 2}px`,
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${clampedProgress}%`,
            backgroundColor: color,
            borderRadius: `${height / 2}px`,
            transition: 'width 0.3s ease',
          }}
        />
      </div>
      {showLabel && (
        <span style={{ fontSize: '12px', color: '#6b7280', minWidth: '36px' }}>
          {clampedProgress}%
        </span>
      )}
    </div>
  );
};

export default ProgressBar;
