import request from '@/utils/request'

export function standardizeMatchData(rawData, sourceId) {
  return request({
    url: `/api/v1/entity-mapping/matches/standardize`,
    method: 'post',
    params: { source_id: sourceId },
    data: rawData
  })
}

export function getEntityMappings(entityType) {
  return request({
    url: `/api/v1/entity-mapping/mappings/${entityType}`,
    method: 'get'
  })
}

export function updateEntityMapping(entityType, entityId, updates) {
  return request({
    url: `/api/v1/entity-mapping/mappings/${entityType}/${entityId}`,
    method: 'put',
    data: updates
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
