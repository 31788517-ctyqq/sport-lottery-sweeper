/**
 * 对冲管理API
 */

import request from '@/utils/request'

// 获取二串一组合对冲机会
export function getParlayOpportunities(date) {
  // 使用模拟数据，直到后端API准备就绪
  if (process.env.NODE_ENV === 'development' || true) {
    // 返回模拟数据
    return new Promise((resolve) => {
      setTimeout(() => {
        const mockData = {
          date: date,
          opportunities: [
            {
              match1_id: 1,
              match1_home_team: '巴塞罗那',
              match1_away_team: '皇家马德里',
              match1_start_time: new Date(`${date}T15:00:00`).toISOString(),
              match1_sp_value: 3.2,
              match1_european_odd: 3.8,
              match2_id: 2,
              match2_home_team: '拜仁慕尼黑',
              match2_away_team: '多特蒙德',
              match2_start_time: new Date(`${date}T17:30:00`).toISOString(), // 确保比赛时间间隔大于1小时
              match2_sp_value: 2.8,
              match2_european_odd: 3.1,
              total_sp_odd: 3.2 * 2.8, // 8.96
              total_european_odd: 3.8 * 3.1, // 11.78
              investment_amount: 743.63,
              revenue_amount: 800.00,
              profit_amount: 56.37,
              profit_rate: 0.0564,
              is_profitable: true
            },
            {
              match1_id: 3,
              match1_home_team: '曼城',
              match1_away_team: '切尔西',
              match1_start_time: new Date(`${date}T18:00:00`).toISOString(),
              match1_sp_value: 2.5,
              match1_european_odd: 2.9,
              match2_id: 4,
              match2_home_team: '尤文图斯',
              match2_away_team: 'AC米兰',
              match2_start_time: new Date(`${date}T21:00:00`).toISOString(), // 确保比赛时间间隔大于1小时
              match2_sp_value: 3.0,
              match2_european_odd: 3.5,
              total_sp_odd: 2.5 * 3.0, // 7.5
              total_european_odd: 2.9 * 3.5, // 10.15
              investment_amount: 719.21,
              revenue_amount: 800.00,
              profit_amount: 80.79,
              profit_rate: 0.0808,
              is_profitable: true
            },
            // 添加符合新公式的示例数据
            {
              match1_id: 5,
              match1_home_team: '沙特联队',
              match1_away_team: '对手队A',
              match1_start_time: new Date(`${date}T14:00:00`).toISOString(),
              match1_sp_value: 1.434,
              match1_european_odd: 1.56,
              match2_id: 6,
              match2_home_team: '荷乙队',
              match2_away_team: '对手队B',
              match2_start_time: new Date(`${date}T17:30:00`).toISOString(), // 确保比赛时间间隔大于1小时
              match2_sp_value: 1.426,
              match2_european_odd: 1.62,
              total_sp_odd: 2.0468,
              total_european_odd: 2.52,
              investment_amount: 732,
              revenue_amount: 800.00,
              profit_amount: 68,
              profit_rate: 0.0393,
              is_profitable: true
            },
            {
              match1_id: 7,
              match1_home_team: '荷乙队',
              match1_away_team: '对手队C',
              match1_start_time: new Date(`${date}T15:00:00`).toISOString(),
              match1_sp_value: 1.874,
              match1_european_odd: 2.12,
              match2_id: 8,
              match2_home_team: '意甲队',
              match2_away_team: '对手队D',
              match2_start_time: new Date(`${date}T19:00:00`).toISOString(), // 确保比赛时间间隔大于1小时
              match2_sp_value: 2.406,
              match2_european_odd: 2.76,
              total_sp_odd: 4.5236,
              total_european_odd: 5.86,
              investment_amount: 738,
              revenue_amount: 800.00,
              profit_amount: 62,
              profit_rate: 0.0355,
              is_profitable: true
            }
          ],
          total_count: 4
        }
        resolve({ data: mockData })
      }, 300) // 模拟网络延迟
    })
  } else {
    // 生产环境使用真实API
    return request({
      url: `/hedging/parlay-opportunities?date=${date}`,
      method: 'get'
    })
  }
}

// 获取对冲配置
export function getHedgingConfig() {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ 
        data: {
          min_profit_rate: 0.02,
          commission_rate: 0.8,
          cost_factor: 0.2
        }
      })
    }, 200)
  })
}

// 手动计算对冲数据
export function calculateManualHedging(data) {
  return new Promise((resolve) => {
    setTimeout(() => {
      // 模拟计算
      const investment = data.investment || 1000
      const sp_odd = data.sp_odd
      const european_odd = data.european_odd
      
      const calculated_investment = investment * (sp_odd - 0.2) / european_odd
      const revenue = 0.8 * investment
      const profit = revenue - calculated_investment
      const profit_rate = profit / investment
      
      resolve({
        data: {
          investment: calculated_investment,
          revenue: revenue,
          profit: profit,
          profit_rate: profit_rate,
          is_profitable: profit_rate >= 0.02
        }
      })
    }, 200)
  })
}