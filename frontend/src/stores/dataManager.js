import { defineStore } from 'pinia'
import * as api from '@/api'

/**
 * 通用数据管理 Store
 * 用于管理列表数据、分页、筛选等状态
 */
export const useDataManagerStore = defineStore('dataManager', {
  state: () => ({
    // 列表数据
    list: [],
    // 当前页数据
    currentList: [],
    // 分页信息
    pagination: {
      currentPage: 1,
      pageSize: 20,
      total: 0,
      totalPages: 0
    },
    // 筛选条件
    filters: {},
    // 排序信息
    sortInfo: {
      field: '',
      order: '' // 'ascending' or 'descending'
    },
    // 加载状态
    loading: false,
    // 错误信息
    error: null,
    // 选中项
    selectedItems: [],
    // 编辑状态
    editingItem: null,
    // 是否为新建
    isNew: false
  }),

  getters: {
    // 获取当前页数据
    getCurrentPageData: (state) => {
      const start = (state.pagination.currentPage - 1) * state.pagination.pageSize
      const end = start + state.pagination.pageSize
      return state.list.slice(start, end)
    },

    // 获取选中项ID列表
    getSelectedIds: (state) => {
      return state.selectedItems.map(item => item.id)
    },

    // 获取选中项数量
    getSelectedCount: (state) => {
      return state.selectedItems.length
    }
  },

  actions: {
    /**
     * 获取列表数据
     * @param {string} apiModule - API模块名，对应 api/index.js 中的模块
     * @param {Object} params - 请求参数
     */
    async fetchList(apiModule, params = {}) {
      this.loading = true
      this.error = null

      try {
        // 合并分页、筛选、排序参数
        const requestParams = {
          page: this.pagination.currentPage,
          size: this.pagination.pageSize,
          ...this.filters,
          ...params
        }

        // 如果有排序信息，添加到请求参数
        if (this.sortInfo.field) {
          requestParams.sort = this.sortInfo.field
          requestParams.order = this.sortInfo.order === 'ascending' ? 'asc' : 'desc'
        }

        // 根据传入的API模块调用相应的方法
        let response
        if (typeof apiModule === 'function') {
          // 如果传入的是函数，直接调用
          response = await apiModule(requestParams)
        } else {
          // 如果传入的是字符串，按模块名查找
          const apiFunc = api[apiModule]
          if (!apiFunc) {
            throw new Error(`API module "${apiModule}" not found`)
          }
          response = await apiFunc(requestParams)
        }

        // 检查响应格式
        if (response.success !== undefined) {
          // 符合统一响应格式
          this.list = response.data || []
          this.pagination.total = response.total || 0
          this.pagination.totalPages = Math.ceil(this.pagination.total / this.pagination.pageSize)
        } else {
          // 不符合统一响应格式，直接赋值
          this.list = response
          this.pagination.total = response.length || 0
        }

        // 更新当前页数据
        this.currentList = this.getCurrentPageData

        return response
      } catch (error) {
        this.error = error.message
        console.error('获取列表数据失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 更新分页信息
     * @param {number} currentPage - 当前页
     * @param {number} pageSize - 每页大小
     */
    updatePagination(currentPage, pageSize) {
      this.pagination.currentPage = currentPage
      this.pagination.pageSize = pageSize
      // 更新当前页数据
      this.currentList = this.getCurrentPageData
    },

    /**
     * 更新筛选条件
     * @param {Object} filters - 筛选条件
     */
    updateFilters(filters) {
      this.filters = { ...this.filters, ...filters }
      // 重置到第一页
      this.pagination.currentPage = 1
    },

    /**
     * 更新排序信息
     * @param {string} field - 排序字段
     * @param {string} order - 排序顺序
     */
    updateSort(field, order) {
      this.sortInfo = { field, order }
    },

    /**
     * 选择项目
     * @param {Array} selection - 选中的项目
     */
    selectItems(selection) {
      this.selectedItems = [...selection]
    },

    /**
     * 清空选择
     */
    clearSelection() {
      this.selectedItems = []
    },

    /**
     * 设置编辑项
     * @param {Object} item - 要编辑的项目
     * @param {boolean} isNew - 是否为新建
     */
    setEditingItem(item, isNew = false) {
      this.editingItem = item ? { ...item } : null
      this.isNew = isNew
    },

    /**
     * 保存项目
     * @param {string} apiModule - API模块名，用于保存操作
     * @param {Object} item - 项目数据
     */
    async saveItem(apiModule, item) {
      this.loading = true
      this.error = null

      try {
        let response
        if (this.isNew) {
          // 新建
          response = await api[`${apiModule}Create`](item)
        } else {
          // 更新
          response = await api[`${apiModule}Update`](item.id, item)
        }

        // 如果保存成功，更新列表
        if (response.success) {
          if (this.isNew) {
            // 如果是新建，添加到列表开头
            this.list.unshift(response.data)
          } else {
            // 如果是更新，替换对应项
            const index = this.list.findIndex(i => i.id === item.id)
            if (index !== -1) {
              this.list.splice(index, 1, response.data)
            }
          }
          
          // 更新当前页数据
          this.currentList = this.getCurrentPageData
          
          // 更新总数
          this.pagination.total = this.list.length
          
          // 清空编辑状态
          this.setEditingItem(null)
        }

        return response
      } catch (error) {
        this.error = error.message
        console.error('保存项目失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 删除项目
     * @param {string} apiModule - API模块名
     * @param {number|string} id - 项目ID
     */
    async deleteItem(apiModule, id) {
      this.loading = true
      this.error = null

      try {
        const response = await api[`${apiModule}Delete`](id)

        if (response.success) {
          // 从列表中移除
          this.list = this.list.filter(item => item.id !== id)
          
          // 更新当前页数据
          this.currentList = this.getCurrentPageData
          
          // 更新总数
          this.pagination.total = this.list.length
        }

        return response
      } catch (error) {
        this.error = error.message
        console.error('删除项目失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 批量删除
     * @param {string} apiModule - API模块名
     * @param {Array} ids - 要删除的ID列表
     */
    async batchDelete(apiModule, ids) {
      this.loading = true
      this.error = null

      try {
        const response = await api[`${apiModule}BatchDelete`](ids)

        if (response.success) {
          // 从列表中移除
          this.list = this.list.filter(item => !ids.includes(item.id))
          
          // 更新当前页数据
          this.currentList = this.getCurrentPageData
          
          // 更新总数
          this.pagination.total = this.list.length
          
          // 清空选择
          this.clearSelection()
        }

        return response
      } catch (error) {
        this.error = error.message
        console.error('批量删除失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 刷新数据
     */
    async refresh(apiModule) {
      return await this.fetchList(apiModule)
    },

    /**
     * 重置状态
     */
    reset() {
      this.list = []
      this.currentList = []
      this.pagination = {
        currentPage: 1,
        pageSize: 20,
        total: 0,
        totalPages: 0
      }
      this.filters = {}
      this.sortInfo = {
        field: '',
        order: ''
      }
      this.error = null
      this.selectedItems = []
      this.editingItem = null
      this.isNew = false
    }
  }
})