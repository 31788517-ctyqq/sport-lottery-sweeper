import { defineStore } from 'pinia';

export const useAppStore = defineStore('app', {
  state: () => ({
    // 模拟数据配置
    mockConfig: {
      leagues: [
        { id: 'premier', name: '英超', color: 'league-premier', icon: 'fas fa-futbol' },
        { id: 'laliga', name: '西甲', color: 'league-laliga', icon: 'fas fa-futbol' },
        { id: 'seriea', name: '意甲', color: 'league-seriea', icon: 'fas fa-futbol' },
        { id: 'bundesliga', name: '德甲', color: 'league-bundesliga', icon: 'fas fa-futbol' },
        { id: 'ligue1', name: '法甲', color: 'league-ligue1', icon: 'fas fa-futbol' },
        { id: 'champions', name: '欧冠', color: 'league-champions', icon: 'fas fa-trophy' }
      ],
      teams: {
        premier: [
          { id: 'MCI', name: '曼城', shortName: 'MCI' },
          { id: 'LIV', name: '利物浦', shortName: 'LIV' },
          { id: 'CHE', name: '切尔西', shortName: 'CHE' },
          { id: 'MUN', name: '曼联', shortName: 'MUN' },
          { id: 'TOT', name: '热刺', shortName: 'TOT' },
          { id: 'ARS', name: '阿森纳', shortName: 'ARS' }
        ],
        laliga: [
          { id: 'RMA', name: '皇家马德里', shortName: 'RMA' },
          { id: 'BAR', name: '巴塞罗那', shortName: 'BAR' },
          { id: 'ATM', name: '马德里竞技', shortName: 'ATM' },
          { id: 'SEV', name: '塞维利亚', shortName: 'SEV' },
          { id: 'VIL', name: '比利亚雷亚尔', shortName: 'VIL' },
          { id: 'BET', name: '皇家贝蒂斯', shortName: 'BET' }
        ],
        seriea: [
          { id: 'JUV', name: '尤文图斯', shortName: 'JUV' },
          { id: 'MIL', name: 'AC米兰', shortName: 'MIL' },
          { id: 'INT', name: '国际米兰', shortName: 'INT' },
          { id: 'NAP', name: '那不勒斯', shortName: 'NAP' },
          { id: 'ROM', name: '罗马', shortName: 'ROM' },
          { id: 'LAZ', name: '拉齐奥', shortName: 'LAZ' }
        ],
        bundesliga: [
          { id: 'BAY', name: '拜仁慕尼黑', shortName: 'BAY' },
          { id: 'DOR', name: '多特蒙德', shortName: 'DOR' },
          { id: 'LEI', name: '莱比锡', shortName: 'LEI' },
          { id: 'LEV', name: '勒沃库森', shortName: 'LEV' },
          { id: 'MGL', name: '门兴', shortName: 'MGL' },
          { id: 'WOL', name: '沃尔夫斯堡', shortName: 'WOL' }
        ],
        ligue1: [
          { id: 'PSG', name: '巴黎圣日耳曼', shortName: 'PSG' },
          { id: 'LYO', name: '里昂', shortName: 'LYO' },
          { id: 'MAR', name: '马赛', shortName: 'MAR' },
          { id: 'MON', name: '摩纳哥', shortName: 'MON' },
          { id: 'LIL', name: '里尔', shortName: 'LIL' },
          { id: 'NIC', name: '尼斯', shortName: 'NIC' }
        ],
        champions: [
          { id: 'MCI', name: '曼城', shortName: 'MCI' },
          { id: 'RMA', name: '皇家马德里', shortName: 'RMA' },
          { id: 'BAY', name: '拜仁慕尼黑', shortName: 'BAY' },
          { id: 'PSG', name: '巴黎圣日耳曼', shortName: 'PSG' },
          { id: 'LIV', name: '利物浦', shortName: 'LIV' },
          { id: 'BAR', name: '巴塞罗那', shortName: 'BAR' }
        ]
      },
      venues: [
        '伊蒂哈德球场', '安菲尔德球场', '斯坦福桥球场', '老特拉福德球场',
        '诺坎普球场', '伯纳乌球场', '安联球场', '王子公园球场',
        '圣西罗球场', '阿尔瓦拉德球场', '威斯特法伦球场', '梅阿查球场'
      ],
      intelligenceTypes: [
        { id: 'injury', name: '伤病', icon: 'fas fa-user-injured', color: 'tag-injury' },
        { id: 'weather', name: '天气', icon: 'fas fa-cloud-sun', color: 'tag-weather' },
        { id: 'referee', name: '裁判', icon: 'fas fa-whistle', color: 'tag-referee' },
        { id: 'sp', name: '赔率', icon: 'fas fa-chart-line', color: 'tag-sp' },
        { id: 'motive', name: '战意', icon: 'fas fa-fire', color: 'tag-motive' },
        { id: 'tactics', name: '战术', icon: 'fas fa-chess-board', color: 'tag-tactics' },
        { id: 'coach', name: '主帅', icon: 'fas fa-user-tie', color: 'tag-coach' },
        { id: 'history', name: '历史', icon: 'fas fa-history', color: 'tag-history' },
        { id: 'atmosphere', name: '氛围', icon: 'fas fa-users', color: 'tag-atmosphere' },
        { id: 'prediction', name: '预测', icon: 'fas fa-crystal-ball', color: 'tag-prediction' }
      ],
      sources: [
        { id: 'official', name: '官方', icon: 'fas fa-check-circle', color: 'source-official' },
        { id: 'media', name: '媒体', icon: 'fas fa-newspaper', color: 'source-media' },
        { id: 'social', name: '社交', icon: 'fas fa-share-alt', color: 'source-social' },
        { id: 'bookmaker', name: '博彩', icon: 'fas fa-chart-line', color: 'source-bookmaker' }
      ],
      generation: {
        totalMatches: 15,
        intelPerMatch: { min: 3, max: 8 },
        newIntelRatio: 0.3,
        highWeightRatio: 0.2,
        mediumWeightRatio: 0.5
      }
    },

    // 应用状态
    currentType: 'all',
    currentSort: 'time',
    matches: [],
    intelligence: {},
    favorites: JSON.parse(localStorage.getItem('favorites')) || [],
    viewMode: 'list',
    autoRefresh: true,
    currentView: 'home', // 'home', 'filter', 'profile', 'favorites'
    filterState: {
      intelTypes: [],
      leagues: [],
      sources: []
    },
    panelState: {
      intelTypeExpanded: true,
      leagueExpanded: false,
      sourceExpanded: false
    },
    
    // 用户数据
    userData: {
      isLoggedIn: false,
      username: '竞彩玩家',
      userId: 'JC2026001',
      level: 'VIP 3级会员',
      avatarSeed: 'default',
      registerDate: '2026-01-01',
      totalViews: 1248,
      correctPredictions: 68,
      streakDays: 7,
      followCount: 12,
      favoriteCount: 24,
      settings: {
        notifications: true,
        darkMode: true
      }
    },
    
    // 统计数据
    stats: {
      totalMatches: 0,
      totalIntel: 0,
      newIntel: 0,
      highWeightIntel: 0,
      matchesByLeague: {},
      avgIntelPerMatch: 0,
      newIntelRatio: 0,
      highWeightRatio: 0
    },
    
    // UI状态
    loading: false,
    lastUpdateTime: '--',
    showLoginModal: false
  }),
  
  getters: {
    // 获取筛选后的比赛
    filteredMatches: (state) => {
      return state.matches.filter(match => {
        // 联赛筛选（支持多选）
        if (state.filterState.leagues.length > 0) {
          if (!state.filterState.leagues.includes(match.leagueId)) {
            return false;
          }
        }

        // 获取比赛的所有情报
        const matchIntelligence = state.intelligence[match.id] || [];

        // 情报类型筛选（支持多选）
        if (state.filterState.intelTypes.length > 0) {
          const hasMatchingIntel = matchIntelligence.some(intel =>
            state.filterState.intelTypes.includes(intel.type)
          );
          if (!hasMatchingIntel) return false;
        }

        // 信息来源筛选（支持多选）
        if (state.filterState.sources.length > 0) {
          const hasMatchingSource = matchIntelligence.some(intel =>
            state.filterState.sources.includes(intel.source)
          );
          if (!hasMatchingSource) return false;
        }

        return true;
      });
    },

    // 获取比赛统计数据
    matchStats: (state) => {
      return {
        totalMatches: state.stats.totalMatches,
        totalIntel: state.stats.totalIntel,
        newIntel: state.stats.newIntel,
        avgIntelPerMatch: state.stats.avgIntelPerMatch
      };
    },

    // 检查是否有活动的筛选器
    hasActiveFilters: (state) => {
      return (
        state.filterState.intelTypes.length > 0 ||
        state.filterState.leagues.length > 0 ||
        state.filterState.sources.length > 0
      );
    }
  },
  
  actions: {
    // 生成模拟数据
    generateMockData() {
      this.loading = true;
      
      // 重置统计数据
      this.stats = {
        totalMatches: 0,
        totalIntel: 0,
        newIntel: 0,
        highWeightIntel: 0,
        matchesByLeague: {},
        avgIntelPerMatch: 0,
        newIntelRatio: 0,
        highWeightRatio: 0
      };
      
      this.matches = [];
      this.intelligence = {};
      
      const today = new Date();
      
      // 生成比赛数据
      for (let i = 0; i < this.mockConfig.generation.totalMatches; i++) {
        const league = this.randomChoice(this.mockConfig.leagues);
        const leagueTeams = this.mockConfig.teams[league.id];
        
        // 随机选择两队，确保不重复
        let homeTeam, awayTeam;
        do {
          homeTeam = this.randomChoice(leagueTeams);
          awayTeam = this.randomChoice(leagueTeams);
        } while (homeTeam.id === awayTeam.id);
        
        // 随机时间（未来1-7天）
        const matchDate = new Date(today);
        matchDate.setDate(matchDate.getDate() + this.random(1, 7));
        matchDate.setHours(this.random(14, 22), this.random(0, 59), 0, 0);
        
        // 生成比赛数据
        const match = {
          id: `MAT${String(i + 1).padStart(3, '0')}`,
          league: league.name,
          leagueId: league.id,
          leagueColor: league.color,
          homeTeam: homeTeam.name,
          homeTeamShort: homeTeam.shortName,
          awayTeam: awayTeam.name,
          awayTeamShort: awayTeam.shortName,
          time: matchDate.toISOString(),
          venue: this.randomChoice(this.mockConfig.venues),
          status: '未开始',
          // 模拟近期战绩
          homeForm: this.generateFormRecord(),
          awayForm: this.generateFormRecord(),
          // 模拟SP数据
          spData: this.generateSPData(),
          // 模拟预测
          predictions: this.generatePredictions()
        };
        
        this.matches.push(match);
        
        // 为该比赛生成情报
        this.generateIntelligenceForMatch(match.id);
      }
      
      // 按时间排序
      this.matches.sort((a, b) => new Date(a.time) - new Date(b.time));
      
      // 更新统计数据
      this.updateStats();
      
      this.loading = false;
    },
    
    // 生成情报数据
    generateIntelligenceForMatch(matchId) {
      const intelCount = this.random(
        this.mockConfig.generation.intelPerMatch.min,
        this.mockConfig.generation.intelPerMatch.max
      );
      
      const intelList = [];
      const match = this.matches.find(m => m.id === matchId);
      
      for (let i = 0; i < intelCount; i++) {
        const intelType = this.randomChoice(this.mockConfig.intelligenceTypes);
        const source = this.randomChoice(this.mockConfig.sources);
        
        // 生成权重
        let weight;
        const rand = Math.random();
        if (rand < this.mockConfig.generation.highWeightRatio) {
          weight = this.random(80, 95) / 10;
        } else if (rand < this.mockConfig.generation.highWeightRatio + this.mockConfig.generation.mediumWeightRatio) {
          weight = this.random(60, 79) / 10;
        } else {
          weight = this.random(30, 59) / 10;
        }
        
        // 是否标记为new
        const isNew = this.randomBool(this.mockConfig.generation.newIntelRatio);
        
        // 生成时间（最近1-48小时）
        const intelTime = new Date(Date.now() - this.random(1 * 60 * 60 * 1000, 48 * 60 * 60 * 1000));
        
        // 生成情报内容
        const content = this.generateIntelContent(intelType.id, match, source.id);
        
        const intelligence = {
          id: `${matchId}-INT${String(i).padStart(2, '0')}`,
          matchId: matchId,
          type: intelType.id,
          typeName: intelType.name,
          typeIcon: intelType.icon,
          typeColor: intelType.color,
          source: source.id,
          sourceName: source.name,
          sourceColor: source.color,
          content: content.text,
          summary: content.summary,
          weight: weight,
          isNew: isNew,
          timestamp: intelTime.toISOString(),
          extraData: this.generateExtraData(intelType.id, match)
        };
        
        intelList.push(intelligence);
        
        // 更新统计
        this.stats.totalIntel++;
        if (isNew) this.stats.newIntel++;
        if (weight >= 8) this.stats.highWeightIntel++;
      }
      
      // 按时间排序（最新的在前面）
      intelList.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
      
      this.intelligence[matchId] = intelList;
      
      // 更新比赛统计
      this.stats.totalMatches++;
      if (!this.stats.matchesByLeague[match.league]) {
        this.stats.matchesByLeague[match.league] = 0;
      }
      this.stats.matchesByLeague[match.league]++;
    },
    
    // 生成战绩记录
    generateFormRecord() {
      const form = [];
      for (let i = 0; i < 5; i++) {
        const rand = Math.random();
        if (rand < 0.4) form.push('W');
        else if (rand < 0.7) form.push('D');
        else form.push('L');
      }
      return form;
    },
    
    // 生成SP数据
    generateSPData() {
      return {
        '竞彩官方': {
          win: { initial: (Math.random() * 0.5 + 1.5).toFixed(2), latest: (Math.random() * 0.5 + 1.5).toFixed(2) },
          draw: { initial: (Math.random() * 0.5 + 3.0).toFixed(2), latest: (Math.random() * 0.5 + 3.0).toFixed(2) },
          loss: { initial: (Math.random() * 0.5 + 4.0).toFixed(2), latest: (Math.random() * 0.5 + 4.0).toFixed(2) }
        },
        '威廉希尔': {
          win: { initial: (Math.random() * 0.5 + 1.5).toFixed(2), latest: (Math.random() * 0.5 + 1.5).toFixed(2) },
          draw: { initial: (Math.random() * 0.5 + 3.0).toFixed(2), latest: (Math.random() * 0.5 + 3.0).toFixed(2) },
          loss: { initial: (Math.random() * 0.5 + 4.0).toFixed(2), latest: (Math.random() * 0.5 + 4.0).toFixed(2) }
        },
        '立博': {
          win: { initial: (Math.random() * 0.5 + 1.5).toFixed(2), latest: (Math.random() * 0.5 + 1.5).toFixed(2) },
          draw: { initial: (Math.random() * 0.5 + 3.0).toFixed(2), latest: (Math.random() * 0.5 + 3.0).toFixed(2) },
          loss: { initial: (Math.random() * 0.5 + 4.0).toFixed(2), latest: (Math.random() * 0.5 + 4.0).toFixed(2) }
        }
      };
    },
    
    // 生成预测
    generatePredictions() {
      const predictions = [];
      const predictionTypes = [
        { type: '胜负平', icon: 'fas fa-trophy' },
        { type: '比分', icon: 'fas fa-futbol' },
        { type: '大小球', icon: 'fas fa-bullseye' }
      ];
      
      predictionTypes.forEach(predType => {
        predictions.push({
          id: `PRED${this.random(1, 1000)}`,
          type: predType.type,
          icon: predType.icon,
          prediction: this.generatePredictionText(predType.type),
          confidence: this.random(60, 95),
          source: this.randomChoice(['AI模型', '专家分析', '历史数据']),
          timestamp: new Date(Date.now() - this.random(0, 24 * 60 * 60 * 1000)).toISOString()
        });
      });
      
      return predictions;
    },
    
    // 生成预测文本
    generatePredictionText(type) {
      const texts = {
        '胜负平': ['主队不败', '客队有望取分', '双方分胜负', '平局可能性大'],
        '比分': ['2-1', '1-1', '3-2', '2-0', '0-0'],
        '大小球': ['大球(>2.5)', '小球(<2.5)', '走盘(2.5)']
      };
      
      return this.randomChoice(texts[type] || ['数据不足，无法预测']);
    },
    
    // 生成情报内容
    generateIntelContent(type, match, source) {
      const templates = {
        injury: {
          official: [
            { text: `${match.homeTeam}主力前锋确认因大腿肌肉拉伤将缺席本场比赛，预计休战2-3周。`, summary: '主力前锋伤缺' },
            { text: `${match.awayTeam}后防核心在训练中受伤，经检查为脚踝扭伤，本场比赛出战成疑。`, summary: '后防核心出战成疑' }
          ],
          media: [
            { text: `据队医透露，${match.homeTeam}中场核心恢复情况良好，有望在本场比赛中复出。`, summary: '中场核心有望复出' },
            { text: `${match.awayTeam}两名主力球员因累积黄牌停赛，对球队实力影响较大。`, summary: '两主力停赛' }
          ]
        },
        weather: {
          official: [
            { text: '比赛日当地天气预报显示将有中雨，气温15-18度，湿度85%，可能影响比赛节奏。', summary: '比赛日有雨' },
            { text: '晴朗天气，气温适宜，湿度60%，非常适合足球比赛。', summary: '天气良好' }
          ]
        },
        referee: {
          official: [
            { text: '本场比赛主裁判为安东尼·泰勒，其执法尺度较严，本赛季共出示黄牌45张，红牌3张。', summary: '主裁判执法严格' },
            { text: 'VAR裁判为迈克尔·奥利弗，本赛季参与判罚准确率高达98%。', summary: 'VAR裁判准确率高' }
          ]
        },
        sp: {
          bookmaker: [
            { text: '竞彩官方胜赔从1.85下调至1.75，平赔从3.40上调至3.60，负赔从4.20上调至4.50。', summary: '主胜赔率下调' },
            { text: '威廉希尔大幅下调客胜赔率，从4.50降至3.80，显示对客队信心增强。', summary: '客胜赔率下调' }
          ]
        },
        motive: {
          media: [
            { text: `${match.homeTeam}本场比赛若获胜将提前锁定联赛冠军，战意十足。`, summary: '主队争冠战意强' },
            { text: `${match.awayTeam}已确定降级，球员心态可能受到影响。`, summary: '客队已降级' }
          ],
          social: [
            { text: '社交媒体显示，主队球迷热情高涨，门票已售罄，主场氛围极佳。', summary: '主场氛围热烈' }
          ]
        },
        tactics: {
          media: [
            { text: `${match.homeTeam}主帅确认将变阵4-3-3，强调高位逼抢和快速反击。`, summary: '主队变阵4-3-3' },
            { text: `${match.awayTeam}预计采用防守反击战术，重点盯防对方核心球员。`, summary: '客队防守反击' }
          ]
        },
        coach: {
          official: [
            { text: `${match.homeTeam}主帅在赛前发布会表示："我们已经做好充分准备，目标全取三分。"`, summary: '主帅信心十足' },
            { text: `${match.awayTeam}主帅因个人原因可能缺席本场比赛，由助教临时指挥。`, summary: '主帅可能缺席' }
          ]
        },
        history: {
          media: [
            { text: `双方近10次交锋，${match.homeTeam}取得6胜3平1负，占据绝对优势。`, summary: '历史交锋主队占优' },
            { text: '上赛季同一对决中，主队曾5-0大胜客队，心理优势明显。', summary: '上季主队大胜' }
          ]
        },
        atmosphere: {
          social: [
            { text: '球迷论坛热议本场比赛，普遍看好主队获胜，支持率超过70%。', summary: '球迷看好主队' },
            { text: '社交媒体上客队球迷组织表示将组织3000人远征助威。', summary: '客队球迷远征' }
          ]
        },
        prediction: {
          media: [
            { text: '权威媒体预测本场比赛主队不败概率高达75%，推荐比分2-1、1-1。', summary: '媒体预测主队不败' },
            { text: '数据分析模型显示，本场比赛出现大球(>2.5)的概率为68%。', summary: '模型预测大球' }
          ]
        }
      };
      
      const typeTemplates = templates[type];
      if (!typeTemplates) {
        return {
          text: '暂无详细信息',
          summary: '信息更新中'
        };
      }
      
      const sourceTemplates = typeTemplates[source] || typeTemplates[Object.keys(typeTemplates)[0]];
      
      if (sourceTemplates && sourceTemplates.length > 0) {
        return this.randomChoice(sourceTemplates);
      }
      
      return {
        text: `关于${match.homeTeam} vs ${match.awayTeam}的${type}情报`,
        summary: `${type}情报更新`
      };
    },
    
    // 生成额外数据
    generateExtraData(type, match) {
      switch(type) {
        case 'sp':
          return {
            companies: ['竞彩官方', '威廉希尔', '立博'],
            changes: [
              { company: '竞彩官方', direction: this.randomBool() ? 'up' : 'down', amount: (Math.random() * 0.3).toFixed(2) },
              { company: '威廉希尔', direction: this.randomBool() ? 'up' : 'down', amount: (Math.random() * 0.3).toFixed(2) }
            ]
          };
        case 'injury':
          return {
            players: [
              { name: '主力前锋', team: match.homeTeam, status: '缺席', duration: '2-3周' },
              { name: '后防核心', team: match.awayTeam, status: '出战成疑', probability: '50%' }
            ]
          };
        case 'weather':
          return {
            temperature: `${this.random(10, 25)}°C`,
            condition: this.randomChoice(['晴朗', '多云', '小雨', '中雨']),
            humidity: `${this.random(50, 90)}%`,
            wind: `${this.random(5, 25)} km/h`
          };
        default:
          return {};
      }
    },
    
    // 更新统计数据
    updateStats() {
      this.stats.avgIntelPerMatch = this.stats.totalMatches > 0 ? (this.stats.totalIntel / this.stats.totalMatches).toFixed(1) : 0;
      this.stats.newIntelRatio = this.stats.totalIntel > 0 ? ((this.stats.newIntel / this.stats.totalIntel) * 100).toFixed(1) : 0;
      this.stats.highWeightRatio = this.stats.totalIntel > 0 ? ((this.stats.highWeightIntel / this.stats.totalIntel) * 100).toFixed(1) : 0;
      
      this.lastUpdateTime = new Date().toLocaleString('zh-CN');
    },
    
    // 检查是否显示该比赛
    shouldShowMatch(match) {
      // 联赛筛选（支持多选）
      if (this.filterState.leagues.length > 0) {
        if (!this.filterState.leagues.includes(match.leagueId)) {
          return false;
        }
      }
      
      // 获取比赛的所有情报
      const matchIntelligence = this.intelligence[match.id] || [];
      
      // 情报类型筛选（支持多选）
      if (this.filterState.intelTypes.length > 0) {
        const hasMatchingIntel = matchIntelligence.some(intel =>
          this.filterState.intelTypes.includes(intel.type)
        );
        if (!hasMatchingIntel) return false;
      }
      
      // 信息来源筛选（支持多选）
      if (this.filterState.sources.length > 0) {
        const hasMatchingSource = matchIntelligence.some(intel =>
          this.filterState.sources.includes(intel.source)
        );
        if (!hasMatchingSource) return false;
      }
      
      return true;
    },
    
    // 切换筛选选项
    toggleFilterOption(filterType, id) {
      let filterArray;
      switch(filterType) {
        case 'intelType':
          filterArray = this.filterState.intelTypes;
          break;
        case 'league':
          filterArray = this.filterState.leagues;
          break;
        case 'source':
          filterArray = this.filterState.sources;
          break;
        default:
          return;
      }
      
      const index = filterArray.indexOf(id);
      if (index === -1) {
        // 添加
        filterArray.push(id);
      } else {
        // 移除
        filterArray.splice(index, 1);
      }
    },
    
    // 移除筛选标签
    removeFilterTag(filterType, id) {
      const filterArray = this.filterState[filterType + 's'];
      const index = filterArray.indexOf(id);
      if (index !== -1) {
        filterArray.splice(index, 1);
      }
    },
    
    // 清除筛选
    clearFilter(filterType) {
      switch(filterType) {
        case 'intelType':
          this.filterState.intelTypes = [];
          break;
        case 'league':
          this.filterState.leagues = [];
          break;
        case 'source':
          this.filterState.sources = [];
          break;
      }
    },
    
    // 设置排序方式
    setSort(sortType) {
      this.currentSort = sortType;
    },
    
    // 更新用户资料
    updateUserData(userData) {
      this.userData = { ...this.userData, ...userData };
    },
    
    // 切换设置
    toggleSetting(setting) {
      if (setting === 'notifications') {
        this.userData.settings.notifications = !this.userData.settings.notifications;
      } else if (setting === 'darkMode') {
        this.userData.settings.darkMode = !this.userData.settings.darkMode;
      }
    },
    
    // 切换视图
    setCurrentView(view) {
      this.currentView = view;
    },
    
    // 显示/隐藏登录模态框
    setShowLoginModal(show) {
      this.showLoginModal = show;
    },
    
    // 工具函数：随机数
    random(min, max) {
      return Math.floor(Math.random() * (max - min + 1)) + min;
    },
    
    // 工具函数：随机选择数组元素
    randomChoice(array) {
      return array[Math.floor(Math.random() * array.length)];
    },
    
    // 工具函数：随机布尔值
    randomBool(probability = 0.5) {
      return Math.random() < probability;
    }
  }
});