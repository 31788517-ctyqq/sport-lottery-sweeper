<template>
  <div class="match-analysis-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">📊 比赛分析模拟</h1>
      <p class="page-description">基于100球数据的比赛分析展示</p>
    </div>

    <!-- 比赛基本信息卡片 -->
    <el-row :gutter="20" class="section-row">
      <el-col :span="24">
        <el-card class="box-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>比赛基本信息</span>
            </div>
          </template>
          <div class="match-basic-info">
            <div class="teams-display">
              <div class="team home-team">
                <div class="team-name">{{ matchData.homeTeam }}</div>
                <div class="team-power">实力值: {{ matchData.homePower }}</div>
              </div>
              <div class="vs-separator">
                <div class="league">{{ matchData.gameShortName }}</div>
                <div class="vs">VS</div>
                <div class="match-time">{{ matchData.matchTimeStr }}</div>
              </div>
              <div class="team away-team">
                <div class="team-name">{{ matchData.guestTeam }}</div>
                <div class="team-power">实力值: {{ matchData.guestPower }}</div>
              </div>
            </div>
            
            <div class="odds-row">
              <div class="odds-item">
                <span class="odds-label">主胜:</span>
                <span class="odds-value">{{ matchData.homeWinAward }}</span>
              </div>
              <div class="odds-item">
                <span class="odds-label">平局:</span>
                <span class="odds-value">{{ matchData.drawAward }}</span>
              </div>
              <div class="odds-item">
                <span class="odds-label">客胜:</span>
                <span class="odds-value">{{ matchData.guestWinAward }}</span>
              </div>
              <div class="odds-item">
                <span class="odds-label">让球:</span>
                <span class="odds-value">{{ matchData.rq }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 球队实力对比 -->
    <el-row :gutter="20" class="section-row">
      <el-col :span="24">
        <el-card class="box-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>球队实力对比</span>
            </div>
          </template>
          <div class="team-comparison">
            <!-- 实力对比进度条 -->
            <div class="power-comparison">
              <div class="power-bar-container">
                <div class="power-labels">
                  <span class="team-label home-label">{{ matchData.homeTeam }}</span>
                </div>
                <el-progress 
                  :percentage="matchData.homePower" 
                  :show-text="false"
                  class="power-bar"
                  :color="'#409EFF'"
                />
                <el-progress 
                  :percentage="matchData.guestPower" 
                  :show-text="false"
                  class="power-bar"
                  :color="'#F56C6C'"
                />
                <div class="power-labels">
                  <span class="team-label away-label">{{ matchData.guestTeam }}</span>
                </div>
              </div>
            </div>
            
            <!-- 对比表格 -->
            <div class="comparison-table">
              <table class="comparison-table-inner">
                <thead>
                  <tr>
                    <th class="metric-column">指标</th>
                    <th class="home-column">{{ matchData.homeTeam }}</th>
                    <th class="away-column">{{ matchData.guestTeam }}</th>
                    <th class="advantage-column">优势方</th>
                  </tr>
                </thead>
                <tbody>
                  <!-- 积分对比 -->
                  <tr>
                    <td class="metric-column">积分（主场/总）</td>
                    <td class="home-column">{{ matchData.homeJiFenHome }}/{{ matchData.homeJiFenHomeAll }}</td>
                    <td class="away-column">{{ matchData.awayJiFenHome }}/{{ matchData.awayJiFenHomeAll }}</td>
                    <td class="advantage-column">
                      <span v-if="parseFloat(matchData.homeJiFenHome) > parseFloat(matchData.awayJiFenHome)" class="advantage home-advantage">主队</span>
                      <span v-else-if="parseFloat(matchData.homeJiFenHome) < parseFloat(matchData.awayJiFenHome)" class="advantage away-advantage">客队</span>
                      <span v-else class="advantage draw">持平</span>
                    </td>
                  </tr>
                  <!-- 客场积分（仅客队） -->
                  <tr>
                    <td class="metric-column">客场积分</td>
                    <td class="home-column">-</td>
                    <td class="away-column">{{ matchData.awayJiFenGuest }}</td>
                    <td class="advantage-column">
                      <span class="advantage away-advantage">客队</span>
                    </td>
                  </tr>
                  <!-- 特征对比 -->
                  <tr>
                    <td class="metric-column">特征</td>
                    <td class="home-column">{{ matchData.homeFeature }}</td>
                    <td class="away-column">{{ matchData.guestFeature }}</td>
                    <td class="advantage-column">
                      <span v-if="parseInt(matchData.homeFeature) > parseInt(matchData.guestFeature)" class="advantage home-advantage">主队</span>
                      <span v-else-if="parseInt(matchData.homeFeature) < parseInt(matchData.guestFeature)" class="advantage away-advantage">客队</span>
                      <span v-else class="advantage draw">持平</span>
                    </td>
                  </tr>
                  <!-- 进攻效率对比 -->
                  <tr>
                    <td class="metric-column">进攻效率</td>
                    <td class="home-column">{{ matchData.homeEnterEfficiency }}</td>
                    <td class="away-column">{{ matchData.guestEnterEfficiency }}</td>
                    <td class="advantage-column">
                      <span v-if="parseFloat(matchData.homeEnterEfficiency.split(':')[1]) > parseFloat(matchData.guestEnterEfficiency.split(':')[1])" class="advantage home-advantage">主队</span>
                      <span v-else-if="parseFloat(matchData.homeEnterEfficiency.split(':')[1]) < parseFloat(matchData.guestEnterEfficiency.split(':')[1])" class="advantage away-advantage">客队</span>
                      <span v-else class="advantage draw">持平</span>
                    </td>
                  </tr>
                  <!-- 防守效率对比 -->
                  <tr>
                    <td class="metric-column">防守效率</td>
                    <td class="home-column">{{ matchData.homePreventEfficiency }}</td>
                    <td class="away-column">{{ matchData.guestPreventEfficiency }}</td>
                    <td class="advantage-column">
                      <span v-if="parseFloat(matchData.homePreventEfficiency.split(':')[1]) > parseFloat(matchData.guestPreventEfficiency.split(':')[1])" class="advantage home-advantage">主队</span>
                      <span v-else-if="parseFloat(matchData.homePreventEfficiency.split(':')[1]) < parseFloat(matchData.guestPreventEfficiency.split(':')[1])" class="advantage away-advantage">客队</span>
                      <span v-else class="advantage draw">持平</span>
                    </td>
                  </tr>
                  <!-- 近期战绩对比 -->
                  <tr>
                    <td class="metric-column">近期战绩</td>
                    <td class="home-column">{{ matchData.homeSpf }}</td>
                    <td class="away-column">{{ matchData.guestSpf }}</td>
                    <td class="advantage-column">
                      <span v-if="parseInt(matchData.homeSpf.split('胜')[0]) > parseInt(matchData.guestSpf.split('胜')[0])" class="advantage home-advantage">主队</span>
                      <span v-else-if="parseInt(matchData.homeSpf.split('胜')[0]) < parseInt(matchData.guestSpf.split('胜')[0])" class="advantage away-advantage">客队</span>
                      <span v-else class="advantage draw">持平</span>
                    </td>
                  </tr>
                  <!-- 大球百分比对比 -->
                  <tr>
                    <td class="metric-column">大球百分比</td>
                    <td class="home-column">{{ matchData.homeDxqPercentStr }}</td>
                    <td class="away-column">{{ matchData.guestDxqPercentStr }}</td>
                    <td class="advantage-column">
                      <span v-if="parseInt(matchData.homeDxqPercentStr) > parseInt(matchData.guestDxqPercentStr)" class="advantage home-advantage">主队</span>
                      <span v-else-if="parseInt(matchData.homeDxqPercentStr) < parseInt(matchData.guestDxqPercentStr)" class="advantage away-advantage">客队</span>
                      <span v-else class="advantage draw">持平</span>
                    </td>
                  </tr>
                  <!-- 近期进球/失球对比 -->
                  <tr>
                    <td class="metric-column">近期进球/失球</td>
                    <td class="home-column">{{ matchData.homeDxqDesc }}</td>
                    <td class="away-column">{{ matchData.guestDxqDesc }}</td>
                    <td class="advantage-column">
                      <span class="advantage info">需具体分析</span>
                    </td>
                  </tr>
                  <!-- 主场/客场进球/失球对比 -->
                  <tr>
                    <td class="metric-column">主场/客场表现</td>
                    <td class="home-column">{{ matchData.homeDxqSame10Desc }}</td>
                    <td class="away-column">{{ matchData.awayDxqSame10Desc }}</td>
                    <td class="advantage-column">
                      <span class="advantage info">需具体分析</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 赔率对比分析 -->
    <el-row :gutter="20" class="section-row">
      <el-col :span="24">
        <el-card class="box-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>赔率对比分析</span>
            </div>
          </template>
          <div class="odds-comparison">
            <!-- 胜盘对比 -->
            <div class="odds-comparison-row">
              <div class="odds-comparison-panel home-odds-panel">
                <h3>主胜盘</h3>
                <div class="odds-comparison-value home-odds-value">{{ matchData.homeWinPan }}</div>
                <div class="odds-breakdown-grid">
                  <div class="breakdown-cell home-breakdown-cell">
                    <div class="breakdown-cell-label">进0球</div>
                    <div class="breakdown-cell-value">{{ matchData.homeWinQiu_0 }}</div>
                  </div>
                  <div class="breakdown-cell home-breakdown-cell">
                    <div class="breakdown-cell-label">进1球</div>
                    <div class="breakdown-cell-value">{{ matchData.homeWinQiu_1 }}</div>
                  </div>
                  <div class="breakdown-cell home-breakdown-cell">
                    <div class="breakdown-cell-label">进2球</div>
                    <div class="breakdown-cell-value">{{ matchData.homeWinQiu_2 }}</div>
                  </div>
                </div>
                <div class="gap-analysis-grid">
                  <div class="gap-cell home-gap-cell">
                    <div class="gap-cell-label">赢1球差距</div>
                    <div class="gap-cell-value">{{ matchData.homeWinGap_1 }}</div>
                  </div>
                  <div class="gap-cell home-gap-cell">
                    <div class="gap-cell-label">赢2球差距</div>
                    <div class="gap-cell-value">{{ matchData.homeWinGap_2 }}</div>
                  </div>
                </div>
              </div>
              
              <div class="odds-comparison-panel away-odds-panel">
                <h3>客胜盘</h3>
                <div class="odds-comparison-value away-odds-value">{{ matchData.guestWinPan }}</div>
                <div class="odds-breakdown-grid">
                  <div class="breakdown-cell away-breakdown-cell">
                    <div class="breakdown-cell-label">进0球</div>
                    <div class="breakdown-cell-value">{{ matchData.awayWinQiu_0 }}</div>
                  </div>
                  <div class="breakdown-cell away-breakdown-cell">
                    <div class="breakdown-cell-label">进1球</div>
                    <div class="breakdown-cell-value">{{ matchData.awayWinQiu_1 }}</div>
                  </div>
                  <div class="breakdown-cell away-breakdown-cell">
                    <div class="breakdown-cell-label">进2球</div>
                    <div class="breakdown-cell-value">{{ matchData.awayWinQiu_2 }}</div>
                  </div>
                </div>
                <div class="gap-analysis-grid">
                  <div class="gap-cell away-gap-cell">
                    <div class="gap-cell-label">赢1球差距</div>
                    <div class="gap-cell-value">{{ matchData.awayWinGap_1 }}</div>
                  </div>
                  <div class="gap-cell away-gap-cell">
                    <div class="gap-cell-label">赢2球差距</div>
                    <div class="gap-cell-value">{{ matchData.awayWinGap_2 }}</div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 失球对比 -->
            <div class="lose-comparison">
              <h3 style="text-align: center; margin-bottom: 20px; color: #303133;">失球对比</h3>
              <div class="lose-comparison-row">
                <div class="lose-comparison-panel home-lose-panel">
                  <h4>主队失球</h4>
                  <div class="lose-grid">
                    <div class="lose-cell home-lose-cell">
                      <div class="lose-cell-label">失0球</div>
                      <div class="lose-cell-value">{{ matchData.homeLoseQiu_0 }}</div>
                    </div>
                    <div class="lose-cell home-lose-cell">
                      <div class="lose-cell-label">失1球</div>
                      <div class="lose-cell-value">{{ matchData.homeLoseQiu_1 }}</div>
                    </div>
                    <div class="lose-cell home-lose-cell">
                      <div class="lose-cell-label">失2球</div>
                      <div class="lose-cell-value">{{ matchData.homeLoseQiu_2 }}</div>
                    </div>
                  </div>
                  <div class="gap-grid">
                    <div class="gap-cell home-gap-cell">
                      <div class="gap-cell-label">输1球差距</div>
                      <div class="gap-cell-value">{{ matchData.homeLoseGap_1 }}</div>
                    </div>
                    <div class="gap-cell home-gap-cell">
                      <div class="gap-cell-label">输2球差距</div>
                      <div class="gap-cell-value">{{ matchData.homeLoseGap_2 }}</div>
                    </div>
                  </div>
                </div>
                
                <div class="lose-comparison-panel away-lose-panel">
                  <h4>客队失球</h4>
                  <div class="lose-grid">
                    <div class="lose-cell away-lose-cell">
                      <div class="lose-cell-label">失0球</div>
                      <div class="lose-cell-value">{{ matchData.awayLoseQiu_0 }}</div>
                    </div>
                    <div class="lose-cell away-lose-cell">
                      <div class="lose-cell-label">失1球</div>
                      <div class="lose-cell-value">{{ matchData.awayLoseQiu_1 }}</div>
                    </div>
                    <div class="lose-cell away-lose-cell">
                      <div class="lose-cell-label">失2球</div>
                      <div class="lose-cell-value">{{ matchData.awayLoseQiu_2 }}</div>
                    </div>
                  </div>
                  <div class="gap-grid">
                    <div class="gap-cell away-gap-cell">
                      <div class="gap-cell-label">输1球差距</div>
                      <div class="gap-cell-value">{{ matchData.awayLoseGap_1 }}</div>
                    </div>
                    <div class="gap-cell away-gap-cell">
                      <div class="gap-cell-label">输2球差距</div>
                      <div class="gap-cell-value">{{ matchData.awayLoseGap_2 }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 历史交锋 -->
    <el-row :gutter="20" class="section-row">
      <el-col :span="24">
        <el-card class="box-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>历史交锋</span>
            </div>
          </template>
          <div class="historical-data">
            <div class="summary">
              <p>{{ matchData.jiaoFenDesc }}</p>
            </div>
            <div class="match-history">
              <div class="history-item">
                <div class="history-match">{{ matchData.jiaoFenMatch1 }}</div>
              </div>
              <div class="history-item">
                <div class="history-match">{{ matchData.jiaoFenMatch2 }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 数据源信息 -->
    <el-row :gutter="20" class="section-row">
      <el-col :span="24">
        <el-card class="box-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>数据源信息</span>
            </div>
          </template>
          <div class="source-info">
            <div class="source-item">
              <span class="label">lineId:</span>
              <span class="value">{{ matchData.lineId }}</span>
            </div>
            <div class="source-item">
              <span class="label">数据来源:</span>
              <span class="value">100球分析页面</span>
            </div>
            <div class="source-item">
              <span class="label">URL:</span>
              <span class="value">https://m.100qiu.com/analysis/detail.php?lotteryType=40&term=26023&lineId=138</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 定义比赛数据
const matchData = ref({
  lineId: "001",
  rq: "0",
  homeTeam: "惠灵顿凤凰",
  guestTeam: "墨尔本胜利",
  homePower: 44,
  homeJiFenHomeAll: "1.27",
  homeJiFenHome: "1.38",
  guestPower: 56,
  awayJiFenHomeAll: "1.33",
  awayJiFenHome: "1.86",
  awayJiFenGuest: "0.88",
  homeWinPan: 0.9,
  homeWinQiu_0: 1,
  homeWinQiu_1: 4,
  homeWinQiu_2: 5,
  homeLoseQiu_0: 2,
  homeLoseQiu_1: 4,
  homeLoseQiu_2: 4,
  guestWinPan: 0.56,
  awayWinQiu_0: 4,
  awayWinQiu_1: 2,
  awayWinQiu_2: 4,
  awayLoseQiu_0: 4,
  awayLoseQiu_1: 3,
  awayLoseQiu_2: 3,
  homeFeature: "一赔概率50%",
  guestFeature: "一赔概率44%",
  homeEnterEfficiency: "进攻:0.19",
  homePreventEfficiency: "防守:-0.17",
  guestEnterEfficiency: "进攻:0.12",
  guestPreventEfficiency: "防守:-0.12",
  homeSpf: "5胜2平3负",
  guestSpf: "4胜1平5负",
  homeWinGap_1: 4,
  homeWinGap_2: 1,
  homeLoseGap_1: 2,
  homeLoseGap_2: 1,
  awayWinGap_1: 1,
  awayWinGap_2: 3,
  awayLoseGap_1: 3,
  awayLoseGap_2: 2,
  homeDxqPercentStr: "80%",
  guestDxqPercentStr: "30%",
  homeDxqDesc: "近期:进球1.8 失球2.1",
  guestDxqDesc: "近期:进球1.6 失球0.9",
  homeDxqSame10Desc: "主场:进球1.5 失球1.3",
  awayDxqSame10Desc: "客场:进球1.4 失球1.3",
  jiaoFenDesc: "双方近6次交战,惠灵顿凤凰123,进5球,失10,大球2次,小球4次",
  jiaoFenMatch1: "澳超   2025-12-29   墨尔本胜利   5:1   惠灵顿凤凰   负",
  jiaoFenMatch2: "澳超   2025-04-12   惠灵顿凤凰   2:3   墨尔本胜利   负",
  matchTimeStr: "2026-02-06",
  gameShortName: "澳超",
  homeWinAward: "3.43",
  guestWinAward: "2.13",
  drawAward: "4.14"
})
</script>

<style scoped>
.match-analysis-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
}

.page-description {
  font-size: 16px;
  color: #606266;
}

.section-row {
  margin-bottom: 20px;
}

.card-header {
  font-size: 18px;
  font-weight: 600;
}

.match-basic-info {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.teams-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-bottom: 20px;
}

.team {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.home-team {
  text-align: right;
}

.away-team {
  text-align: left;
}

.team-name {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 8px;
}

.team-power {
  font-size: 16px;
  color: #606266;
}

.vs-separator {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 0 30px;
}

.league {
  font-size: 18px;
  font-weight: 600;
  color: #409EFF;
  margin-bottom: 8px;
}

.vs {
  font-size: 32px;
  font-weight: bold;
  color: #F56C6C;
  margin-bottom: 8px;
}

.match-time {
  font-size: 16px;
  color: #909399;
}

.odds-row {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-top: 20px;
}

.odds-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.odds-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 4px;
}

.odds-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.team-analysis {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.analysis-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.analysis-item:last-child {
  border-bottom: none;
}

.analysis-item .label {
  font-weight: 500;
  color: #606266;
}

.analysis-item .value {
  font-weight: 600;
  color: #303133;
}

.odds-analysis {
  padding: 10px 0;
}

.odds-panel {
  text-align: center;
}

.odds-panel h3 {
  margin-bottom: 16px;
  color: #303133;
}

.odds-value-large {
  font-size: 36px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 20px;
}

.odds-breakdown, .lose-analysis {
  margin-top: 20px;
}

.breakdown-item, .lose-item, .gap-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px dashed #ebeef5;
}

.breakdown-item:last-child, .lose-item:last-child, .gap-item:last-child {
  border-bottom: none;
}

.lose-section {
  margin-bottom: 20px;
}

.lose-section h4 {
  margin-bottom: 12px;
  color: #606266;
}

.historical-data {
  padding: 10px 0;
}

.summary {
  margin-bottom: 20px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.summary p {
  margin: 0;
  color: #606266;
}

.match-history {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.history-match {
  font-family: monospace;
  color: #303133;
}

.source-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.source-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.source-item:last-child {
  border-bottom: none;
}

.source-item .label {
  font-weight: 500;
  color: #606266;
}

.source-item .value {
  font-weight: 600;
  color: #303133;
  word-break: break-all;
}

/* 球队对比样式 */
.team-comparison {
  padding: 10px 0;
}

.power-comparison {
  margin-bottom: 30px;
}

.power-bar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.power-labels {
  display: flex;
  justify-content: space-between;
  width: 100%;
  margin-bottom: 5px;
}

.team-label {
  font-weight: bold;
  font-size: 18px;
}

.home-label {
  color: #409EFF;
}

.away-label {
  color: #F56C6C;
}

.power-value {
  font-weight: bold;
  font-size: 20px;
}

.power-bar {
  width: 100%;
  height: 24px;
  border-radius: 12px;
}

.comparison-table {
  overflow-x: auto;
}

.comparison-table-inner {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.comparison-table-inner th,
.comparison-table-inner td {
  padding: 12px 16px;
  text-align: center;
  border: 1px solid #ebeef5;
}

.comparison-table-inner th {
  background-color: #f5f7fa;
  font-weight: 600;
  color: #303133;
}

.comparison-table-inner .metric-column {
  text-align: left;
  font-weight: 500;
  color: #606266;
  background-color: #fafafa;
  width: 25%;
}

.comparison-table-inner .home-column {
  background-color: rgba(64, 158, 255, 0.05);
  color: #409EFF;
  font-weight: 600;
  width: 25%;
}

.comparison-table-inner .away-column {
  background-color: rgba(245, 108, 108, 0.05);
  color: #F56C6C;
  font-weight: 600;
  width: 25%;
}

.comparison-table-inner .advantage-column {
  width: 25%;
}

.advantage {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.home-advantage {
  background-color: rgba(64, 158, 255, 0.1);
  color: #409EFF;
  border: 1px solid rgba(64, 158, 255, 0.3);
}

.away-advantage {
  background-color: rgba(245, 108, 108, 0.1);
  color: #F56C6C;
  border: 1px solid rgba(245, 108, 108, 0.3);
}

.draw {
  background-color: rgba(144, 147, 153, 0.1);
  color: #909399;
  border: 1px solid rgba(144, 147, 153, 0.3);
}

.info {
  background-color: rgba(103, 194, 58, 0.1);
  color: #67C23A;
  border: 1px solid rgba(103, 194, 58, 0.3);
}

/* 赔率对比样式 */
.odds-comparison {
  padding: 10px 0;
}

.odds-comparison-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.odds-comparison-panel {
  flex: 1;
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  margin: 0 10px;
}

.home-odds-panel {
  background-color: rgba(64, 158, 255, 0.05);
  border: 1px solid rgba(64, 158, 255, 0.2);
}

.away-odds-panel {
  background-color: rgba(245, 108, 108, 0.05);
  border: 1px solid rgba(245, 108, 108, 0.2);
}

.odds-comparison-panel h3 {
  margin-bottom: 16px;
  color: #303133;
}

.odds-comparison-value {
  font-size: 42px;
  font-weight: bold;
  margin-bottom: 20px;
}

.home-odds-value {
  color: #409EFF;
}

.away-odds-value {
  color: #F56C6C;
}

.odds-breakdown-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-top: 20px;
}

.breakdown-cell {
  padding: 10px;
  border-radius: 4px;
  text-align: center;
}

.home-breakdown-cell {
  background-color: rgba(64, 158, 255, 0.08);
  border: 1px solid rgba(64, 158, 255, 0.15);
}

.away-breakdown-cell {
  background-color: rgba(245, 108, 108, 0.08);
  border: 1px solid rgba(245, 108, 108, 0.15);
}

.breakdown-cell-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.breakdown-cell-value {
  font-size: 20px;
  font-weight: bold;
}

.gap-analysis-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-top: 20px;
}

.gap-cell {
  padding: 8px;
  border-radius: 4px;
  text-align: center;
}

.home-gap-cell {
  background-color: rgba(64, 158, 255, 0.05);
  border: 1px solid rgba(64, 158, 255, 0.1);
}

.away-gap-cell {
  background-color: rgba(245, 108, 108, 0.05);
  border: 1px solid rgba(245, 108, 108, 0.1);
}

.gap-cell-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 2px;
}

.gap-cell-value {
  font-size: 18px;
  font-weight: bold;
}

/* 失球对比样式 */
.lose-comparison {
  margin-top: 30px;
}

.lose-comparison-row {
  display: flex;
  justify-content: space-between;
  gap: 20px;
}

.lose-comparison-panel {
  flex: 1;
  padding: 20px;
  border-radius: 8px;
}

.home-lose-panel {
  background-color: rgba(64, 158, 255, 0.03);
  border: 1px solid rgba(64, 158, 255, 0.1);
}

.away-lose-panel {
  background-color: rgba(245, 108, 108, 0.03);
  border: 1px solid rgba(245, 108, 108, 0.1);
}

.lose-comparison-panel h4 {
  margin-bottom: 16px;
  color: #606266;
  text-align: center;
}

.lose-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 20px;
}

.lose-cell {
  padding: 8px;
  border-radius: 4px;
  text-align: center;
}

.home-lose-cell {
  background-color: rgba(64, 158, 255, 0.05);
  border: 1px solid rgba(64, 158, 255, 0.1);
}

.away-lose-cell {
  background-color: rgba(245, 108, 108, 0.05);
  border: 1px solid rgba(245, 108, 108, 0.1);
}

.lose-cell-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 2px;
}

.lose-cell-value {
  font-size: 18px;
  font-weight: bold;
}

.gap-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

/* 小型实力对比条样式 */
.power-mini-comparison {
  margin: 20px 0;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.power-bar-labels {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.power-mini-label {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

.power-mini-bar-container {
  position: relative;
  width: 100%;
  height: 24px;
  background-color: #e4e7ed;
  border-radius: 12px;
  overflow: hidden;
}

.power-mini-bar {
  position: absolute;
  top: 0;
  height: 100%;
  transition: width 0.5s ease;
}

.home-power-bar {
  left: 0;
  background-color: #409EFF;
  border-radius: 12px 0 0 12px;
}

.away-power-bar {
  right: 0;
  background-color: #F56C6C;
  border-radius: 0 12px 12px 0;
}

.power-bar-names {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
}

.power-name {
  font-size: 14px;
  font-weight: 500;
}

.home-name {
  color: #409EFF;
}

.away-name {
  color: #F56C6C;
}
</style>