<template>
  <el-dialog title="比赛分析" v-model="dialogVisible" width="70%" class="analysis-dialog">
    <div v-if="analysisData">
      <div class="analysis-sim-container">
        <div class="analysis-sim-header">
          <div class="analysis-sim-title">比赛分析模拟</div>
          <div class="analysis-sim-subtitle">基于100球数据的比赛分析展示</div>
        </div>

        <div class="analysis-sim-card">
          <div class="analysis-sim-card-title">比赛基本信息</div>
          <div class="analysis-sim-basic">
            <div class="analysis-sim-team">
              <div class="analysis-sim-team-name">{{ analysisData.homeTeam || '-' }}</div>
              <div class="analysis-sim-team-meta">实力值: {{ analysisData.homePower ?? '-' }}</div>
            </div>
            <div class="analysis-sim-vs">
              <div class="analysis-sim-league">{{ analysisData.gameShortName || '-' }}</div>
              <div class="analysis-sim-vs-text">VS</div>
              <div class="analysis-sim-time">{{ analysisData.matchTimeStr || '-' }}</div>
            </div>
            <div class="analysis-sim-team">
              <div class="analysis-sim-team-name">{{ analysisData.guestTeam || '-' }}</div>
              <div class="analysis-sim-team-meta">实力值: {{ analysisData.guestPower ?? '-' }}</div>
            </div>
          </div>
          <div class="analysis-sim-odds">
            <div class="analysis-sim-odds-item"><span>主胜</span><strong>{{ analysisData.homeWinAward ?? '-' }}</strong></div>
            <div class="analysis-sim-odds-item"><span>平局</span><strong>{{ analysisData.drawAward ?? '-' }}</strong></div>
            <div class="analysis-sim-odds-item"><span>客胜</span><strong>{{ analysisData.guestWinAward ?? '-' }}</strong></div>
            <div class="analysis-sim-odds-item"><span>让球</span><strong>{{ analysisData.rq ?? '-' }}</strong></div>
          </div>
        </div>

        <div class="analysis-sim-card">
          <div class="analysis-sim-card-title">球队实力对比</div>
          <div class="analysis-sim-progress">
            <div class="analysis-sim-progress-labels">
              <span>{{ analysisData.homeTeam || '-' }}</span>
              <span>{{ analysisData.guestTeam || '-' }}</span>
            </div>
            <div class="analysis-sim-progress-bars">
              <el-progress :percentage="getProgressValue(analysisData.homePower)" :show-text="false" :color="'#a4b2a4'" />
              <el-progress :percentage="getProgressValue(analysisData.guestPower)" :show-text="false" :color="'#b9a7a0'" />
            </div>
          </div>
          <div class="analysis-sim-table">
            <div class="analysis-sim-table-row analysis-sim-table-head">
              <span>指标</span><span>主队</span><span>客队</span><span>优势方</span>
            </div>
            <div class="analysis-sim-table-row">
              <span>积分（主场/总）</span>
              <span>{{ analysisData.homeJiFenHome || '-' }}/{{ analysisData.homeJiFenHomeAll || '-' }}</span>
              <span>{{ analysisData.awayJiFenHome || '-' }}/{{ analysisData.awayJiFenHomeAll || '-' }}</span>
              <span>{{ compareAdvantage(analysisData.homeJiFenHome, analysisData.awayJiFenHome) }}</span>
            </div>
            <div class="analysis-sim-table-row">
              <span>客场积分</span>
              <span>-</span>
              <span>{{ analysisData.awayJiFenGuest || '-' }}</span>
              <span>客队</span>
            </div>
            <div class="analysis-sim-table-row">
              <span>特征</span>
              <span>{{ analysisData.homeFeature || '-' }}</span>
              <span>{{ analysisData.guestFeature || '-' }}</span>
              <span>{{ compareAdvantage(getPercentValue(analysisData.homeFeature), getPercentValue(analysisData.guestFeature)) }}</span>
            </div>
            <div class="analysis-sim-table-row">
              <span>进攻效率</span>
              <span>{{ analysisData.homeEnterEfficiency || '-' }}</span>
              <span>{{ analysisData.guestEnterEfficiency || '-' }}</span>
              <span>{{ compareAdvantage(getEfficiencyValue(analysisData.homeEnterEfficiency), getEfficiencyValue(analysisData.guestEnterEfficiency)) }}</span>
            </div>
            <div class="analysis-sim-table-row">
              <span>防守效率</span>
              <span>{{ analysisData.homePreventEfficiency || '-' }}</span>
              <span>{{ analysisData.guestPreventEfficiency || '-' }}</span>
              <span>{{ compareAdvantage(getEfficiencyValue(analysisData.homePreventEfficiency), getEfficiencyValue(analysisData.guestPreventEfficiency)) }}</span>
            </div>
            <div class="analysis-sim-table-row">
              <span>近期战绩</span>
              <span>{{ analysisData.homeSpf || '-' }}</span>
              <span>{{ analysisData.guestSpf || '-' }}</span>
              <span>{{ compareAdvantage(getSpfWins(analysisData.homeSpf), getSpfWins(analysisData.guestSpf)) }}</span>
            </div>
            <div class="analysis-sim-table-row">
              <span>大球百分比</span>
              <span>{{ analysisData.homeDxqPercentStr || '-' }}</span>
              <span>{{ analysisData.guestDxqPercentStr || '-' }}</span>
              <span>{{ compareAdvantage(getPercentValue(analysisData.homeDxqPercentStr), getPercentValue(analysisData.guestDxqPercentStr)) }}</span>
            </div>
            <div class="analysis-sim-table-row">
              <span>近期进球/失球</span>
              <span>{{ analysisData.homeDxqDesc || '-' }}</span>
              <span>{{ analysisData.guestDxqDesc || '-' }}</span>
              <span>需分析</span>
            </div>
            <div class="analysis-sim-table-row">
              <span>主场/客场表现</span>
              <span>{{ analysisData.homeDxqSame10Desc || '-' }}</span>
              <span>{{ analysisData.awayDxqSame10Desc || '-' }}</span>
              <span>需分析</span>
            </div>
          </div>
        </div>

        <div class="analysis-sim-card">
          <div class="analysis-sim-card-title">赔率对比分析</div>
          <div class="analysis-sim-odds-panels">
            <div class="analysis-sim-odds-panel">
              <div class="analysis-sim-panel-title">主胜盘</div>
              <div class="analysis-sim-panel-value">{{ analysisData.homeWinPan ?? '-' }}</div>
              <div class="analysis-sim-panel-grid">
                <div>进0球 {{ analysisData.homeWinQiu_0 ?? '-' }}</div>
                <div>进1球 {{ analysisData.homeWinQiu_1 ?? '-' }}</div>
                <div>进2球 {{ analysisData.homeWinQiu_2 ?? '-' }}</div>
              </div>
              <div class="analysis-sim-panel-grid">
                <div>赢1球差距 {{ analysisData.homeWinGap_1 ?? '-' }}</div>
                <div>赢2球差距 {{ analysisData.homeWinGap_2 ?? '-' }}</div>
                <div>-</div>
              </div>
            </div>
            <div class="analysis-sim-odds-panel">
              <div class="analysis-sim-panel-title">客胜盘</div>
              <div class="analysis-sim-panel-value">{{ analysisData.guestWinPan ?? '-' }}</div>
              <div class="analysis-sim-panel-grid">
                <div>进0球 {{ analysisData.awayWinQiu_0 ?? '-' }}</div>
                <div>进1球 {{ analysisData.awayWinQiu_1 ?? '-' }}</div>
                <div>进2球 {{ analysisData.awayWinQiu_2 ?? '-' }}</div>
              </div>
              <div class="analysis-sim-panel-grid">
                <div>赢1球差距 {{ analysisData.awayWinGap_1 ?? '-' }}</div>
                <div>赢2球差距 {{ analysisData.awayWinGap_2 ?? '-' }}</div>
                <div>-</div>
              </div>
            </div>
          </div>
          <div class="analysis-sim-lose">
            <div class="analysis-sim-lose-panel">
              <div class="analysis-sim-panel-title">主队失球</div>
              <div class="analysis-sim-panel-grid">
                <div>失0球 {{ analysisData.homeLoseQiu_0 ?? '-' }}</div>
                <div>失1球 {{ analysisData.homeLoseQiu_1 ?? '-' }}</div>
                <div>失2球 {{ analysisData.homeLoseQiu_2 ?? '-' }}</div>
              </div>
              <div class="analysis-sim-panel-grid">
                <div>输1球差距 {{ analysisData.homeLoseGap_1 ?? '-' }}</div>
                <div>输2球差距 {{ analysisData.homeLoseGap_2 ?? '-' }}</div>
                <div>-</div>
              </div>
            </div>
            <div class="analysis-sim-lose-panel">
              <div class="analysis-sim-panel-title">客队失球</div>
              <div class="analysis-sim-panel-grid">
                <div>失0球 {{ analysisData.awayLoseQiu_0 ?? '-' }}</div>
                <div>失1球 {{ analysisData.awayLoseQiu_1 ?? '-' }}</div>
                <div>失2球 {{ analysisData.awayLoseQiu_2 ?? '-' }}</div>
              </div>
              <div class="analysis-sim-panel-grid">
                <div>输1球差距 {{ analysisData.awayLoseGap_1 ?? '-' }}</div>
                <div>输2球差距 {{ analysisData.awayLoseGap_2 ?? '-' }}</div>
                <div>-</div>
              </div>
            </div>
          </div>
        </div>

        <div class="analysis-sim-card">
          <div class="analysis-sim-card-title">历史交锋</div>
          <div class="analysis-sim-summary">{{ analysisData.jiaoFenDesc || '-' }}</div>
          <div class="analysis-sim-history">
            <div v-for="item in getJiaoFenMatches(analysisData)" :key="item" class="analysis-sim-history-item">{{ item }}</div>
            <div v-if="!getJiaoFenMatches(analysisData).length" class="analysis-sim-history-item">暂无交锋记录</div>
          </div>
        </div>

        <div class="analysis-sim-card">
          <div class="analysis-sim-card-title">数据源信息</div>
          <div class="analysis-sim-source">
            <div><span>lineId:</span><strong>{{ analysisData.lineId || '-' }}</strong></div>
            <div><span>数据来源:</span><strong>100球分析页面</strong></div>
            <div><span>URL:</span><strong>https://m.100qiu.com/analysis/detail.php?lotteryType=40&term=26023&lineId={{ analysisData.lineId || '-' }}</strong></div>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="analysis-empty">暂无原始数据，请先通过数据源配置抓取入库。</div>
  </el-dialog>
</template>

<script>
import { defineComponent, computed } from 'vue';
import { ElDialog, ElProgress } from 'element-plus';

export default defineComponent({
  name: 'AnalysisDialog',
  components: {
    ElDialog,
    ElProgress
  },
  props: {
    visible: {
      type: Boolean,
      required: true
    },
    analysisData: {
      type: Object,
      default: null
    }
  },
  emits: ['update:visible'],
  setup(props, { emit }) {
    const dialogVisible = computed({
      get: () => props.visible,
      set: (val) => emit('update:visible', val)
    });

    const getJiaoFenMatches = (data) => {
      if (!data) return [];
      const matches = [];
      for (let i = 1; i <= 6; i += 1) {
        const key = `jiaoFenMatch${i}`;
        if (data[key]) matches.push(data[key]);
      }
      return matches;
    };

    const getPercentValue = (value) => {
      if (!value) return 0;
      const match = String(value).match(/(\d+)(?:\.\d+)?%/);
      if (match) return Math.min(100, Number(match[1]));
      return 0;
    };

    const getProgressValue = (value) => {
      const num = Number(value);
      if (Number.isNaN(num)) return 0;
      return Math.max(0, Math.min(100, num));
    };

    const getEfficiencyValue = (value) => {
      if (!value) return 0;
      const parts = String(value).split(':');
      if (parts.length < 2) return 0;
      const num = Number(parts[1]);
      return Number.isNaN(num) ? 0 : num;
    };

    const getSpfWins = (value) => {
      if (!value) return 0;
      const match = String(value).match(/(\d+)胜/);
      if (!match) return 0;
      return Number(match[1]);
    };

    const compareAdvantage = (homeValue, awayValue) => {
      const homeNum = Number(homeValue);
      const awayNum = Number(awayValue);
      if (Number.isNaN(homeNum) || Number.isNaN(awayNum)) return '持平';
      if (homeNum > awayNum) return '主队';
      if (homeNum < awayNum) return '客队';
      return '持平';
    };

    return {
      dialogVisible,
      getJiaoFenMatches,
      getPercentValue,
      getProgressValue,
      getEfficiencyValue,
      getSpfWins,
      compareAdvantage
    };
  }
});
</script>

<style scoped>
.analysis-dialog :deep(.el-dialog) {
  max-width: 920px;
  width: 92%;
}

.analysis-sim-container {
  display: grid;
  gap: 16px;
}

.analysis-sim-header {
  padding: 12px 16px;
  border-radius: 12px;
  background: #f4f1ed;
  border: 1px solid #e4dfd8;
}

.analysis-sim-title {
  font-size: 18px;
  font-weight: 700;
  color: #5a534e;
}

.analysis-sim-subtitle {
  font-size: 13px;
  color: #8b8680;
  margin-top: 4px;
}

.analysis-sim-card {
  border: 1px solid #e2ddd6;
  border-radius: 12px;
  padding: 14px 16px;
  background: #fdfcfb;
}

.analysis-sim-card-title {
  font-size: 14px;
  font-weight: 600;
  color: #6b6763;
  margin-bottom: 10px;
}

.analysis-sim-basic {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.analysis-sim-team {
  text-align: center;
}

.analysis-sim-team-name {
  font-size: 18px;
  font-weight: 700;
  color: #5a534e;
}

.analysis-sim-team-meta {
  font-size: 12px;
  color: #8b8680;
  margin-top: 4px;
}

.analysis-sim-vs {
  text-align: center;
  color: #7a7067;
}

.analysis-sim-league {
  font-size: 13px;
  font-weight: 600;
}

.analysis-sim-vs-text {
  font-size: 22px;
  font-weight: 700;
  margin: 4px 0;
  color: #b36b5e;
}

.analysis-sim-time {
  font-size: 12px;
  color: #8b8680;
}

.analysis-sim-odds {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
}

.analysis-sim-odds-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px;
  border-radius: 8px;
  background: #f6f2ee;
  border: 1px solid #e4dfd8;
  font-size: 12px;
  color: #8b8680;
  text-align: center;
}

.analysis-sim-odds-item strong {
  color: #5a534e;
  font-size: 16px;
}

.analysis-sim-progress {
  display: grid;
  gap: 8px;
  margin-bottom: 12px;
}

.analysis-sim-progress-labels {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #6f6a64;
}

.analysis-sim-progress-bars :deep(.el-progress__bar) {
  height: 10px;
  border-radius: 999px;
}

.analysis-sim-table {
  border: 1px solid #ece6df;
  border-radius: 10px;
  overflow: hidden;
}

.analysis-sim-table-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(90px, 1fr));
  padding: 10px 12px;
  font-size: 13px;
  color: #6f6a64;
  border-bottom: 1px solid #eee8e1;
}

.analysis-sim-table-row:last-child {
  border-bottom: none;
}

.analysis-sim-table-head {
  background: #f2eeea;
  font-weight: 600;
  color: #6b6763;
}

.analysis-sim-odds-panels {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.analysis-sim-odds-panel,
.analysis-sim-lose-panel {
  border: 1px solid #e4dfd8;
  border-radius: 10px;
  padding: 12px;
  background: #f8f5f1;
  text-align: center;
}

.analysis-sim-panel-title {
  font-size: 13px;
  color: #8b8680;
  margin-bottom: 6px;
}

.analysis-sim-panel-value {
  font-size: 22px;
  font-weight: 700;
  color: #b36b5e;
  margin-bottom: 8px;
}

.analysis-sim-panel-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
  font-size: 12px;
  color: #6f6a64;
}

.analysis-sim-lose {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.analysis-sim-summary {
  padding: 10px 12px;
  background: #f4f1ed;
  border-radius: 8px;
  color: #6f6a64;
  font-size: 13px;
}

.analysis-sim-history {
  display: grid;
  gap: 8px;
  margin-top: 10px;
}

.analysis-sim-history-item {
  padding: 8px 10px;
  border: 1px solid #e4dfd8;
  border-radius: 8px;
  background: #fdfcfb;
  font-size: 12px;
  color: #6f6a64;
}

.analysis-sim-source {
  display: grid;
  gap: 8px;
  font-size: 12px;
  color: #6f6a64;
}

.analysis-sim-source span {
  color: #8b8680;
  margin-right: 6px;
}

@media (max-width: 900px) {
  .analysis-sim-basic {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .analysis-sim-table-row {
    grid-template-columns: repeat(2, minmax(90px, 1fr));
    row-gap: 6px;
  }
}

.analysis-empty {
  color: #8b8680;
  font-size: 14px;
  padding: 16px 0;
}
</style>