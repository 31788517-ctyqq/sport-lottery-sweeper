/**
 * Storage Keys Constants
 * 统一管理本地存储键名，避免硬编码和冲突
 */

export const STORAGE_KEYS = {
  // Authentication
  AUTH_TOKEN: 'auth_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_PROFILE: 'user_profile',
  USER_PERMISSIONS: 'user_permissions',
  
  // Theme & UI
  THEME_PREFERENCE: 'app_theme_preference',
  LANGUAGE: 'app_language',
  SIDEBAR_COLLAPSED: 'sidebar_collapsed',
  
  // User Preferences
  FAVORITE_MATCHES: 'favorite_matches',
  RECENT_SEARCHES: 'recent_searches',
  FILTER_SETTINGS: 'filter_settings',
  TABLE_COLUMNS: 'table_columns_config',
  
  // Cache
  MATCH_CACHE: 'match_data_cache',
  ODDS_CACHE: 'odds_data_cache',
  LEAGUE_CACHE: 'league_list_cache',
  
  // Temporary
  DRAFT_FORM: 'draft_form_data',
  TOUR_COMPLETED: 'onboarding_tour_completed',
  NOTIFICATIONS_READ: 'notifications_read_ids'
};

/**
 * Storage Key Prefixes
 * 用于动态生成带前缀的键名
 */
export const STORAGE_PREFIXES = {
  USER: 'user_',
  CACHE: 'cache_',
  TEMP: 'temp_',
  CONFIG: 'config_'
};

/**
 * 生成带前缀的存储键
 * @param {string} prefix - 前缀
 * @param {string} key - 键名
 * @returns {string} 完整的存储键
 */
export function createStorageKey(prefix, key) {
  return `${prefix}${key}`;
}

/**
 * 生成用户特定的存储键
 * @param {string|number} userId - 用户ID
 * @param {string} key - 键名
 * @returns {string} 用户特定的存储键
 */
export function createUserStorageKey(userId, key) {
  return `${STORAGE_PREFIXES.USER}${userId}_${key}`;
}

export default STORAGE_KEYS;
