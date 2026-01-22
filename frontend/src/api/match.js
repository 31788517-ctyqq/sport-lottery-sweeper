/**
 * 比赛数据API
 */

import request from '@/utils/request'

/**
 * 获取近期比赛数据
 * @param {number} daysAhead - 获取未来几天的比赛，默认3天
 * @returns {Promise}
 */
export function getRecentMatches(daysAhead = 3) {
  return request({
    url: `/api/v1/public/matches/?days_ahead=${daysAhead}`,
    method: 'get'
  })
}

/**
 * 获取热门比赛
 * @returns {Promise}
 */
export function getPopularMatches() {
  return request({
    url: '/api/v1/public/matches/popular',
    method: 'get'
  })
}

/**
 * 获取比赛详情
 * @param {string} matchId - 比赛ID
 * @returns {Promise}
 */
export function getMatchDetail(matchId) {
  return request({
    url: `/api/v1/matches/${matchId}`,
    method: 'get'
  })
}

/**
 * 获取趋势比赛
 * @returns {Promise}
 */
export function getTrendingMatches() {
  return request({
    url: '/api/v1/matches/trending',
    method: 'get'
  })
}

/**
 * 获取联赛积分榜
 * @param {string} league - 联赛名称
 * @returns {Promise}
 */
export function getLeagueStandings(league) {
  return request({
    url: `/api/v1/matches/standings/${league}`,
    method: 'get'
  })
}