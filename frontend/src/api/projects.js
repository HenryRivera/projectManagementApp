import client from './client'

export const getProjects = async (params = {}) => {
  const response = await client.get('/projects', { params })
  return response.data
}

export const getProject = async (id, includeDeleted = true) => {
  const response = await client.get(`/projects/${id}`, {
    params: { include_deleted: includeDeleted }
  })
  return response.data
}

export const createProject = async (project) => {
  const response = await client.post('/projects', project)
  return response.data
}

export const updateProject = async (id, project) => {
  const response = await client.put(`/projects/${id}`, project)
  return response.data
}

export const deleteProject = async (id) => {
  const response = await client.delete(`/projects/${id}`)
  return response.data
}

export const recoverProject = async (id) => {
  const response = await client.post(`/projects/${id}/recover`)
  return response.data
}

export const bulkUpdateProjects = async (bulkUpdate) => {
  const response = await client.post('/projects/bulk-update', bulkUpdate)
  return response.data
}

export const getUsers = async () => {
  const response = await client.get('/users')
  return response.data
}

export const getTags = async () => {
  const response = await client.get('/tags')
  return response.data
}

export const createMilestone = async (projectId, milestone) => {
  const response = await client.post(`/projects/${projectId}/milestones`, milestone)
  return response.data
}

export const updateMilestone = async (milestoneId, milestone) => {
  const response = await client.put(`/milestones/${milestoneId}`, milestone)
  return response.data
}

export const addTeamMember = async (projectId, teamMember) => {
  const response = await client.post(`/projects/${projectId}/team-members`, teamMember)
  return response.data
}

export const updateTeamMember = async (memberId, memberUpdate) => {
  const response = await client.put(`/team-members/${memberId}`, memberUpdate)
  return response.data
}

export const removeTeamMember = async (memberId) => {
  const response = await client.delete(`/team-members/${memberId}`)
  return response.data
}
