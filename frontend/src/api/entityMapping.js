import request from '@/utils/request'

export function standardizeMatchData(rawData, sourceId) {
  return request({
    url: `/api/v1/entity-mapping/matches/standardize`,
    method: 'post',
    params: { source_id: sourceId },
    data: rawData
  })
}

export function getEntityMappings(entityType, params = {}) {
  return request({
    url: `/api/v1/entity-mapping/mappings/${entityType}`,
    method: 'get',
    params
  })
}

export function updateEntityMapping(entityType, entityId, updates) {
  return request({
    url: `/api/v1/entity-mapping/mappings/${entityType}/${entityId}`,
    method: 'put',
    data: updates
  })
}

export function getEntityMappingConflicts(entityType, params = {}) {
  return request({
    url: `/api/v1/entity-mapping/conflicts/${entityType}`,
    method: 'get',
    params
  })
}

export function reviewEntityMapping(entityType, entityId, payload = {}) {
  return request({
    url: `/api/v1/entity-mapping/review/${entityType}/${entityId}`,
    method: 'post',
    data: payload
  })
}

export function getOfficialInfoSummary() {
  return request({
    url: '/api/v1/entity-mapping/official-info/summary',
    method: 'get'
  })
}

export function verifyOfficialInfo(entityType, entityId) {
  return request({
    url: `/api/v1/entity-mapping/official-info/verify/${entityType}/${entityId}`,
    method: 'post'
  })
}

export function verifyOfficialInfoAll(entityType = 'all') {
  return request({
    url: '/api/v1/entity-mapping/official-info/verify-all',
    method: 'post',
    params: { entity_type: entityType }
  })
}

export function discoverOfficialInfo(entityType, entityId) {
  return request({
    url: `/api/v1/entity-mapping/official-info/discover/${entityType}/${entityId}`,
    method: 'post'
  })
}

export function discoverOfficialInfoAll(entityType = 'all') {
  return request({
    url: '/api/v1/entity-mapping/official-info/discover-all',
    method: 'post',
    params: { entity_type: entityType }
  })
}

export function updateOfficialInfo(entityType, entityId, updates) {
  return request({
    url: `/api/v1/entity-mapping/official-info/${entityType}/${entityId}`,
    method: 'put',
    data: updates
  })
}

export function getEntityMappingSyncStatus() {
  return request({
    url: '/api/v1/entity-mapping/sync/status',
    method: 'get'
  })
}

export function triggerEntityMappingSync() {
  return request({
    url: '/api/v1/entity-mapping/sync/trigger',
    method: 'post'
  })
}
