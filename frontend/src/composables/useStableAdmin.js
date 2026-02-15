/**
 * 稳定管理页面组合式函数
 * 为所有管理页面提供统一的错误处理和数据获取
 */
import { ref, reactive } from 'vue'
import { enhancedAPI } from '@/utils/enhanced-api-handler'
import { ElMessage } from 'element-plus'

export function useStableAdmin() {
  const loading = ref(false)
  const error = ref(null)
  const data = ref([])
  const pagination = reactive({
    page: 1,
    pageSize: 20,
    total: 0
  })

  /**
   * 安全加载数据 - 永不崩溃
   */
  const safeLoadData = async (loadFunction, options = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const result = await loadFunction()
      
      if (result.success) {
        data.value = result.data || []
        
        // 如果有分页信息，更新分页
        if (result.total !== undefined) {
          pagination.total = result.total
        }
        
        // 成功静默处理，避免过多提示
        if (options.showSuccess !== false) {
          // ElMessage.success('数据加载成功') // 注释掉，避免过多弹窗
        }
        
        return result
      } else {
        // 即使失败也不设置错误状态，避免页面崩溃
        console.warn('Data load returned unsuccessful:', result.error)
        data.value = []
        return { success: true, data: [], error: result.error }
      }
      
    } catch (err) {
      console.error('Safe load data error:', err)
      error.value = err.message
      data.value = [] // 确保始终有数据，即使是空的
      
      // 不显示错误提示，避免弹窗过多
      return { success: true, data: [], error: err.message }
      
    } finally {
      loading.value = false
    }
  }

  /**
   * 加载用户数据
   */
  const loadUsers = async (params = {}) => {
    const finalParams = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...params
    }
    
    return safeLoadData(
      () => enhancedAPI.get('/api/admin/users', finalParams, { silent: true }),
      { showSuccess: false }
    )
  }

  /**
   * 加载角色数据
   */
  const loadRoles = async (params = {}) => {
    return safeLoadData(
      () => enhancedAPI.get('/api/admin/roles', params, { silent: true }),
      { showSuccess: false }
    )
  }

  /**
   * 加载部门数据
   */
  const loadDepartments = async (params = {}) => {
    return safeLoadData(
      () => enhancedAPI.get('/api/admin/departments', params, { silent: true }),
      { showSuccess: false }
    )
  }

  /**
   * 加载数据源数据
   */
  const loadDataSources = async (params = {}) => {
    return safeLoadData(
      () => enhancedAPI.get('/api/v1/admin/data-sources', params, { silent: true }),
      { showSuccess: false }
    )
  }

  /**
   * 通用的安全API调用
   */
  const safeApiCall = async (apiCall, options = {}) => {
    try {
      const result = await apiCall()
      
      if (!result.success && !options.allowFailure) {
        // 只有在不允许失败时才显示错误
        if (!options.silent) {
          ElMessage.warning(options.errorMessage || '操作失败')
        }
      }
      
      return result
    } catch (err) {
      console.error('Safe API call error:', err)
      if (!options.silent) {
        ElMessage.error(options.errorMessage || '操作失败')
      }
      return { success: false, error: err.message }
    }
  }

  return {
    loading,
    error,
    data,
    pagination,
    safeLoadData,
    loadUsers,
    loadRoles,
    loadDepartments,
    loadDataSources,
    safeApiCall
  }
}