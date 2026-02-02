import axios from 'axios';

// Use same hostname as frontend for network access
const API_URL = `http://${window.location.hostname}:5005/api`;

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const authService = {
  // Only check if file exists and get password (no validation)
  checkCredentials: (username) => api.post('/auth/check-credentials', { username }),
  login: (username, password) => api.post('/auth/login', { username, password }),
  submitOtp: (otp) => api.post('/auth/submit-otp', { otp }),
  clearOtp: () => api.post('/auth/clear-otp'),
  checkStatus: () => api.get('/auth/status'),
  logout: () => api.post('/auth/logout'),
};

export const surveyService = {
  getAll: () => api.get('/surveys'),
  getDetail: (id) => api.get(`/surveys/${id}`),
  getUserRole: (surveyId, periodId) => api.get(`/surveys/${surveyId}/role/${periodId}`),
};

export const regionService = {
  getProvinsi: (groupId) => api.get(`/regions/provinsi?groupId=${groupId}`),
  getKabupaten: (groupId, provFullCode) => api.get(`/regions/kabupaten?groupId=${groupId}&provFullCode=${provFullCode}`),
  getKecamatan: (groupId, kabId) => api.get(`/regions/kecamatan?groupId=${groupId}&kabId=${kabId}`),
  getDesa: (groupId, kecId) => api.get(`/regions/desa?groupId=${groupId}&kecId=${kecId}`),
  getSls: (groupId, desaId) => api.get(`/regions/sls?groupId=${groupId}&desaId=${desaId}`),
};

export const wilayahService = {
  checkStatus: (surveyId, periodId, kabId) =>
    api.get(`/wilayah/status?surveyId=${surveyId}&periodId=${periodId}&kabId=${kabId}`),
  fetch: (data) => api.post('/wilayah/fetch', data),
};

export const actionService = {
  getColumns: (surveyName) => api.get(`/action/get-columns?surveyName=${encodeURIComponent(surveyName || '')}`),
  getFileColumns: (filename) => api.get(`/action/get-file-columns/${encodeURIComponent(filename)}`),
  getHistory: () => api.get('/action/history'),
  downloadRaw: (data) => api.post('/action/download-raw', data),
  exportFiltered: (filename, selectedColumns) => api.post(`/action/export-filtered/${encodeURIComponent(filename)}`, { selectedColumns }),
  approve: (data) => api.post('/action/approve', data),
  revoke: (data) => api.post('/action/revoke', data),
  reject: (data) => api.post('/action/reject', data),
  getProgress: (taskId) => api.get(`/action/progress/${taskId}`),
  getDownloadUrl: (filename) => `${API_URL}/action/download-file/${filename}`,
};

export default api;
