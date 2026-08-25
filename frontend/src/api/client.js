import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const client = axios.create({ baseURL: API_BASE_URL })

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('cp_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const api = {
  register: (data) => client.post('/auth/register', data).then(r => r.data),
  login: (data) => client.post('/auth/login', data).then(r => r.data),
  me: () => client.get('/auth/me').then(r => r.data),

  uploadResume: (file) => {
    const form = new FormData()
    form.append('file', file)
    return client.post('/resumes/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(r => r.data)
  },
  listResumes: () => client.get('/resumes').then(r => r.data),

  createJD: (data) => client.post('/job-descriptions', data).then(r => r.data),
  listJDs: () => client.get('/job-descriptions').then(r => r.data),

  runPipeline: (data) => client.post('/pipeline/run', data).then(r => r.data),
  getPipelineStatus: (runId) => client.get(`/pipeline/${runId}/status`).then(r => r.data),
  approveTailoring: (runId, data) => client.post(`/pipeline/${runId}/approve-tailoring`, data).then(r => r.data),
  getTailoredResume: (runId) => client.get(`/pipeline/${runId}/tailored-resume`).then(r => r.data),
  downloadTailoredResume: (runId) => client.get(`/pipeline/${runId}/tailored-resume/download`, {
    responseType: 'blob',
  }),
  getBattlecard: (runId) => client.get(`/pipeline/${runId}/battlecard`).then(r => r.data),
  submitMockAnswer: (runId, data) => client.post(`/pipeline/${runId}/mock-interview/answer`, data).then(r => r.data),
  getSalaryNegotiation: (runId) => client.get(`/pipeline/${runId}/salary-negotiation`).then(r => r.data),
  getActionPlan: (runId) => client.get(`/pipeline/${runId}/action-plan`).then(r => r.data),
  getElevatorPitch: (runId) => client.get(`/pipeline/${runId}/elevator-pitch`).then(r => r.data),
}

export default client
