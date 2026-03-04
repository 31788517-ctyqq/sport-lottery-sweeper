import request from '@/utils/request'

export function getKaggleSyncStatus() {
  return request({
    url: '/api/v1/admin/kaggle-sync/status',
    method: 'get'
  })
}

export function getKaggleDatasets(params = {}) {
  return request({
    url: '/api/v1/admin/kaggle-sync/datasets',
    method: 'get',
    params
  })
}

export function createKaggleDataset(data) {
  return request({
    url: '/api/v1/admin/kaggle-sync/datasets',
    method: 'post',
    data
  })
}

export function updateKaggleDataset(datasetId, data) {
  return request({
    url: `/api/v1/admin/kaggle-sync/datasets/${datasetId}`,
    method: 'patch',
    data
  })
}

export function getKaggleRuns(params = {}) {
  return request({
    url: '/api/v1/admin/kaggle-sync/runs',
    method: 'get',
    params
  })
}

export function getKaggleRunDetail(runIdentifier) {
  return request({
    url: `/api/v1/admin/kaggle-sync/runs/${runIdentifier}`,
    method: 'get'
  })
}

export function getKaggleRunQuality(runIdentifier) {
  return request({
    url: `/api/v1/admin/kaggle-sync/runs/${runIdentifier}/quality`,
    method: 'get'
  })
}

export function getKaggleDatasetPreview(datasetId, params = {}) {
  return request({
    url: `/api/v1/admin/kaggle-sync/datasets/${datasetId}/preview`,
    method: 'get',
    params
  })
}

export function rebuildKaggleDataset(datasetId, data = {}) {
  return request({
    url: `/api/v1/admin/kaggle-sync/datasets/${datasetId}/rebuild`,
    method: 'post',
    data
  })
}

export function runKaggleSyncNow(data = {}) {
  return request({
    url: '/api/v1/admin/kaggle-sync/run-now',
    method: 'post',
    data
  })
}

export function runKaggleMergeBackfillNow(data = {}) {
  return request({
    url: '/api/v1/admin/kaggle-sync/merge-backfill-now',
    method: 'post',
    data
  })
}
