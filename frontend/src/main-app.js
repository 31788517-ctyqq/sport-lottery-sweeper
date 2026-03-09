// ============================================
// 应用状态管理
// ============================================
const AppState = {
    currentFilter: {
        type: null,
        source: null,
        weight: null,
        league: null,
        timeRange: null
    },
    currentType: 'all', // 当前显示的情报类型
    currentSort: 'time', // time, weight
    filteredMatches: [],
    allMatches: []
};

// ============================================
// 模拟数据配置
// ============================================
const MockConfig = {
    intelligenceTypes: [
        { id: 'sp', name: '赔率变动', icon: 'fas fa-chart-line', color: 'var(--tag-sp)' },
        { id: 'injury', name: '伤病情报', icon: 'fas fa-user-injured', color: 'var(--tag-injury)' },
        { id: 'weather', name: '天气影响', icon: 'fas fa-cloud-rain', color: 'var(--tag-weather)' },
        { id: 'referee', name: '裁判信息', icon: 'fas fa-whistle', color: 'var(--tag-referee)' },
        { id: 'motive', name: '战意分析', icon: 'fas fa-fire', color: 'var(--tag-motive)' },
        { id: 'schedule', name: '赛程密集', icon: 'fas fa-calendar-day', color: 'var(--tag-schedule)' },
        { id: 'tactics', name: '战术分析', icon: 'fas fa-chess', color: 'var(--tag-tactics)' },
        { id: 'coach', name: '教练变动', icon: 'fas fa-chalkboard-teacher', color: 'var(--tag-coach)' },
        { id: 'history', name: '历史交锋', icon: 'fas fa-history', color: 'var(--tag-history)' },
        { id: 'prediction', name: '预测分析', icon: 'fas fa-brain', color: 'var(--tag-prediction)' },
        { id: 'atmosphere', name: '氛围影响', icon: 'fas fa-users', color: 'var(--tag-atmosphere)' },
        { id: 'other', name: '其他情报', icon: 'fas fa-info-circle', color: 'var(--tag-other)' }
    ],
    sources: [
        { id: 'official', name: '官方', color: 'var(--source-official)' },
        { id: 'media', name: '媒体', color: 'var(--source-media)' },
        { id: 'social', name: '社媒', color: 'var(--source-social)' },
        { id: 'bookmaker', name: '机构', color: 'var(--source-bookmaker)' }
    ],
    weights: [
        { id: 'high', name: '高', threshold: 8.0 },
        { id: 'medium', name: '中', threshold: 6.0 },
        { id: 'low', name: '低', threshold: 0 }
    ],
    leagues: [
        '英超', '西甲', '德甲', '意甲', '法甲', 
        '中超', '日职联', '韩K联', 
        '欧冠', '欧联', '欧协联',
        '世界杯', '欧洲杯', '美洲杯'
    ],
    generation: {
        totalMatches: 15,
        intelPerMatch: { min: 3, max: 7 },
        newIntelRatio: 0.3,
        highWeightRatio: 0.2,
        mediumWeightRatio: 0.5
    }
};

// ============================================
// 用户数据
// ============================================
const UserData = {
    username: '竞彩玩家',
    userId: 'JC2026001',
    level: 'VIP 3级会员',
    registerDate: '2024-01-15',
    usageDuration: '128天',
    totalViews: 12847,
    correctPredictions: 76.3,
    streakDays: 8,
    followCount: 1247,
    favoriteCount: 89,
    isLoggedIn: false,
    avatarSeed: 'default',
    settings: {
        notifications: true,
        darkMode: true
    }
};

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    // 生成模拟数据
    generateMockData();
    
    // 渲染统计数据
    renderStats();
    
    // 渲染比赛列表
    renderMatches();
    
    // 更新最后更新时间
    updateLastUpdateTime();
    
    // 设置定时更新
    setInterval(refreshStats, 30000); // 30秒更新一次统计
});

// ============================================
// 数据生成函数
// ============================================

function generateMockData() {
    const matches = [];
    
    for (let i = 0; i < MockConfig.generation.totalMatches; i++) {
        const match = {
            id: `match_${Date.now()}_${i}`,
            league: getRandomItem(MockConfig.leagues),
            homeTeam: generateTeamName(true),
            awayTeam: generateTeamName(false),
            matchTime: generateMatchTime(i),
            score: i < 10 ? `${Math.floor(Math.random() * 4)}:${Math.floor(Math.random() * 4)}` : '-:-', // 只有前10场比赛有比分
            odds: {
                homeWin: (1.5 + Math.random() * 2.5).toFixed(2),
                draw: (3.0 + Math.random() * 2.0).toFixed(2),
                awayWin: (2.5 + Math.random() * 3.0).toFixed(2)
            },
            status: i < 10 ? (Math.random() > 0.5 ? '已结束' : '进行中') : '未开始',
            intelligence: generateMatchIntelligence()
        };
        
        matches.push(match);
    }
    
    AppState.allMatches = matches;
    AppState.filteredMatches = [...matches];
}

function generateMatchIntelligence() {
    const count = getRandomInt(
        MockConfig.generation.intelPerMatch.min, 
        MockConfig.generation.intelPerMatch.max
    );
    
    const intelligence = [];
    
    for (let i = 0; i < count; i++) {
        const isHighWeight = Math.random() < MockConfig.generation.highWeightRatio;
        const isMediumWeight = !isHighWeight && Math.random() < MockConfig.generation.mediumWeightRatio;
        const weight = isHighWeight ? 
            parseFloat((8.0 + Math.random() * 2.0).toFixed(1)) : 
            isMediumWeight ?
            parseFloat((6.0 + Math.random() * 1.9).toFixed(1)) :
            parseFloat((1.0 + Math.random() * 4.9).toFixed(1));
        
        const type = getRandomItem(MockConfig.intelligenceTypes).id;
        const source = getRandomItem(MockConfig.sources).id;
        
        const intel = {
            id: `intel_${Date.now()}_${i}`,
            type: type,
            source: source,
            title: generateIntelTitle(type),
            content: generateIntelContent(type),
            weight: weight,
            time: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString(),
            isNew: Math.random() < MockConfig.generation.newIntelRatio,
            impact: calculateImpact(type, weight)
        };
        
        intelligence.push(intel);
    }
    
    return intelligence;
}

function generateIntelTitle(type) {
    const titles = {
        sp: ['重要赔率变动', '欧指大幅调整', '亚盘深度分析', '进球数预测变化'],
        injury: ['主力球员伤缺', '关键位置减员', '复出时间未定', '训练受伤消息'],
        weather: ['恶劣天气预警', '场地条件不佳', '气温影响发挥', '风向数据统计'],
        referee: ['裁判执法风格', '争议判罚记录', '黄牌倾向明显', 'VAR使用习惯'],
        motive: ['争冠形势影响', '保级压力巨大', '国家德比战意', '轮换策略调整'],
        schedule: ['一周双赛疲劳', '长途飞行影响', '赛程密集预警', '休息时间优势'],
        tactics: ['阵型调整信号', '战术打法变化', '临场变阵可能', '攻防转换分析'],
        coach: ['主教练变动', '助教团队调整', '执教理念转变', '临场指挥能力'],
        history: ['历史交锋数据', '心理优势明显', '克星球队出现', '主场优势分析'],
        prediction: ['大数据预测', '专家分析观点', 'AI模型推演', '趋势分析报告'],
        atmosphere: ['主场氛围影响', '球迷支持度', '客场压力因素', '更衣室气氛'],
        other: ['其他重要情报', '突发情况通报', '场外因素影响', '特殊背景分析']
    };
    
    return getRandomItem(titles[type] || ['其他类型情报']);
}

function generateIntelContent(type) {
    const contents = {
        sp: [
            '根据最新数据监控，本场比赛的欧指出现明显变动。主胜赔率从初始的2.10下调至1.85，降幅高达11.9%，表明有大量资金流向主队。同时，平局和客胜赔率相应上调，进一步印证了对主队的信心。',
            '亚盘方面，亚洲盘口从平手升至主让平半，水位维持在中低水区间，进一步印证了对主队的信心。建议关注主队方向的机会。',
            '进球数盘口方面，大球2.5球持续受热捧，市场预期本场比赛将产生较多进球，值得关注大球方向。'
        ],
        injury: [
            '据官方消息，主队核心前锋张三在训练中拉伤大腿肌肉，预计缺席本场比赛。张三本赛季已打入12粒进球，是球队得分的重要保障。',
            '客队中场主力李四累计黄牌停赛，无法登场。李四在中场的拦截和组织能力对球队至关重要，他的缺阵可能影响客队整体战术安排。',
            '主队门将王五有轻伤在身，虽然能够坚持比赛，但扑救能力可能受到影响，这为客队提供了更多机会。'
        ],
        weather: [
            '气象预报显示，比赛当日将有大雨，场地湿滑会影响传球精准度和技术发挥。这种条件下，往往有利于防守反击战术的球队。',
            '气温降至5摄氏度以下，低温可能导致球员肌肉紧张，增加受伤风险，同时也会影响皮球的弹跳轨迹。',
            '强风天气会对长传和定位球产生显著影响，主罚任意球和角球的球员需要特别适应风向。'
        ]
    };
    
    return getRandomItem(contents[type] || ['暂无具体内容，仅供参考。']);
}

function calculateImpact(type, weight) {
    // 根据情报类型和权重计算影响程度
    let baseImpact = weight * 0.5;
    
    // 不同类型的情报有不同的影响系数
    const coefficients = {
        sp: 1.2,      // 赔率变动影响最大
        injury: 1.1,  // 伤病影响较大
        weather: 0.8, // 天气影响适中
        referee: 0.9, // 裁判影响中等
        motive: 1.0,  // 战意影响正常
        schedule: 0.7, // 赛程影响稍小
        tactics: 0.9,  // 战术影响中等
        coach: 0.8,   // 教练影响适中
        history: 0.6,  // 历史交锋影响较小
        prediction: 0.7, // 预测分析影响适中
        atmosphere: 0.8, // 氛围影响适中
        other: 0.5    // 其他影响最小
    };
    
    return parseFloat((baseImpact * (coefficients[type] || 0.8)).toFixed(1));
}

function generateTeamName(isHome) {
    const prefixes = ['红', '蓝', '绿', '黄', '紫', '黑', '白', '金', '银'];
    const middles = ['龙', '虎', '狮', '鹰', '狼', '豹', '熊', '鹿', '牛'];
    const suffixes = ['竞技', '联队', 'FC', '俱乐部', '城', '联盟', '勇士', '风暴'];
    
    const prefix = getRandomItem(prefixes);
    const middle = getRandomItem(middles);
    const suffix = getRandomItem(suffixes);
    
    return `${prefix}${middle}${suffix}${isHome ? '主场' : '客场'}`;
}

function generateMatchTime(index) {
    // 生成比赛时间，随机分布在接下来的几天内
    const baseTime = new Date();
    baseTime.setDate(baseTime.getDate() + (index % 3)); // 分布在未来3天内
    baseTime.setHours(19 + (index % 5), 30 + (index % 2) * 15, 0, 0); // 设置具体时间
    
    return baseTime;
}

// ============================================
// 渲染函数
// ============================================

function renderStats() {
    const stats = {
        totalMatches: AppState.allMatches.length,
        upcomingMatches: AppState.allMatches.filter(m => m.status === '未开始').length,
        liveMatches: AppState.allMatches.filter(m => m.status === '进行中').length,
        finishedMatches: AppState.allMatches.filter(m => m.status === '已结束').length,
        totalIntelligence: AppState.allMatches.reduce((sum, match) => sum + match.intelligence.length, 0),
        highWeightIntelligence: AppState.allMatches
            .flatMap(m => m.intelligence)
            .filter(i => i.weight >= 8.0).length
    };
    
    document.getElementById('totalMatches').textContent = stats.totalMatches;
    document.getElementById('upcomingMatches').textContent = stats.upcomingMatches;
    document.getElementById('liveMatches').textContent = stats.liveMatches;
    document.getElementById('finishedMatches').textContent = stats.finishedMatches;
    document.getElementById('totalIntelligence').textContent = stats.totalIntelligence;
    document.getElementById('highWeightIntelligence').textContent = stats.highWeightIntelligence;
}

function renderMatches() {
    // 应用筛选
    applyFilters();
    
    // 根据当前排序方式排序
    const sortedMatches = [...AppState.filteredMatches];
    
    if (AppState.currentSort === 'weight') {
        // 按最高权重情报排序
        sortedMatches.sort((a, b) => {
            const maxWeightA = Math.max(...a.intelligence.map(i => i.weight));
            const maxWeightB = Math.max(...b.intelligence.map(i => i.weight));
            return maxWeightB - maxWeightA;
        });
    } else {
        // 按时间排序
        sortedMatches.sort((a, b) => new Date(a.matchTime) - new Date(b.matchTime));
    }
    
    // 渲染比赛列表
    const container = document.getElementById('matchListContainer');
    container.innerHTML = '';
    
    sortedMatches.forEach(match => {
        // 根据当前显示类型过滤情报
        let filteredIntel = [...match.intelligence];
        
        if (AppState.currentType !== 'all') {
            filteredIntel = filteredIntel.filter(i => i.type === AppState.currentType);
        }
        
        // 如果筛选后没有情报且当前不是显示全部，则跳过这场比赛
        if (AppState.currentType !== 'all' && filteredIntel.length === 0) {
            return;
        }
        
        const matchCard = document.createElement('div');
        matchCard.className = 'match-card';
        matchCard.innerHTML = `
            <div class="match-header">
                <span class="match-league">${match.league}</span>
                <span class="match-time">${formatTime(match.matchTime)}</span>
                <span class="match-status ${match.status === '进行中' ? 'live' : match.status === '已结束' ? 'finished' : 'upcoming'}">${match.status}</span>
            </div>
            
            <div class="match-teams">
                <div class="team home-team">
                    <span class="team-name">${match.homeTeam}</span>
                    <span class="team-score">${match.score.split(':')[0]}</span>
                </div>
                
                <div class="match-vs">VS</div>
                
                <div class="team away-team">
                    <span class="team-name">${match.awayTeam}</span>
                    <span class="team-score">${match.score.split(':')[1]}</span>
                </div>
            </div>
            
            <div class="match-odds">
                <span class="odd">胜 ${match.odds.homeWin}</span>
                <span class="odd">平 ${match.odds.draw}</span>
                <span class="odd">负 ${match.odds.awayWin}</span>
            </div>
            
            <div class="match-intelligence">
                <h4>相关情报 <span class="count">(${filteredIntel.length})</span></h4>
                
                <div class="intelligence-list">
                    ${filteredIntel.map(intel => `
                        <div class="intelligence-item ${intel.isNew ? 'new-intel' : ''}" onclick="toggleMatchCard(this)">
                            <div class="intel-header">
                                <span class="intel-type" style="background-color: ${getIntelColor(intel.type)}">
                                    <i class="${getIntelIcon(intel.type)}"></i>
                                    ${getTypeLabel(intel.type)}
                                </span>
                                
                                <span class="intel-source" style="color: ${getSourceColor(intel.source)}">
                                    ${getSourceLabel(intel.source)}
                                </span>
                                
                                <span class="intel-weight ${getWeightClass(intel.weight)}">
                                    权重 ${intel.weight}
                                </span>
                                
                                <span class="intel-time">${formatTimeAgo(intel.time)}</span>
                            </div>
                            
                            <div class="intel-content">
                                <h5>${intel.title}</h5>
                                <p>${intel.content}</p>
                                
                                <div class="intel-footer">
                                    <span class="impact">影响力: ${intel.impact}</span>
                                    ${intel.isNew ? '<span class="new-tag">NEW</span>' : ''}
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        container.appendChild(matchCard);
    });
    
    // 如果没有匹配的比赛，显示空状态
    if (sortedMatches.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-search"></i>
                <h3>没有找到匹配的比赛</h3>
                <p>尝试调整筛选条件</p>
                <button class="btn-secondary" onclick="clearFilter()">清除筛选</button>
            </div>
        `;
    }
}

// ============================================
// 交互函数
// ============================================

function toggleMatchCard(element) {
    const content = element.querySelector('.intel-content');
    content.classList.toggle('expanded');
    
    const header = element.querySelector('.intel-header');
    header.classList.toggle('active', content.classList.contains('expanded'));
}

function refreshStats() {
    // 生成新的统计数据（轻微波动）
    const matches = AppState.allMatches;
    matches.forEach(match => {
        // 随机更新一些赔率
        match.odds.homeWin = (parseFloat(match.odds.homeWin) + (Math.random() - 0.5) * 0.2).toFixed(2);
        match.odds.draw = (parseFloat(match.odds.draw) + (Math.random() - 0.5) * 0.2).toFixed(2);
        match.odds.awayWin = (parseFloat(match.odds.awayWin) + (Math.random() - 0.5) * 0.2).toFixed(2);
    });
    
    renderStats();
    
    // 如果当前显示的是列表，也更新列表
    if (document.getElementById('matchList') && !document.getElementById('matchList').classList.contains('hidden')) {
        renderMatches();
    }
}

// 筛选相关函数
function selectFilterOption(element, filterType, value) {
    // 取消同组其他选项的选择状态
    element.parentElement.querySelectorAll('.filter-option').forEach(option => {
        option.classList.remove('selected');
    });
    
    // 选中当前选项
    element.classList.add('selected');
    
    // 更新筛选条件
    AppState.currentFilter[filterType] = value === AppState.currentFilter[filterType] ? null : value;
    
    // 如果取消了筛选，移除UI上的选中状态
    if (!AppState.currentFilter[filterType]) {
        element.classList.remove('selected');
    }
    
    // 应用筛选并重新渲染
    renderMatches();
    
    // 更新筛选摘要
    updateFilterSummary();
    
    showToast(`${MockConfig.intelligenceTypes.find(t => t.id === value)?.name || 
              MockConfig.sources.find(s => s.id === value)?.name || 
              value}筛选已${AppState.currentFilter[filterType] ? '应用' : '取消'}`);
}

function toggleFilterPanel(panelId) {
    const panel = document.getElementById(`${panelId}Panel`);
    const button = document.getElementById(`${panelId}Btn`);
    
    // 切换面板可见性
    panel.classList.toggle('active');
    
    // 切换按钮状态
    button.classList.toggle('active', panel.classList.contains('active'));
}

function clearFilter() {
    // 重置筛选条件
    AppState.currentFilter = {
        type: null,
        source: null,
        weight: null,
        league: null,
        timeRange: null
    };
    
    // 清除UI上的选中状态
    document.querySelectorAll('#filterPanels .filter-option.selected').forEach(el => {
        el.classList.remove('selected');
    });
    
    // 隐藏所有面板
    document.querySelectorAll('#filterPanels .filter-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // 清除筛选摘要
    document.getElementById('filterSummary').innerHTML = '';
    
    // 重新渲染
    renderMatches();
    
    showToast('筛选条件已清除');
}

function removeFilterTag(tagId) {
    // 根据标签ID移除相应的筛选条件
    const parts = tagId.split('-');
    const type = parts[0];
    const value = parts[1];
    
    if (AppState.currentFilter[type] === value) {
        AppState.currentFilter[type] = null;
    }
    
    // 重新渲染
    renderMatches();
    
    // 移除标签UI
    document.getElementById(tagId).remove();
    
    showToast('筛选条件已移除');
}

function applyFilters() {
    AppState.filteredMatches = AppState.allMatches.filter(match => {
        // 类型筛选
        if (AppState.currentFilter.type) {
            const hasTypeIntel = match.intelligence.some(i => i.type === AppState.currentFilter.type);
            if (!hasTypeIntel) return false;
        }
        
        // 来源筛选
        if (AppState.currentFilter.source) {
            const hasSourceIntel = match.intelligence.some(i => i.source === AppState.currentFilter.source);
            if (!hasSourceIntel) return false;
        }
        
        // 权重筛选
        if (AppState.currentFilter.weight) {
            let minWeight = 0;
            if (AppState.currentFilter.weight === 'high') minWeight = 8.0;
            else if (AppState.currentFilter.weight === 'medium') minWeight = 6.0;
            
            const hasWeightIntel = match.intelligence.some(i => i.weight >= minWeight);
            if (!hasWeightIntel) return false;
        }
        
        // 联赛筛选
        if (AppState.currentFilter.league && match.league !== AppState.currentFilter.league) {
            return false;
        }
        
        // 时间范围筛选
        if (AppState.currentFilter.timeRange) {
            const matchTime = new Date(match.matchTime);
            const now = new Date();
            let valid = false;
            
            if (AppState.currentFilter.timeRange === 'today') {
                const today = new Date();
                valid = matchTime.getDate() === today.getDate() &&
                        matchTime.getMonth() === today.getMonth() &&
                        matchTime.getFullYear() === today.getFullYear();
            } else if (AppState.currentFilter.timeRange === 'tomorrow') {
                const tomorrow = new Date();
                tomorrow.setDate(tomorrow.getDate() + 1);
                valid = matchTime.getDate() === tomorrow.getDate() &&
                        matchTime.getMonth() === tomorrow.getMonth() &&
                        matchTime.getFullYear() === tomorrow.getFullYear();
            }
            
            if (!valid) return false;
        }
        
        return true;
    });
    
    // 更新筛选摘要
    updateFilterSummary();
}

function updateFilterSummary() {
    const summaryEl = document.getElementById('filterSummary');
    summaryEl.innerHTML = '';
    
    Object.entries(AppState.currentFilter).forEach(([type, value]) => {
        if (value) {
            const typeLabels = {
                type: '情报类型',
                source: '情报来源',
                weight: '情报权重',
                league: '联赛',
                timeRange: '比赛时间'
            };
            
            const valueLabels = {
                // 类型
                sp: '赔率变动', injury: '伤病情报', weather: '天气影响',
                referee: '裁判信息', motive: '战意分析', schedule: '赛程密集',
                tactics: '战术分析', coach: '教练变动', history: '历史交锋',
                prediction: '预测分析', atmosphere: '氛围影响', other: '其他情报',
                
                // 来源
                official: '官方', media: '媒体', social: '社媒', bookmaker: '机构',
                
                // 权重
                high: '高权重', medium: '中权重', low: '低权重',
                
                // 时间范围
                today: '今天', tomorrow: '明天'
            };
            
            const label = valueLabels[value] || value;
            const tagId = `${type}-${value}`;
            
            const tag = document.createElement('span');
            tag.className = 'filter-tag';
            tag.id = tagId;
            tag.innerHTML = `
                ${typeLabels[type]}: ${label}
                <i class="fas fa-times" onclick="removeFilterTag('${tagId}')"></i>
            `;
            
            summaryEl.appendChild(tag);
        }
    });
}

function quickFilter(filterId, element) {
    // 如果是相同的筛选，取消筛选
    if (AppState.currentType === filterId) {
        AppState.currentType = 'all';
        element.classList.remove('active');
        generateNewMockData();
        return;
    }
    
    // 更新筛选状态
    document.querySelectorAll('#quickFilters .filter-chip').forEach(chip => {
        chip.classList.remove('active');
    });
    element.classList.add('active');
    
    // 设置当前筛选类型
    AppState.currentType = filterId;
    
    // 重新渲染比赛列表
    renderMatches();
}

// 设置排序方式
function setSort(sortType) {
    AppState.currentSort = sortType;
    
    // 更新排序按钮状态
    document.getElementById('sortTime').classList.toggle('active', sortType === 'time');
    document.getElementById('sortWeight').classList.toggle('active', sortType === 'weight');
    
    // 重新渲染比赛列表
    renderMatches();
}

// 刷新数据
function refreshData() {
    const refreshBtn = document.getElementById('refreshBtn');
    refreshBtn.classList.add('spinning');
    
    showLoading();
    
    setTimeout(() => {
        // 生成新的模拟数据
        generateMockData();
        renderStats();
        renderMatches();
        updateLastUpdateTime();
        
        // 显示刷新成功提示
        showToast('数据已刷新！');
        
        hideLoading();
        refreshBtn.classList.remove('spinning');
    }, 1200);
}

// 生成新的模拟数据
function generateNewMockData() {
    showLoading();
    
    const options = {
        totalMatches: parseInt(prompt('请输入比赛数量 (默认: 15):', '15') || '15'),
        intelPerMatch: parseInt(prompt('每场比赛平均情报数 (默认: 5):', '5') || '5'),
        newIntelRatio: parseFloat(prompt('新情报比例 (0-1, 默认: 0.3):', '0.3') || '0.3'),
        highWeightRatio: parseFloat(prompt('高权重比例 (0-1, 默认: 0.2):', '0.2') || '0.2')
    };
    
    // 更新配置
    MockConfig.generation = {
        totalMatches: options.totalMatches || 15,
        intelPerMatch: { 
            min: Math.max(1, Math.floor(options.intelPerMatch * 0.6)),
            max: Math.max(3, Math.floor(options.intelPerMatch * 1.4))
        },
        newIntelRatio: Math.min(1, Math.max(0, options.newIntelRatio || 0.3)),
        highWeightRatio: Math.min(1, Math.max(0, options.highWeightRatio || 0.2)),
        mediumWeightRatio: 0.5
    };
    
    setTimeout(() => {
        // 生成新数据
        generateMockData();
        renderStats();
        renderMatches();
        hideLoading();
        
        showToast(`已生成${MockConfig.generation.totalMatches}场比赛数据`);
    }, 1000);
}

// 处理导航
function handleNavigation(navId) {
    switch (navId) {
        case 'navHome':
            // 显示比赛列表
            document.getElementById('statsPanel').classList.remove('hidden');
            document.getElementById('matchList').classList.remove('hidden');
            document.getElementById('profilePanel').classList.add('hidden');
            document.getElementById('emptyState').classList.add('hidden');
            document.getElementById('filterPanels').classList.remove('hidden');
            document.getElementById('filterSummary').classList.remove('hidden');
            break;
            
        case 'navFilter':
            // 显示筛选面板
            document.getElementById('statsPanel').classList.add('hidden');
            document.getElementById('matchList').classList.add('hidden');
            document.getElementById('profilePanel').classList.add('hidden');
            document.getElementById('emptyState').classList.add('hidden');
            document.getElementById('filterPanels').classList.remove('hidden');
            document.getElementById('filterSummary').classList.remove('hidden');
            // 默认展开第一个面板
            toggleFilterPanel('intelType');
            break;
            
        case 'navProfile':
            // 显示用户面板
            document.getElementById('statsPanel').classList.add('hidden');
            document.getElementById('matchList').classList.add('hidden');
            document.getElementById('profilePanel').classList.remove('hidden');
            document.getElementById('emptyState').classList.add('hidden');
            document.getElementById('filterPanels').classList.add('hidden');
            document.getElementById('filterSummary').classList.add('hidden');
            updateProfileData();
            break;
            
        case 'navFavorites':
            showToast('收藏功能开发中');
            break;
    }
}

// ============================================
// 用户相关函数
// ============================================

// 更新用户资料数据
function updateProfileData() {
    document.getElementById('userName').textContent = UserData.username;
    document.getElementById('userId').textContent = UserData.userId;
    document.getElementById('userLevel').textContent = UserData.level;
    document.getElementById('registerDate').textContent = UserData.registerDate;
    document.getElementById('usageDuration').textContent = UserData.usageDuration || '128天';
    document.getElementById('totalViews').textContent = UserData.totalViews.toLocaleString();
    document.getElementById('correctPredictions').textContent = UserData.correctPredictions + '%';
    document.getElementById('streakDays').textContent = UserData.streakDays;
    document.getElementById('followCount').textContent = UserData.followCount;
    document.getElementById('favoriteCount').textContent = UserData.favoriteCount;
    document.getElementById('accountStatus').textContent = UserData.isLoggedIn ? '正常' : '未登录';
    
    // 更新头像
    const avatarUrl = `https://api.dicebear.com/7.x/avataaars/svg?seed=${UserData.avatarSeed}`;
    document.getElementById('userAvatar').src = avatarUrl;
    
    // 更新设置开关
    document.getElementById('notificationsToggle').checked = UserData.settings.notifications;
    document.getElementById('darkModeToggle').checked = UserData.settings.darkMode;
}

// 切换登录/注册标签
function switchLoginTab(tab) {
    document.getElementById('loginTab').classList.toggle('active', tab === 'login');
    document.getElementById('registerTab').classList.toggle('active', tab === 'register');
    document.getElementById('loginForm').classList.toggle('active', tab === 'login');
    document.getElementById('registerForm').classList.toggle('active', tab === 'register');
}

// 显示登录模态框
function showLoginModal() {
    document.getElementById('loginModal').classList.remove('hidden');
    switchLoginTab('login');
}

// 关闭登录模态框
function closeLoginModal() {
    document.getElementById('loginModal').classList.add('hidden');
    // 清空表单
    document.getElementById('loginUsername').value = '';
    document.getElementById('loginPassword').value = '';
    document.getElementById('registerUsername').value = '';
    document.getElementById('registerPassword').value = '';
    document.getElementById('confirmPassword').value = '';
    document.getElementById('email').value = '';
}

// 登录函数
function login() {
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    if (!username || !password) {
        showToast('请输入用户名和密码');
        return;
    }
    
    // 模拟登录
    if (username === 'demo' && password === 'demo123') {
        UserData.isLoggedIn = true;
        UserData.username = username;
        UserData.avatarSeed = username;
        UserData.userId = `USER${Math.floor(Math.random() * 10000)}`;
        UserData.level = 'VIP 1级会员';
        
        updateProfileData();
        closeLoginModal();
        showToast('登录成功！');
    } else {
        // 演示模式，随便输入都能"登录"
        UserData.isLoggedIn = true;
        UserData.username = username;
        UserData.avatarSeed = username;
        UserData.userId = `USER${Math.floor(Math.random() * 10000)}`;
        UserData.level = '普通会员';
        
        updateProfileData();
        closeLoginModal();
        showToast('登录成功！(演示模式)');
    }
}

// 注册函数
function register() {
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const email = document.getElementById('email').value;
    
    if (!username || !password || !confirmPassword || !email) {
        showToast('请填写所有必填项');
        return;
    }
    
    if (password !== confirmPassword) {
        showToast('两次输入的密码不一致');
        return;
    }
    
    if (password.length < 6) {
        showToast('密码长度至少6位');
        return;
    }
    
    // 模拟注册
    UserData.isLoggedIn = true;
    UserData.username = username;
    UserData.avatarSeed = username;
    UserData.userId = `USER${Math.floor(Math.random() * 10000)}`;
    UserData.level = '新会员';
    UserData.registerDate = new Date().toISOString().split('T')[0];
    
    updateProfileData();
    closeLoginModal();
    showToast('注册成功！欢迎使用');
}

// 更换头像
function changeAvatar() {
    const newSeed = prompt('请输入头像种子 (任意字符串):', UserData.avatarSeed);
    if (newSeed) {
        UserData.avatarSeed = newSeed;
        updateProfileData();
        showToast('头像已更新');
    }
}

// 切换设置
function toggleSetting(setting) {
    if (setting === 'notifications') {
        UserData.settings.notifications = !UserData.settings.notifications;
        document.getElementById('notificationsToggle').checked = UserData.settings.notifications;
        showToast(UserData.settings.notifications ? '通知已开启' : '通知已关闭');
    } else if (setting === 'darkMode') {
        UserData.settings.darkMode = !UserData.settings.darkMode;
        document.getElementById('darkModeToggle').checked = UserData.settings.darkMode;
        showToast(UserData.settings.darkMode ? '深色模式已开启' : '深色模式已关闭');
    }
}

// 清除缓存
function clearCache() {
    if (confirm('确定要清除所有缓存数据吗？')) {
        localStorage.clear();
        // 重置部分用户数据
        UserData.isLoggedIn = false;
        UserData.username = '竞彩玩家';
        UserData.userId = 'JC2026001';
        UserData.level = 'VIP 3级会员';
        UserData.avatarSeed = 'default';
        
        updateProfileData();
        showToast('缓存已清除');
    }
}

// ============================================
// 工具函数
// ============================================

// 格式化时间
function formatTime(date) {
    if (!(date instanceof Date)) {
        date = new Date(date);
    }
    return date.toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

// 格式化相对时间
function formatTimeAgo(timeString) {
    const time = new Date(timeString);
    const now = new Date();
    const diffMs = now - time;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return '刚刚';
    if (diffMins < 60) return `${diffMins}分钟前`;
    if (diffHours < 24) return `${diffHours}小时前`;
    if (diffDays < 7) return `${diffDays}天前`;
    return time.toLocaleDateString('zh-CN');
}

// 获取类型标签
function getTypeLabel(type) {
    const typeObj = MockConfig.intelligenceTypes.find(t => t.id === type);
    return typeObj ? typeObj.name : type;
}

// 获取来源标签
function getSourceLabel(source) {
    const sourceObj = MockConfig.sources.find(s => s.id === source);
    return sourceObj ? sourceObj.name : source;
}

// 获取类型图标
function getIntelIcon(type) {
    const typeObj = MockConfig.intelligenceTypes.find(t => t.id === type);
    return typeObj ? typeObj.icon : 'fas fa-info-circle';
}

// 获取类型颜色
function getIntelColor(type) {
    const typeObj = MockConfig.intelligenceTypes.find(t => t.id === type);
    return typeObj ? typeObj.color : 'var(--tag-other)';
}

// 获取来源颜色
function getSourceColor(source) {
    const sourceObj = MockConfig.sources.find(s => s.id === source);
    return sourceObj ? sourceObj.color : 'var(--source-other)';
}

// 获取权重类别
function getWeightClass(weight) {
    if (weight >= 8.0) return 'weight-high';
    if (weight >= 6.0) return 'weight-medium';
    return 'weight-low';
}

// 更新最后更新时间
function updateLastUpdateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit'
    });
    const dateString = now.toLocaleDateString('zh-CN');
    document.getElementById('lastUpdate').textContent = `最后更新: ${dateString} ${timeString}`;
}

// 显示加载状态
function showLoading() {
    document.getElementById('loadingSpinner').classList.add('active');
}

// 隐藏加载状态
function hideLoading() {
    document.getElementById('loadingSpinner').classList.remove('active');
}

// 显示Toast提示
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast-message';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 80px;
        left: 50%;
        transform: translateX(-50%);
        background: var(--primary);
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        z-index: 9999;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        animation: toastSlideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'toastSlideOut 0.3s ease-out';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

// 添加Toast动画
const style = document.createElement('style');
style.textContent = `
    @keyframes toastSlideIn {
        from { transform: translateX(-50%) translateY(-20px); opacity: 0; }
        to { transform: translateX(-50%) translateY(0); opacity: 1; }
    }
    @keyframes toastSlideOut {
        from { transform: translateX(-50%) translateY(0); opacity: 1; }
        to { transform: translateX(-50%) translateY(-20px); opacity: 0; }
    }
`;
document.head.appendChild(style);

// 工具函数
function getRandomItem(array) {
    return array[Math.floor(Math.random() * array.length)];
}

function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

// 暴露全局函数供HTML调用
window.toggleMatchCard = toggleMatchCard;
window.refreshData = refreshData;
window.refreshStats = refreshStats;
window.showLoginModal = showLoginModal;
window.closeLoginModal = closeLoginModal;
window.login = login;
window.register = register;
window.changeAvatar = changeAvatar;
window.toggleSetting = toggleSetting;
window.clearCache = clearCache;
window.toggleFilterPanel = toggleFilterPanel;
window.clearFilter = clearFilter;
window.applyFilters = applyFilters;
window.removeFilterTag = removeFilterTag;
window.quickFilter = quickFilter;
window.setSort = setSort;
window.handleNavigation = handleNavigation;
window.generateNewMockData = generateNewMockData;
window.selectFilterOption = selectFilterOption;