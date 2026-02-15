/**
 * 竞彩数据API接口
 */

import request from '@/utils/request';

// 获取竞彩数据列表
export function getCaiPiaoDataList(params) {
  return request({
    url: '/api/caipiao-data/',
    method: 'get',
    params
  });
}

// 根据ID获取竞彩数据
export function getCaiPiaoDataById(id) {
  return request({
    url: `/api/caipiao-data/${id}`,
    method: 'get'
  });
}

// 创建竞彩数据
export function createCaiPiaoData(data) {
  return request({
    url: '/api/caipiao-data/',
    method: 'post',
    data
  });
}

// 更新竞彩数据
export function updateCaiPiaoData(id, data) {
  return request({
    url: `/api/caipiao-data/${id}`,
    method: 'put',
    data
  });
}

// 删除竞彩数据
export function deleteCaiPiaoData(id) {
  return request({
    url: `/api/caipiao-data/${id}`,
    method: 'delete'
  });
}

// 从API同步竞彩数据
export function syncCaiPiaoDataFromApi(params) {
  return request({
    url: '/api/caipiao-data/sync-from-api/',
    method: 'post',
    params
  });
}

// 批量创建竞彩数据
export function batchCreateCaiPiaoData(data) {
  return request({
    url: '/api/caipiao-data/batch/',
    method: 'post',
    data
  });
}