import React, { useState } from 'react'
import PropTypes from 'prop-types'
import './BulkOperations.css'

const BulkOperations = ({ selectedCount, onBulkUpdate, onClearSelection }) => {
  const [status, setStatus] = useState('')
  const [tagNames, setTagNames] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    const updateData = {}
    
    if (status) {
      updateData.status = status
    }
    
    if (tagNames.trim()) {
      updateData.tag_names = tagNames.split(',').map(t => t.trim()).filter(t => t)
    }

    if (Object.keys(updateData).length > 0) {
      onBulkUpdate(updateData)
      setStatus('')
      setTagNames('')
    }
  }

  return (
    <div className="bulk-operations">
      <div className="bulk-header">
        <span>{selectedCount} project(s) selected</span>
        <button onClick={onClearSelection} className="btn-clear">Clear</button>
      </div>
      <form onSubmit={handleSubmit} className="bulk-form">
        <div className="bulk-controls">
          <div className="bulk-control">
            <label>Update Status</label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
            >
              <option value="">No change</option>
              <option value="planning">Planning</option>
              <option value="active">Active</option>
              <option value="on_hold">On Hold</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div className="bulk-control">
            <label>Update Tags (comma-separated)</label>
            <input
              type="text"
              value={tagNames}
              onChange={(e) => setTagNames(e.target.value)}
              placeholder="tag1, tag2, tag3"
            />
          </div>
          <button type="submit" className="btn-apply" disabled={!status && !tagNames.trim()}>
            Apply to Selected
          </button>
        </div>
      </form>
    </div>
  )
}

BulkOperations.propTypes = {
  selectedCount: PropTypes.number.isRequired,
  onBulkUpdate: PropTypes.func.isRequired,
  onClearSelection: PropTypes.func.isRequired,
}

export default BulkOperations
