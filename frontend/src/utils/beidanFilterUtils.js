/**
 * 工具函数，用于处理BeidanFilterPanel中的逻辑
 */

// 计算实力等级差
export function calcDeltaPLevel(homePower, awayPower) {
  if (homePower === '-' || awayPower === '-') return 0;
  const diff = Number(homePower) - Number(awayPower);
  if (diff > 25) return 3;
  if (diff >= 17) return 2;
  if (diff >= 9) return 1;
  if (diff >= -8) return 0;
  if (diff >= -16) return -1;
  if (diff >= -25) return -2;
  return -3;
}

// 计算赢盘等级差
export function calcDeltaWp(homeWp, awayWp) {
  const wpToScore = (wp) => {
    const value = Number(wp);
    if (Number.isNaN(value)) return 0;
    if (value > 1.4) return 4;
    if (value >= 1.2) return 3;
    if (value >= 0.8) return 2;
    if (value >= 0.6) return 1;
    return 0;
  };

  const homeScore = wpToScore(homeWp);
  const awayScore = wpToScore(awayWp);
  return homeScore - awayScore;
}

// 计算稳定性等级
export function calcStabilityTier(homeFeature, guestFeature) {
  const homeText = homeFeature || '';
  const guestText = guestFeature || '';
  const parsePercents = (text) => {
    if (!text) return [];
    const matches = String(text).match(/(\d+(?:\.\d+)?)%/g) || [];
    return matches.map((m) => Number(m.replace('%', ''))).filter((v) => !Number.isNaN(v));
  };
  
  const homePercents = parsePercents(homeText);
  const guestPercents = parsePercents(guestText);
  const homeOne = /一赔/.test(homeText) ? (homePercents[0] || 0) : null;
  const guestOne = /一赔/.test(guestText) ? (guestPercents[0] || 0) : null;

  if (homeOne !== null && guestOne !== null) {
    const pValue = homeOne + guestOne;
    if (pValue >= 140) return { tier: 'S', pLevel: 1 };
    if (pValue >= 110) return { tier: 'A', pLevel: 2 };
    return { tier: 'B-', pLevel: 4 };
  }

  if (homeOne !== null || guestOne !== null) {
    const oneValue = homeOne !== null ? homeOne : guestOne;
    const opponentPercents = homeOne !== null ? guestPercents : homePercents;
    const opponentMax = opponentPercents.length ? Math.max(...opponentPercents) : 0;
    const pValue = oneValue - opponentMax;
    if (pValue >= 40) return { tier: 'B', pLevel: 3 };
    if (pValue >= 15) return { tier: 'C', pLevel: 5 };
    if (pValue >= 0) return { tier: 'D', pLevel: 6 };
    return { tier: 'E', pLevel: 7 };
  }

  return { tier: 'E', pLevel: 7 };
}

// 格式化比赛时间
export function formatMatchTime(value) {
  if (!value) return '-';
  
  // 如果已经是格式化好的字符串，直接返回
  if (typeof value === 'string' && /^\d{4}\/\d{2}\/\d{2} \d{2}:\d{2}:\d{2}$/.test(value)) {
    return value;
  }
  
  // 尝试解析各种可能的日期格式
  let date;
  if (value instanceof Date) {
    date = value;
  } else if (typeof value === 'string') {
    // 尝试处理ISO格式
    if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(value)) {
      date = new Date(value);
    } 
    // 尝试处理YYYY-MM-DD格式
    else if (/^\d{4}-\d{2}-\d{2}/.test(value)) {
      date = new Date(value);
    }
    // 尝试处理时间戳
    else if (/^\d+$/.test(value)) {
      date = new Date(parseInt(value, 10));
    } else {
      return value;
    }
  } else if (typeof value === 'number') {
    date = new Date(value);
  } else {
    return String(value);
  }
  
  // 验证日期是否有效
  if (Number.isNaN(date.getTime())) {
    return String(value);
  }
  
  const pad = (num) => String(num).padStart(2, '0');
  return `${date.getFullYear()}/${pad(date.getMonth() + 1)}/${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

// 数据标准化函数
export function normalizeMatches(matches = [], dateTime = null) {
  return matches.map((item, index) => {
    const matchId = item.match_id || item.id || item.lineId || item.line_id || `match-${index}`;
    const raw = item.source_attributes || item.sourceAttributes || item.raw_data || item.rawData || null;
    const homeTeam = (raw && raw.homeTeam) || item.home_team || item.homeTeam || item.home || '-';
    const awayTeam = (raw && raw.guestTeam) || item.away_team || item.awayTeam || item.guestTeam || item.guest_team || item.away || '-';
    const league = (raw && raw.gameShortName) || item.league || item.gameShortName || item.leagueName || '-';
    const matchTime = (raw && raw.matchTimeStr) || item.match_time || item.matchTime || item.startTime || item.matchDate || '-';
    const powerHome = (raw && raw.homePower) || item.power_home || item.powerHome || item.homePower || item.home_power || '-';
    const powerAway = (raw && raw.guestPower) || item.power_away || item.powerAway || item.guestPower || item.awayPower || item.away_power || '-';
    const winPanHome = (raw && raw.homeWinPan) || item.win_pan_home || item.winPanHome || item.homeWinPan || item.home_win_pan || '-';
    const winPanAway = (raw && raw.guestWinPan) || item.win_pan_away || item.winPanAway || item.guestWinPan || item.awayWinPan || item.away_win_pan || '-';
    const homeFeature = (raw && raw.homeFeature) || item.home_feature || item.homeFeature || '-';
    const awayFeature = (raw && raw.guestFeature) || item.away_feature || item.awayFeature || item.guestFeature || item.guest_feature || '-';
    
    // 只有当powerHome/powerAway是有效数字时才计算派生值
    let deltaPLevel, powerDiff;
    if (powerHome !== '-' && powerAway !== '-' && !isNaN(parseFloat(powerHome)) && !isNaN(parseFloat(powerAway))) {
      deltaPLevel = calcDeltaPLevel(parseFloat(powerHome), parseFloat(powerAway));
      powerDiff = deltaPLevel;
    } else {
      deltaPLevel = 0;
      powerDiff = 0;
    }
    
    // 只有当winPanHome/winPanAway是有效数字时才计算winPanDiff
    let deltaWp, winPanDiff;
    if (winPanHome !== '-' && winPanAway !== '-' && !isNaN(parseFloat(winPanHome)) && !isNaN(parseFloat(winPanAway))) {
      deltaWp = calcDeltaWp(parseFloat(winPanHome), parseFloat(winPanAway));
      winPanDiff = deltaWp;
    } else {
      deltaWp = 0;
      winPanDiff = 0;
    }
    
    // 计算稳定性等级和P级
    const stabilityResult = calcStabilityTier(homeFeature, awayFeature);
    const stabilityValue = stabilityResult.tier;
    const pLevel = stabilityResult.pLevel;
    
    const lineId = (raw && raw.lineId) || item.lineId || item.line_id || matchId;
    
    // 现在match_id采用date_time_lineId格式，直接使用
    const formattedMatchId = item.match_id || String(matchId);
    const dateTimeFromRaw = (raw && raw.date_time) || (raw && raw.dateTime) || (raw && raw['date_time']);
    let dateTimePart = dateTimeFromRaw || dateTime || null; // 这里需要引用外部的filterForm，暂时设为null
    
    // 如果还没有dateTimePart，尝试从matchTime中提取YYMMDD格式
    if (!dateTimePart && matchTime) {
      try {
        const dateStr = String(matchTime).split('T')[0];
        const yearMatch = dateStr.match(/^(\d{4})-(\d{2})-(\d{2})$/);
        if (yearMatch) {
          const [, year, month, day] = yearMatch;
          const yy = year.slice(-2);
          // 统一使用两位数的日期格式：YYMMDD
          dateTimePart = `${yy}${month}${day}`;
        }
      } catch (e) {
        console.warn('Failed to extract date_time from matchTime:', matchTime, e);
      }
    }
    
    // 如果还是没有dateTimePart，回退到原有的逻辑
    if (!dateTimePart) {
      const dateStr = String(matchTime || '').split('T')[0];
      const parts = dateStr.split('-');
      if (parts.length === 3) {
        const yy = parts[0].slice(-2);
        dateTimePart = `${yy}${parts[1]}${parts[2]}`;
      } else {
        dateTimePart = dateStr.replace(/-/g, '').slice(2);
      }
    }
    
    return {
      match_id: formattedMatchId,
      home_team: homeTeam,
      away_team: awayTeam,
      league,
      match_time: matchTime,
      power_home: powerHome,
      power_away: powerAway,
      win_pan_home: winPanHome,
      win_pan_away: winPanAway,
      home_feature: homeFeature,
      away_feature: awayFeature,
      p_level: pLevel,
      delta_wp: deltaWp,
      power_diff: powerDiff,
      win_pan_diff: winPanDiff,
      stability: stabilityValue,
      source_attributes: item.source_attributes || item.sourceAttributes || item.raw_data || item.rawData || null
    }
  });
}