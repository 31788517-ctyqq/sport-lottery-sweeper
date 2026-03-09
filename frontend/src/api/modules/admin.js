/**
 * 管理后台专用API
 */
import client from '../client';

export const adminAPI = {
  // --- 用户管理 ---
  getUsers(params = {}) {
    return client.get('/admin/users', { params });
  },
  createUser(userData) {
    return client.post('/admin/users', userData);
  },
  updateUser(id, userData) {
    return client.put(`/admin/users/${id}`, userData);
  },
  deleteUser(id) {
    return client.delete(`/admin/users/${id}`);
  },

  // --- 数据源管理 ---
  getDataSources(params = {}) {
    return client.get('/admin/data-sources', { params });
  },
  createDataSource(sourceData) {
    return client.post('/admin/data-sources', sourceData);
  },
  updateDataSource(id, sourceData) {
    return client.put(`/admin/data-sources/${id}`, sourceData);
  },
  deleteDataSource(id) {
    return client.delete(`/admin/data-sources/${id}`);
  },
  testConnection(id) {
    return client.post(`/admin/data-sources/${id}/test-connection`);
  },

  // --- 比赛管理 ---
  getAdminMatches(params = {}) {
    return client.get('/admin/matches', { params });
  },
  createMatch(matchData) {
    return client.post('/admin/matches', matchData);
  },
  updateMatch(id, matchData) {
    return client.put(`/admin/matches/${id}`, matchData);
  },
  deleteMatch(id) {
    return client.delete(`/admin/matches/${id}`);
  },

  // --- 情报管理 ---
  getAdminIntelligence(params = {}) {
    return client.get('/admin/intelligence', { params });
  },
  createIntelligence(reportData) {
    return client.post('/admin/intelligence', reportData);
  },
  updateIntelligence(id, reportData) {
    return client.put(`/admin/intelligence/${id}`, reportData);
  },
  deleteIntelligence(id) {
    return client.delete(`/admin/intelligence/${id}`);
  },
  publishIntelligence(id) {
    return client.post(`/admin/intelligence/${id}/publish`);
  },
  archiveIntelligence(id) {
    return client.post(`/admin/intelligence/${id}/archive`);
  },

  // --- 数据质量 ---
  getQualityMetrics(params = {}) {
    return client.get('/admin/data-quality/metrics', { params });
  },
  runQualityCheck(sourceId) {
    return client.post(`/admin/data-quality/run-check/${sourceId}`);
  },

  // --- 系统配置 ---
  getSystemConfig() {
    return client.get('/admin/system/config');
  },
  updateSystemConfig(configData) {
    return client.put('/admin/system/config', configData);
  },

  // --- API管理 ---
  getAPIList(params = {}) {
    return client.get('/admin/api', { params });
  },
  toggleAPIStatus(apiId, enabled) {
    return client.patch(`/admin/api/${apiId}/status`, { enabled });
  },
  createAPI(apiData) {
    return client.post('/admin/api', apiData);
  },
  updateAPI(id, apiData) {
    return client.put(`/admin/api/${id}`, apiData);
  },
  deleteAPI(id) {
    return client.delete(`/admin/api/${id}`);
  },

  // --- 日志管理 ---
  getSystemLogs(params = {}) {
    return client.get('/admin/logs', { params });
  },

  // --- 备份恢复 ---
  getBackupHistory(params = {}) {
    return client.get('/admin/backups', { params });
  },
  createBackup(backupData) {
    return client.post('/admin/backups', backupData);
  },
  restoreFromBackup(backupId) {
    return client.post(`/admin/backups/${backupId}/restore`);
  },
  downloadBackup(backupId) {
    // 返回一个可下载的URL或者使用fetch处理blob
    return `${client.defaults.baseURL}/admin/backups/${backupId}/download`;
    // 或者 return client.get(`/admin/backups/${backupId}/download`, { responseType: 'blob' });
  },
  deleteBackup(backupId) {
    return client.delete(`/admin/backups/${backupId}`);
  },

  // --- 监控 ---
  getSystemMetrics() {
    return client.get('/admin/monitoring/metrics');
  },
  getServerLogs(params = {}) {
    return client.get('/admin/monitoring/server-logs', { params });
  },

  // 兼容别名方法
  getUsersList(params = {}) {
    return this.getUsers(params);
  },

  getOperationLogs(params = {}) {
    return this.getSystemLogs(params);
  },

  getStats() {
    return this.getSystemMetrics();
  },

  updateUserStatus(userId, status) {
    return this.updateUser(userId, { status });
  },
};

// 解构所有方法
export const {
  getUsers: adminGetUsers,
  createUser: adminCreateUser,
  updateUser: adminUpdateUser,
  deleteUser: adminDeleteUser,
  getDataSources: adminGetDataSources,
  createDataSource: adminCreateDataSource,
  updateDataSource: adminUpdateDataSource,
  deleteDataSource: adminDeleteDataSource,
  testConnection: adminTestConnection,
  getAdminMatches: adminGetMatches,
  createMatch: adminCreateMatch,
  updateMatch: adminUpdateMatch,
  deleteMatch: adminDeleteMatch,
  getAdminIntelligence: adminGetIntelligence,
  createIntelligence: adminCreateIntelligence,
  updateIntelligence: adminUpdateIntelligence,
  deleteIntelligence: adminDeleteIntelligence,
  publishIntelligence: adminPublishIntelligence,
  archiveIntelligence: adminArchiveIntelligence,
  getQualityMetrics: adminGetQualityMetrics,
  runQualityCheck: adminRunQualityCheck,
  getSystemConfig: adminGetSystemConfig,
  updateSystemConfig: adminUpdateSystemConfig,
  getAPIList: adminGetAPIList,
  toggleAPIStatus: adminToggleAPIStatus,
  createAPI: adminCreateAPI,
  updateAPI: adminUpdateAPI,
  deleteAPI: adminDeleteAPI,
  getSystemLogs: adminGetSystemLogs,
  getBackupHistory: adminGetBackupHistory,
  createBackup: adminCreateBackup,
  restoreFromBackup: adminRestoreFromBackup,
  downloadBackup: adminDownloadBackup,
  deleteBackup: adminDeleteBackup,
  getSystemMetrics: adminGetSystemMetrics,
  getServerLogs: adminGetServerLogs,
  getUsersList: adminGetUsersList,
  getOperationLogs: adminGetOperationLogs,
  getStats: adminGetStats,
  updateUserStatus: adminUpdateUserStatus,
} = adminAPI;