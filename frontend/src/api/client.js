import axios from 'axios'

// Use relative path when behind nginx, or full URL for direct dev access
// If VITE_API_URL is set and starts with '/', use it as-is (relative)
// Otherwise, default to '/api' for nginx or use the env var if it's a full URL
let API_BASE_URL = import.meta.env.VITE_API_URL
if (!API_BASE_URL || API_BASE_URL.startsWith('/')) {
  API_BASE_URL = API_BASE_URL || '/api'
} else if (API_BASE_URL.includes('localhost/api')) {
  // If it's http://localhost/api, use relative path instead
  API_BASE_URL = '/api'
}

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export default client
