import request from '@/utils/request'

// 获取比赛列表
export function getMatchList(params) {
  return request({
    url: '/api/admin/matches',
    method: 'get',
    params
  })
}

// 新增比赛
export function createMatch(data) {
  return request({
    url: '/api/admin/matches',
    method: 'post',
    data
  })
}

// 删除比赛
export function deleteMatch(id) {
  return request({
    url: `/api/admin/matches/${id}`,
    method: 'delete'
  })
}
