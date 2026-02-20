<template>
  <div class="collection-page">
    <el-card class="block">
      <template #header>
        <div class="block-header">
          <div>
            <h3>情报采集管理（降本可落地版）</h3>
            <p>按竞彩赛程创建采集任务，支持即时采集、计划采集、来源观点查看与钉钉推送预览。</p>
          </div>
          <el-button @click="reloadAll" :icon="Refresh">刷新</el-button>
        </div>
      </template>

      <el-form :model="query" inline>
        <el-form-item label="赛程日期">
          <el-date-picker
            v-model="query.date"
            type="date"
            value-format="YYYY-MM-DD"
            format="YYYY-MM-DD"
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="query.search" placeholder="联赛/球队关键词" clearable style="width: 220px" />
        </el-form-item>
        <el-form-item label="采集模式">
          <el-radio-group v-model="taskForm.mode">
            <el-radio-button value="immediate">即时采集</el-radio-button>
            <el-radio-button value="scheduled">计划采集</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="来源">
          <el-select v-model="taskForm.sources" multiple collapse-tags style="width: 360px">
            <el-option v-for="s in sourceOptions" :key="s.code" :label="s.code" :value="s.code" />
          </el-select>
        </el-form-item>
        <el-form-item label="情报类型">
          <el-select v-model="taskForm.intelTypes" multiple collapse-tags style="width: 420px">
            <el-option v-for="t in intelTypeOptions" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="taskForm.mode === 'scheduled'" label="时点">
          <el-checkbox-group v-model="taskForm.offsetHours">
            <el-checkbox :label="24">24h</el-checkbox>
            <el-checkbox :label="12">12h</el-checkbox>
            <el-checkbox :label="6">6h</el-checkbox>
            <el-checkbox :label="1">1h</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="时间窗阈值">
          <div class="time-window-config">
            <el-input-number
              v-model="timeWindowForm.beforeHours"
              :min="1"
              :max="720"
              controls-position="right"
              size="small"
            />
            <span>h 前</span>
            <span>~</span>
            <el-input-number
              v-model="timeWindowForm.afterHours"
              :min="0"
              :max="72"
              controls-position="right"
              size="small"
            />
            <span>h 后</span>
            <span>严格模式</span>
            <el-switch v-model="timeWindowForm.strictMode" size="small" />
            <el-button
              size="small"
              type="primary"
              plain
              :loading="loading.saveTimeWindow"
              @click="saveTimeWindowConfig"
            >
              保存阈值
            </el-button>
            <el-tag size="small" type="info">{{ timeWindowMeta.boundsLabel }}</el-tag>
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading.matches" @click="loadMatches">查询赛程</el-button>
          <el-button type="success" :loading="loading.createTask" @click="submitTask">创建任务</el-button>
          <el-button type="warning" plain @click="openAdvancedSettings">采集参数</el-button>
        </el-form-item>
      </el-form>
      <div v-if="query.search && query.search.trim()" class="active-filter-tip">
        <el-alert type="warning" :closable="false" show-icon>
          <template #title>
            当前按关键词筛选：
            <el-tag type="warning" effect="dark" size="small">{{ query.search }}</el-tag>
            ，会只显示命中该关键词的比赛。
            <el-button link type="primary" @click="clearKeywordAndReload">清空关键词并重查</el-button>
          </template>
        </el-alert>
      </div>

      <el-table
        ref="matchTableRef"
        v-loading="loading.matches"
        :data="displayedMatches"
        stripe
        height="320"
        @selection-change="onMatchSelectionChange"
        @row-click="onSelectMatch"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="league_name" label="联赛" width="130" />
        <el-table-column prop="kickoff_time" label="开赛时间" width="175" />
        <el-table-column prop="home_team" label="主队" min-width="140" />
        <el-table-column prop="away_team" label="客队" min-width="140" />
        <el-table-column prop="status" label="状态" width="100" />
      </el-table>
      <div class="selection-tip">
        已选择 {{ selectedMatchIds.length }} 场
        <el-divider direction="vertical" />
        <el-switch
          v-model="onlyMatchesWithItems"
          inline-prompt
          active-text="只看有结果比赛"
          inactive-text="显示全部比赛"
          :loading="indexingMatches"
        />
        <span v-if="onlyMatchesWithItems" class="selection-sub-tip">
          命中 {{ displayedMatches.length }}/{{ matches.length }} 场
        </span>
      </div>
    </el-card>

    <el-row :gutter="16" class="row">
      <el-col :span="14">
        <el-card class="block">
          <template #header>
            <div class="block-header-inline">
              <span>采集任务</span>
              <el-select v-model="taskQuery.status" style="width: 140px" @change="loadTasks">
                <el-option label="全部状态" value="" />
                <el-option label="待执行" value="pending" />
                <el-option label="执行中" value="running" />
                <el-option label="执行成功" value="success" />
                <el-option label="部分成功" value="partial" />
                <el-option label="已取消" value="cancelled" />
                <el-option label="执行失败" value="failed" />
              </el-select>
            </div>
          </template>
          <el-table v-loading="loading.tasks" :data="tasks" stripe height="360">
            <el-table-column prop="id" label="任务ID" width="90" />
            <el-table-column prop="mode" label="模式" width="100" />
            <el-table-column prop="status" label="状态" width="100" />
            <el-table-column label="统计" width="160">
              <template #default="{ row }">
                {{ row.success_count }}/{{ row.total_count }}
              </template>
            </el-table-column>
            <el-table-column label="场次覆盖" width="140">
              <template #default="{ row }">
                {{ row.matched_matches || 0 }}/{{ row.total_matches || 0 }}
                <span class="coverage-rate-text">{{ formatCoverage(row.coverage_rate) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" min-width="170" />
            <el-table-column label="操作" width="300">
              <template #default="{ row }">
                <el-button size="small" type="primary" plain @click="openTaskDetail(row)">详情</el-button>
                <el-button size="small" @click="openTaskLogs(row)">日志</el-button>
                <el-button
                  size="small"
                  type="warning"
                  :loading="isTaskRetrying(row.id)"
                  :disabled="isTaskRetrying(row.id)"
                  @click="retryTask(row)"
                >
                  重试
                </el-button>
                <el-button size="small" type="danger" @click="cancelTask(row)">取消</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="10">
        <el-card class="block">
          <template #header>
            <div class="block-header-inline">
              <span>结果与推送预览（match_id: {{ activeMatchId || '-' }}）</span>
              <el-button size="small" type="primary" :disabled="!activeMatchId" @click="refreshResult">
                刷新结果
              </el-button>
            </div>
          </template>
          <div v-if="taskTracker.visible" class="task-tracker">
            <el-alert
              :type="taskTracker.status === 'failed' ? 'error' : taskTracker.status === 'success' ? 'success' : taskTracker.status === 'partial' ? 'warning' : 'info'"
              :title="taskTracker.message"
              :closable="false"
              show-icon
            />
          </div>

          <el-space wrap>
            <el-button size="small" :disabled="!activeMatchId" @click="loadResult('')">全部</el-button>
            <el-button size="small" :disabled="!activeMatchId" @click="loadResult('off_field')">场外信息</el-button>
            <el-button size="small" :disabled="!activeMatchId" @click="loadResult('prediction')">结果预测</el-button>
            <el-button size="small" type="success" :disabled="!activeMatchId" @click="buildPreview">生成推送预览卡</el-button>
          </el-space>
          <div class="debug-toolbar">
            <el-select v-model="debugForm.source" size="small" style="width: 120px">
              <el-option v-for="s in sourceOptions" :key="s.code" :label="s.code" :value="s.code" />
            </el-select>
            <el-select v-model="debugForm.intelType" size="small" style="width: 160px">
              <el-option v-for="t in intelTypeOptions" :key="t.value" :label="t.label" :value="t.value" />
            </el-select>
            <el-input-number
              v-model="debugForm.maxCandidates"
              :min="5"
              :max="80"
              size="small"
              controls-position="right"
            />
            <el-button
              size="small"
              type="warning"
              plain
              :disabled="!activeMatchId"
              :loading="loading.debugCandidates"
              @click="openCandidateDebug"
            >
              候选调试
            </el-button>
            <el-button
              size="small"
              type="info"
              plain
              :disabled="!activeMatchId"
              :loading="loading.debugReplay"
              @click="openReplayDebug"
            >
              回放调试
            </el-button>
          </div>

          <el-table
            v-loading="loading.items"
            :data="items"
            stripe
            height="240"
            style="margin-top: 10px"
            @row-click="setActiveItem"
          >
            <el-table-column prop="source_code" label="来源" width="90" />
            <el-table-column prop="intel_type" label="情报类型" width="140" />
            <el-table-column label="抓取类型" width="110">
              <template #default="{ row }">
                {{ row.__parsed?.viewTypeLabel || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="匹配分" width="90">
              <template #default="{ row }">
                {{ row.__parsed?.matchScore || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="质量分" width="90">
              <template #default="{ row }">
                {{ row.__parsed?.qualityScore ?? '-' }}
              </template>
            </el-table-column>
            <el-table-column label="AI增强" width="90">
              <template #default="{ row }">
                <el-tag v-if="row.__parsed?.aiEnhanced" type="success" size="small">已增强</el-tag>
                <el-tag v-else type="info" size="small">未增强</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="AI置信度" width="100">
              <template #default="{ row }">
                {{ row.__parsed?.aiConfidence ?? '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="confidence" label="置信度评分" width="100" />
            <el-table-column prop="title" label="标题" min-width="170" show-overflow-tooltip />
            <el-table-column label="原文" width="80">
              <template #default="{ row }">
                <el-link
                  v-if="row.__parsed?.articleUrl"
                  :href="row.__parsed?.articleUrl"
                  type="primary"
                  target="_blank"
                >
                  打开
                </el-link>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="来源观点摘要" min-width="200" show-overflow-tooltip>
              <template #default="{ row }">
                {{ row.__parsed?.aiSummary || row.__parsed?.summary || row.content_raw || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="AI观点" min-width="160" show-overflow-tooltip>
              <template #default="{ row }">
                {{ row.__parsed?.aiViewpoint || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="采纳原因" min-width="150" show-overflow-tooltip>
              <template #default="{ row }">
                {{ row.__parsed?.qualityPassReason || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="过滤原因" min-width="150" show-overflow-tooltip>
              <template #default="{ row }">
                {{ row.__parsed?.qualityBlockReason || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="90">
              <template #default="{ row }">
                <el-button size="small" @click.stop="openItemDetail(row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="result-summary" v-if="items.length">
            <el-tag size="small">总条数 {{ items.length }}</el-tag>
            <el-tag size="small" type="success">文章页 {{ itemStats.article }}</el-tag>
            <el-tag size="small" type="warning">兜底 {{ itemStats.fallback }}</el-tag>
            <el-tag size="small" type="info">来源摘要 {{ itemStats.sourceView }}</el-tag>
            <el-tag size="small" type="success">高质量 {{ itemStats.highQuality }}</el-tag>
            <el-tag size="small" type="primary">AI增强 {{ itemStats.aiEnhanced }}</el-tag>
          </div>

          <el-empty
            v-if="!loading.items && !items.length"
            :description="emptyResultDescription"
          />

          <div v-else class="item-inspector">
            <div class="item-inspector-header">
              <span>采集内容查看区</span>
              <el-button
                v-if="activeItemRow"
                size="small"
                text
                type="primary"
                @click="openItemDetail(activeItemRow)"
              >
                弹窗查看
              </el-button>
            </div>
            <el-descriptions v-if="activeItemParsed" :column="2" border size="small">
              <el-descriptions-item label="来源">{{ activeItemRow?.source_code || '-' }}</el-descriptions-item>
              <el-descriptions-item label="抓取类型">{{ activeItemParsed.viewTypeLabel }}</el-descriptions-item>
              <el-descriptions-item label="情报类型">{{ activeItemRow?.intel_type || '-' }}</el-descriptions-item>
              <el-descriptions-item label="置信度">{{ activeItemRow?.confidence ?? '-' }}</el-descriptions-item>
              <el-descriptions-item label="匹配分">{{ activeItemParsed.matchScore || '-' }}</el-descriptions-item>
              <el-descriptions-item label="质量分">{{ activeItemParsed.qualityScore ?? '-' }}</el-descriptions-item>
              <el-descriptions-item label="AI增强">{{ activeItemParsed.aiEnhanced ? '是' : '否' }}</el-descriptions-item>
              <el-descriptions-item label="AI置信度">{{ activeItemParsed.aiConfidence ?? '-' }}</el-descriptions-item>
              <el-descriptions-item label="AI提供商">{{ activeItemParsed.aiProvider || '-' }}</el-descriptions-item>
              <el-descriptions-item label="AI模型">{{ activeItemParsed.aiModel || '-' }}</el-descriptions-item>
              <el-descriptions-item label="AI风险等级">{{ activeItemParsed.aiRiskLevel || '-' }}</el-descriptions-item>
              <el-descriptions-item label="AI观点" :span="2">{{ activeItemParsed.aiViewpoint || '-' }}</el-descriptions-item>
              <el-descriptions-item label="解析器">{{ activeItemParsed.sourceParser || '-' }}</el-descriptions-item>
              <el-descriptions-item label="命中词" :span="2">
                {{ activeItemParsed.matchHitTerms?.length ? activeItemParsed.matchHitTerms.join(' / ') : '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="标题" :span="2">{{ activeItemParsed.title || '-' }}</el-descriptions-item>
              <el-descriptions-item label="原文链接" :span="2">
                <el-link
                  v-if="activeItemParsed.articleUrl"
                  :href="activeItemParsed.articleUrl"
                  target="_blank"
                  type="primary"
                >
                  {{ activeItemParsed.articleUrl }}
                </el-link>
                <span v-else>-</span>
              </el-descriptions-item>
              <el-descriptions-item label="摘要/观点" :span="2">
                {{ activeItemParsed.aiSummary || activeItemParsed.summary || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="AI说明" :span="2">
                {{ activeItemParsed.aiReason || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="采纳原因" :span="2">
                {{ activeItemParsed.qualityPassReason || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="兜底原因" :span="2">
                {{ activeItemParsed.qualityBlockReason || activeItemParsed.fallbackReason || '-' }}
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <div class="preview-box" v-if="preview">
            <div class="preview-title">{{ preview.headline }}</div>
            <div class="preview-meta">
              <span>置信度：{{ preview.confidence_score ?? preview.confidence }}</span>
              <span>风险等级：{{ preview.risk_level }}</span>
              <span>推送状态：{{ preview.status }}</span>
            </div>
            <ul>
              <li v-for="(e, i) in (preview.evidence || [])" :key="i">
                [{{ e.source }}] {{ e.content }}
              </li>
            </ul>
          </div>

          <el-divider />
          <el-form :model="dingtalkForm" label-width="85px">
            <el-form-item label="Webhook">
              <el-input v-model="dingtalkForm.webhook" placeholder="https://oapi.dingtalk.com/robot/send?access_token=..." />
            </el-form-item>
            <el-form-item label="Secret">
              <el-input v-model="dingtalkForm.secret" placeholder="可选" />
            </el-form-item>
            <el-form-item>
              <el-button :loading="loading.saveBinding" @click="saveBinding">保存绑定</el-button>
              <el-button :loading="loading.testBinding" type="warning" :disabled="!currentBindingId" @click="testBinding">测试发送</el-button>
              <el-button :loading="loading.push" type="primary" :disabled="!preview || !activeMatchId" @click="pushPreview">提交推送任务</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="logDialogVisible" title="任务日志" width="760px">
      <el-timeline>
        <el-timeline-item v-for="(l, idx) in taskLogs" :key="idx" :timestamp="l.time">
          <el-tag :type="logTypeToTag(l.level)" size="small">{{ l.level }}</el-tag>
          <span style="margin-left: 8px">{{ l.message }}</span>
        </el-timeline-item>
      </el-timeline>
    </el-dialog>

    <el-dialog v-model="taskDetailDialogVisible" title="任务详情" width="760px">
      <el-skeleton :loading="taskDetailLoading" animated :rows="6">
        <el-descriptions v-if="taskDetail" :column="2" border size="small">
          <el-descriptions-item label="任务ID">{{ taskDetail.id }}</el-descriptions-item>
          <el-descriptions-item label="任务UUID">{{ taskDetail.task_uuid || '-' }}</el-descriptions-item>
          <el-descriptions-item label="模式">{{ taskDetail.mode || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ taskDetail.status || '-' }}</el-descriptions-item>
          <el-descriptions-item label="统计">
            {{ taskDetail.success_count || 0 }}/{{ taskDetail.total_count || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="失败数">{{ taskDetail.failed_count || 0 }}</el-descriptions-item>
          <el-descriptions-item label="成功率">{{ formatPercent(taskDetail.success_rate) }}</el-descriptions-item>
          <el-descriptions-item label="场次覆盖">
            {{ taskDetail.matched_matches || 0 }}/{{ taskDetail.total_matches || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="覆盖率">
            {{ formatCoverage(taskDetail.coverage_rate) }}
          </el-descriptions-item>
          <el-descriptions-item label="比赛ID" :span="2">
            {{ (taskDetail.match_ids || []).join(', ') || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="场次进度" :span="2">
            {{ formatMatchProgress(taskDetail.match_progress) }}
          </el-descriptions-item>
          <el-descriptions-item label="来源" :span="2">
            {{ (taskDetail.sources || []).join(', ') || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="情报类型" :span="2">
            {{ (taskDetail.intel_types || []).join(', ') || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="错误信息" :span="2">
            {{ taskDetail.error_message || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ taskDetail.created_at || '-' }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ taskDetail.updated_at || '-' }}</el-descriptions-item>
        </el-descriptions>

        <el-divider />
        <div class="block-header-inline" style="margin-bottom: 8px">
          <span>失败摘要</span>
          <el-button
            v-if="taskDetail?.id"
            size="small"
            text
            type="primary"
            :loading="loading.taskFailureSummary"
            @click="loadTaskFailureSummary(taskDetail.id)"
          >
            刷新
          </el-button>
        </div>
        <el-empty
          v-if="!taskFailureSummary || (!taskFailureSummary.top_reasons?.length && !taskFailureSummary.source_failures?.length)"
          description="暂无失败摘要"
        />
        <template v-else>
          <el-alert
            type="warning"
            :closable="false"
            show-icon
            :title="`Top 原因：${formatTopReasons(taskFailureSummary.top_reasons)}`"
            style="margin-bottom: 8px"
          />
          <el-table
            v-if="taskFailureSummary.source_failures?.length"
            :data="taskFailureSummary.source_failures"
            stripe
            max-height="220"
            style="margin-bottom: 8px"
          >
            <el-table-column prop="source" label="来源" width="110" />
            <el-table-column prop="timeout" label="超时" width="80" />
            <el-table-column prop="errors" label="错误" width="80" />
            <el-table-column prop="retries" label="重试" width="80" />
            <el-table-column prop="circuit_skipped" label="熔断跳过" width="100" />
            <el-table-column prop="blocked_decisions" label="拦截数" width="90" />
          </el-table>
        </template>

        <el-divider />
        <div class="block-header-inline" style="margin-bottom: 8px">
          <span>子任务进度（按比赛）</span>
          <span class="coverage-rate-text">共 {{ taskSubtasks.length }} 场</span>
        </div>
        <el-table v-loading="taskSubtasksLoading" :data="taskSubtasks" max-height="300" stripe>
          <el-table-column prop="match_id" label="match_id" width="110" />
          <el-table-column prop="status" label="状态" width="110" />
          <el-table-column label="完成数/期望数" width="150">
            <template #default="{ row }">
              {{ row.item_count || 0 }}/{{ row.expected_count || 0 }}
            </template>
          </el-table-column>
          <el-table-column label="成功/失败" width="140">
            <template #default="{ row }">
              {{ row.success_count || 0 }}/{{ row.failed_count || 0 }}
            </template>
          </el-table-column>
          <el-table-column prop="last_error" label="最后错误" min-width="200" show-overflow-tooltip />
          <el-table-column prop="updated_at" label="更新时间" min-width="170" />
        </el-table>
      </el-skeleton>
    </el-dialog>

    <el-dialog v-model="itemDialogVisible" title="采集内容详情" width="860px">
      <template v-if="itemDetail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="来源">{{ itemDetail.source_code }}</el-descriptions-item>
          <el-descriptions-item label="情报类型">{{ itemDetail.intel_type }}</el-descriptions-item>
          <el-descriptions-item label="置信度">{{ itemDetail.confidence }}</el-descriptions-item>
          <el-descriptions-item label="匹配分">{{ itemDetail.matchScore || '-' }}</el-descriptions-item>
          <el-descriptions-item label="质量分">{{ itemDetail.qualityScore ?? '-' }}</el-descriptions-item>
          <el-descriptions-item label="AI增强">{{ itemDetail.aiEnhanced ? '是' : '否' }}</el-descriptions-item>
          <el-descriptions-item label="AI置信度">{{ itemDetail.aiConfidence ?? '-' }}</el-descriptions-item>
          <el-descriptions-item label="AI提供商">{{ itemDetail.aiProvider || '-' }}</el-descriptions-item>
          <el-descriptions-item label="AI模型">{{ itemDetail.aiModel || '-' }}</el-descriptions-item>
          <el-descriptions-item label="AI风险等级">{{ itemDetail.aiRiskLevel || '-' }}</el-descriptions-item>
          <el-descriptions-item label="AI观点" :span="2">{{ itemDetail.aiViewpoint || '-' }}</el-descriptions-item>
          <el-descriptions-item label="解析器">{{ itemDetail.sourceParser || '-' }}</el-descriptions-item>
          <el-descriptions-item label="命中词" :span="2">
            {{ itemDetail.matchHitTerms?.length ? itemDetail.matchHitTerms.join(' / ') : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="标题" :span="2">{{ itemDetail.title || '-' }}</el-descriptions-item>
          <el-descriptions-item label="原文链接" :span="2">
            <el-link v-if="itemDetail.articleUrl" :href="itemDetail.articleUrl" target="_blank" type="primary">
              {{ itemDetail.articleUrl }}
            </el-link>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="摘要" :span="2">{{ itemDetail.aiSummary || itemDetail.summary || '-' }}</el-descriptions-item>
          <el-descriptions-item label="AI说明" :span="2">{{ itemDetail.aiReason || '-' }}</el-descriptions-item>
          <el-descriptions-item label="采纳原因" :span="2">{{ itemDetail.qualityPassReason || '-' }}</el-descriptions-item>
          <el-descriptions-item label="兜底原因" :span="2">{{ itemDetail.qualityBlockReason || itemDetail.fallbackReason || '-' }}</el-descriptions-item>
        </el-descriptions>
        <el-divider />
        <div class="raw-box">
          <div class="raw-title">原始内容</div>
          <pre>{{ itemDetail.content_raw || '-' }}</pre>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="debugDialogVisible" title="候选抓取调试结果" width="980px">
      <el-descriptions v-if="debugResult" :column="2" border size="small" style="margin-bottom: 10px">
        <el-descriptions-item label="比赛ID">{{ debugResult.match_id || activeMatchId || '-' }}</el-descriptions-item>
        <el-descriptions-item label="来源">{{ debugResult.source || debugForm.source }}</el-descriptions-item>
        <el-descriptions-item label="候选数">{{ debugResult.candidate_count || 0 }}</el-descriptions-item>
        <el-descriptions-item label="评估数">{{ debugResult.evaluated_count || 0 }}</el-descriptions-item>
        <el-descriptions-item label="时间窗">
          {{ debugResult.time_window?.bounds_label || timeWindowMeta.boundsLabel }}
        </el-descriptions-item>
        <el-descriptions-item label="种子页">
          <el-link v-if="debugResult.seed_url" :href="debugResult.seed_url" target="_blank" type="primary">
            {{ debugResult.seed_url }}
          </el-link>
          <span v-else>-</span>
        </el-descriptions-item>
      </el-descriptions>
      <el-table :data="debugCandidates" stripe max-height="420">
        <el-table-column prop="__index" label="#" width="56" />
        <el-table-column prop="score" label="分数" width="80" />
        <el-table-column prop="status_code" label="状态码" width="90" />
        <el-table-column prop="__timePassLabel" label="时间窗" width="90" />
        <el-table-column prop="publish_time" label="发布时间" width="170" />
        <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
        <el-table-column label="命中词" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.__hitTermsText || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="time_window_reason" label="时间窗原因" min-width="180" show-overflow-tooltip />
        <el-table-column prop="filter_reason" label="过滤原因" width="120" />
        <el-table-column label="链接" width="90">
          <template #default="{ row }">
            <el-link v-if="row.url" :href="row.url" target="_blank" type="primary">打开</el-link>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <el-dialog v-model="advancedSettingsVisible" title="采集参数设置" width="980px">
      <el-tabs v-model="advancedSettingsTab">
        <el-tab-pane label="网络配置" name="network">
          <el-form label-width="170px">
            <el-form-item label="信任系统代理">
              <el-switch v-model="networkForm.trustEnv" />
            </el-form-item>
            <el-form-item label="最大重试次数">
              <el-input-number v-model="networkForm.maxRetry" :min="1" :max="5" />
            </el-form-item>
            <el-form-item label="重试退避(ms)">
              <el-input-number v-model="networkForm.retryBackoffMs" :min="0" :max="5000" />
            </el-form-item>
            <el-form-item label="熔断阈值">
              <el-input-number v-model="networkForm.circuitBreakerThreshold" :min="1" :max="50" />
            </el-form-item>
            <el-form-item label="熔断秒数">
              <el-input-number v-model="networkForm.circuitBreakerSeconds" :min="1" :max="600" />
            </el-form-item>
            <el-form-item label="来源超时配置(JSON)">
              <el-input
                v-model="networkForm.sourceTimeoutJson"
                type="textarea"
                :rows="7"
                placeholder='{"default":1.2,"500w":1.8}'
              />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="来源规则" name="source-rules">
          <el-form label-width="170px">
            <el-form-item label="tty黑名单路径">
              <el-input
                v-model="sourceRuleForm.ttyBlacklistText"
                placeholder="/news/-1, /news/75"
              />
            </el-form-item>
            <el-form-item label="tty降权路径(JSON)">
              <el-input
                v-model="sourceRuleForm.ttySoftPenaltyJson"
                type="textarea"
                :rows="6"
                placeholder='{"\/news\/3":1.2}'
              />
            </el-form-item>
            <el-form-item label="仅允许数字详情页">
              <el-switch v-model="sourceRuleForm.ttyRequireNumericDetail" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="质量阈值" name="quality">
          <el-form label-width="170px">
            <el-form-item label="标题最小长度">
              <el-input-number v-model="qualityForm.minTitleLen" :min="2" :max="40" />
            </el-form-item>
            <el-form-item label="最少命中词数">
              <el-input-number v-model="qualityForm.minContextHits" :min="1" :max="5" />
            </el-form-item>
            <el-form-item label="预测正文最小长度">
              <el-input-number v-model="qualityForm.minExcerptPrediction" :min="20" :max="500" />
            </el-form-item>
            <el-form-item label="场外正文最小长度">
              <el-input-number v-model="qualityForm.minExcerptOffField" :min="40" :max="800" />
            </el-form-item>
            <el-form-item label="微博正文最小长度">
              <el-input-number v-model="qualityForm.minExcerptWeibo" :min="10" :max="300" />
            </el-form-item>
            <el-form-item label="来源最低分(JSON)">
              <el-input
                v-model="qualityForm.minScoreJson"
                type="textarea"
                :rows="8"
                placeholder='{"500w":1.6,"default":1.8}'
              />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="别名词典" name="alias">
          <el-form label-width="170px">
            <el-form-item label="联赛别名(JSON)">
              <el-input
                v-model="aliasForm.leagueAliasJson"
                type="textarea"
                :rows="8"
                placeholder='{"英超":["EPL","Premier League"]}'
              />
            </el-form-item>
            <el-form-item label="球队别名(JSON)">
              <el-input
                v-model="aliasForm.teamAliasJson"
                type="textarea"
                :rows="8"
                placeholder='{"曼联":["Man Utd","Manchester United"]}'
              />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="来源健康" name="source-health">
          <el-table :data="sourceHealthRows" stripe max-height="360">
            <el-table-column prop="source" label="来源" width="120" />
            <el-table-column prop="total_items" label="条目数" width="100" />
            <el-table-column prop="accepted_rate" label="采纳率" width="100" />
            <el-table-column prop="blocked_rate" label="拦截率" width="100" />
            <el-table-column prop="avg_quality_score" label="平均质量分" width="120" />
            <el-table-column prop="avg_confidence" label="平均置信度" width="120" />
            <el-table-column prop="latest_crawled_at" label="最新采集时间" min-width="180" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button @click="advancedSettingsVisible = false">关闭</el-button>
        <el-button :loading="loading.loadAdvancedSettings" @click="loadAdvancedSettings">刷新</el-button>
        <el-button type="primary" :loading="loading.saveAdvancedSettings" @click="saveAdvancedSettings">
          保存全部
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import {
  getAliasDictionary,
  cancelCollectionTask,
  createCollectionTask,
  createCollectionSchedule,
  createDingTalkBinding,
  createPushTask,
  debugReplay,
  debugMatchCandidates,
  openCollectionTaskEventsStream,
  getCollectionSources,
  getCollectionTask,
  getCollectionTaskFailureSummary,
  getCollectionTaskSubtasks,
  getCollectionTaskLogs,
  getCollectionTasks,
  getDingTalkBindings,
  getJczqMatches,
  getMatchCollectionItems,
  getNetworkSettings,
  getPushPreview,
  getQualityThresholds,
  getSourceHealth,
  getSourceRules,
  getTimeWindowSettings,
  retryCollectionTask,
  testDingTalkBinding,
  updateAliasDictionary,
  updateNetworkSettings,
  updateQualityThresholds,
  updateSourceRules,
  updateDingTalkBinding,
  updateTimeWindowSettings
} from '@/api/intelligenceCollection'

const loading = reactive({
  matches: false,
  createTask: false,
  tasks: false,
  items: false,
  saveTimeWindow: false,
  debugCandidates: false,
  debugReplay: false,
  saveAdvancedSettings: false,
  loadAdvancedSettings: false,
  saveBinding: false,
  testBinding: false,
  push: false,
  taskFailureSummary: false
})

const query = reactive({
  date: new Date().toISOString().slice(0, 10),
  search: ''
})

const taskQuery = reactive({
  status: ''
})

const sourceOptions = ref([])
const intelTypeOptions = [
  { label: '伤病', value: 'injury' },
  { label: '天气', value: 'weather' },
  { label: '战意', value: 'motivation' },
  { label: '战术', value: 'tactics' },
  { label: '主裁判', value: 'referee' },
  { label: '主帅', value: 'coach' },
  { label: '历史交锋', value: 'history' },
  { label: '胜平负预测', value: 'win_draw_lose' },
  { label: '让球胜平负预测', value: 'handicap_1x2' }
]

const taskForm = reactive({
  mode: 'immediate',
  sources: ['500w', 'ttyingqiu', 'tencent'],
  intelTypes: ['injury', 'weather', 'motivation', 'win_draw_lose', 'handicap_1x2'],
  offsetHours: [24, 12, 6, 1]
})

const timeWindowForm = reactive({
  beforeHours: 240,
  afterHours: 12,
  strictMode: true
})
const timeWindowMeta = reactive({
  boundsLabel: '-240h ~ +12h',
  sourceBefore: 'default',
  sourceAfter: 'default',
  sourceStrict: 'default'
})
const debugForm = reactive({
  source: '500w',
  intelType: 'win_draw_lose',
  maxCandidates: 20
})
const advancedSettingsVisible = ref(false)
const advancedSettingsTab = ref('network')
const networkForm = reactive({
  trustEnv: false,
  maxRetry: 2,
  retryBackoffMs: 120,
  circuitBreakerThreshold: 6,
  circuitBreakerSeconds: 45,
  sourceTimeoutJson: '{\n  "default": 2.5,\n  "500w": 2.8,\n  "ttyingqiu": 3.5,\n  "tencent": 2.8,\n  "weibo": 2.8,\n  "sina": 2.8\n}'
})
const sourceRuleForm = reactive({
  ttyBlacklistText: '/news/-1, /news/75',
  ttySoftPenaltyJson: '{\n  "/news/3": 1.2,\n  "/news/6009": 1.2\n}',
  ttyRequireNumericDetail: true
})
const qualityForm = reactive({
  minTitleLen: 6,
  minContextHits: 1,
  minExcerptPrediction: 80,
  minExcerptOffField: 120,
  minExcerptWeibo: 40,
  minScoreJson: '{\n  "500w": 1.6,\n  "sina": 1.5,\n  "tencent": 1.6,\n  "weibo": 1.4,\n  "ttyingqiu": 1.8,\n  "default": 1.8\n}'
})
const aliasForm = reactive({
  leagueAliasJson: '{}',
  teamAliasJson: '{}'
})
const sourceHealthRows = ref([])

const matches = ref([])
const selectedMatchIds = ref([])
const tasks = ref([])
const items = ref([])
const preview = ref(null)
const activeMatchId = ref(null)

const taskLogs = ref([])
const logDialogVisible = ref(false)
const taskDetailDialogVisible = ref(false)
const taskDetailLoading = ref(false)
const taskDetail = ref(null)
const taskSubtasks = ref([])
const taskSubtasksLoading = ref(false)
const taskFailureSummary = ref(null)
const itemDialogVisible = ref(false)
const itemDetail = ref(null)
const activeItemRow = ref(null)
const activeItemParsed = ref(null)
const onlyMatchesWithItems = ref(false)
const indexingMatches = ref(false)
const matchesWithItems = ref(new Set())

const dingtalkForm = reactive({
  webhook: '',
  secret: ''
})
const currentBindingId = ref(null)
const retryingTaskMap = ref({})
const itemStats = reactive({
  article: 0,
  fallback: 0,
  sourceView: 0,
  highQuality: 0,
  aiEnhanced: 0
})
const activeResultCategory = ref('')
const resultCache = ref(new Map())
const debugDialogVisible = ref(false)
const debugResult = ref(null)
const debugCandidates = ref([])
const taskTracker = reactive({
  visible: false,
  taskId: null,
  status: 'idle',
  message: '',
  action: '',
  matchId: null
})

const emptyResultDescription = computed(() => {
  if (!activeMatchId.value) return '请先在左侧赛程表选择一场比赛'
  if (taskTracker.visible && (taskTracker.status === 'running' || taskTracker.status === 'pending')) {
    return `任务 ${taskTracker.taskId || '-'} 正在执行，结果将在完成后自动刷新`
  }
  if (taskTracker.visible && taskTracker.status === 'partial') {
    return `任务 ${taskTracker.taskId || '-'} 部分成功，可先查看已采集结果`
  }
  if (taskTracker.visible && taskTracker.status === 'failed') {
    return `任务 ${taskTracker.taskId || '-'} 执行失败，请先查看任务日志`
  }
  if (taskTracker.visible && taskTracker.status === 'success') {
    return '任务已完成，但当前比赛暂无命中内容'
  }
  return '当前比赛暂无采集结果，请先创建/执行采集任务'
})

const parseJsonSafe = (raw, fallback) => {
  try {
    const parsed = JSON.parse(raw)
    return parsed && typeof parsed === 'object' ? parsed : fallback
  } catch (_) {
    return fallback
  }
}

const statusLabelMap = {
  pending: '待执行',
  running: '执行中',
  success: '执行成功',
  partial: '部分成功',
  failed: '执行失败',
  cancelled: '已取消',
  unknown: '状态未知'
}
const RESULT_CACHE_TTL_MS = 2 * 60 * 1000

const formatCoverage = (coverageRate) => {
  const value = Number(coverageRate || 0)
  return `${(value * 100).toFixed(1)}%`
}

const formatPercent = (value) => {
  const num = Number(value || 0)
  return `${(num * 100).toFixed(1)}%`
}

const formatTopReasons = (rows = []) => {
  if (!Array.isArray(rows) || !rows.length) return '-'
  return rows
    .slice(0, 3)
    .map((x) => `${x.reason} x${x.count}`)
    .join('；')
}

const formatMatchProgress = (rows) => {
  if (!Array.isArray(rows) || !rows.length) return '-'
  return rows
    .slice(0, 6)
    .map((x) => `#${x.match_id}:${x.item_count}/${x.expected_count}`)
    .join(' | ')
}

const displayedMatches = computed(() => {
  if (!onlyMatchesWithItems.value) return matches.value
  return matches.value.filter((x) => matchesWithItems.value.has(x.id))
})

const logTypeToTag = (level) => {
  if (level === 'success') return 'success'
  if (level === 'warning') return 'warning'
  if (level === 'error') return 'danger'
  return 'info'
}

const loadSources = async () => {
  const list = await getCollectionSources()
  sourceOptions.value = list || []
  const codes = sourceOptions.value.map((x) => x.code)
  if (!codes.includes(debugForm.source)) {
    debugForm.source = codes[0] || '500w'
  }
}

const loadTimeWindowConfig = async () => {
  try {
    const settings = await getTimeWindowSettings()
    timeWindowForm.beforeHours = Number(settings?.before_hours ?? 240)
    timeWindowForm.afterHours = Number(settings?.after_hours ?? 12)
    timeWindowForm.strictMode = settings?.strict_mode !== false
    timeWindowMeta.boundsLabel = settings?.bounds_label || `-${timeWindowForm.beforeHours}h ~ +${timeWindowForm.afterHours}h`
    timeWindowMeta.sourceBefore = settings?.source?.before || 'default'
    timeWindowMeta.sourceAfter = settings?.source?.after || 'default'
    timeWindowMeta.sourceStrict = settings?.source?.strict || 'default'
  } catch (e) {
    console.error(e)
    ElMessage.warning('加载时间窗配置失败，已使用默认值')
  }
}

const saveTimeWindowConfig = async () => {
  loading.saveTimeWindow = true
  try {
    const payload = {
      before_hours: Number(timeWindowForm.beforeHours || 240),
      after_hours: Number(timeWindowForm.afterHours || 12),
      strict_mode: !!timeWindowForm.strictMode
    }
    const settings = await updateTimeWindowSettings(payload)
    timeWindowForm.beforeHours = Number(settings?.before_hours ?? payload.before_hours)
    timeWindowForm.afterHours = Number(settings?.after_hours ?? payload.after_hours)
    timeWindowForm.strictMode = settings?.strict_mode !== false
    timeWindowMeta.boundsLabel = settings?.bounds_label || `-${timeWindowForm.beforeHours}h ~ +${timeWindowForm.afterHours}h`
    timeWindowMeta.sourceBefore = settings?.source?.before || 'db'
    timeWindowMeta.sourceAfter = settings?.source?.after || 'db'
    timeWindowMeta.sourceStrict = settings?.source?.strict || 'db'
    ElMessage.success('时间窗阈值已保存并即时生效')
  } catch (e) {
    console.error(e)
    ElMessage.error('保存时间窗阈值失败')
  } finally {
    loading.saveTimeWindow = false
  }
}

const loadAdvancedSettings = async () => {
  loading.loadAdvancedSettings = true
  try {
    const [network, sourceRules, qualityThresholds, aliasDictionary, sourceHealth] = await Promise.all([
      getNetworkSettings(),
      getSourceRules(),
      getQualityThresholds(),
      getAliasDictionary(),
      getSourceHealth({ days: 7 })
    ])

    networkForm.trustEnv = !!network?.trust_env
    networkForm.maxRetry = Number(network?.max_retry ?? 2)
    networkForm.retryBackoffMs = Number(network?.retry_backoff_ms ?? 120)
    networkForm.circuitBreakerThreshold = Number(network?.circuit_breaker_threshold ?? 6)
    networkForm.circuitBreakerSeconds = Number(network?.circuit_breaker_seconds ?? 45)
    networkForm.sourceTimeoutJson = JSON.stringify(network?.source_timeout_seconds || {}, null, 2)

    const ttyRules = sourceRules?.rules?.ttyingqiu || {}
    sourceRuleForm.ttyBlacklistText = (ttyRules?.blacklist_exact_paths || []).join(', ')
    sourceRuleForm.ttySoftPenaltyJson = JSON.stringify(ttyRules?.soft_penalty_paths || {}, null, 2)
    sourceRuleForm.ttyRequireNumericDetail = ttyRules?.require_numeric_news_detail !== false

    const thresholds = qualityThresholds?.thresholds || {}
    qualityForm.minTitleLen = Number(thresholds?.min_title_len ?? 6)
    qualityForm.minContextHits = Number(thresholds?.min_context_hits ?? 1)
    qualityForm.minExcerptPrediction = Number(thresholds?.min_excerpt_len?.prediction ?? 80)
    qualityForm.minExcerptOffField = Number(thresholds?.min_excerpt_len?.off_field ?? 120)
    qualityForm.minExcerptWeibo = Number(thresholds?.min_excerpt_len?.weibo ?? 40)
    qualityForm.minScoreJson = JSON.stringify(thresholds?.min_match_score_by_source || {}, null, 2)

    aliasForm.leagueAliasJson = JSON.stringify(aliasDictionary?.dictionary?.league || {}, null, 2)
    aliasForm.teamAliasJson = JSON.stringify(aliasDictionary?.dictionary?.team || {}, null, 2)

    sourceHealthRows.value = Array.isArray(sourceHealth?.items) ? sourceHealth.items : []
  } catch (e) {
    console.error(e)
    ElMessage.warning('加载高级配置失败')
  } finally {
    loading.loadAdvancedSettings = false
  }
}

const saveAdvancedSettings = async () => {
  loading.saveAdvancedSettings = true
  try {
    const sourceTimeoutMap = parseJsonSafe(networkForm.sourceTimeoutJson, {})
    const ttySoftPenalty = parseJsonSafe(sourceRuleForm.ttySoftPenaltyJson, {})
    const minScoreMap = parseJsonSafe(qualityForm.minScoreJson, {})
    const leagueAliasMap = parseJsonSafe(aliasForm.leagueAliasJson, {})
    const teamAliasMap = parseJsonSafe(aliasForm.teamAliasJson, {})
    const ttyBlacklist = sourceRuleForm.ttyBlacklistText
      .split(',')
      .map((x) => x.trim())
      .filter(Boolean)

    await Promise.all([
      updateNetworkSettings({
        trust_env: !!networkForm.trustEnv,
        max_retry: Number(networkForm.maxRetry || 2),
        retry_backoff_ms: Number(networkForm.retryBackoffMs || 120),
        circuit_breaker_threshold: Number(networkForm.circuitBreakerThreshold || 6),
        circuit_breaker_seconds: Number(networkForm.circuitBreakerSeconds || 45),
        source_timeout_seconds: sourceTimeoutMap
      }),
      updateSourceRules({
        rules: {
          ttyingqiu: {
            blacklist_exact_paths: ttyBlacklist,
            soft_penalty_paths: ttySoftPenalty,
            require_numeric_news_detail: !!sourceRuleForm.ttyRequireNumericDetail
          }
        }
      }),
      updateQualityThresholds({
        thresholds: {
          min_title_len: Number(qualityForm.minTitleLen || 6),
          min_context_hits: Number(qualityForm.minContextHits || 1),
          min_excerpt_len: {
            prediction: Number(qualityForm.minExcerptPrediction || 80),
            off_field: Number(qualityForm.minExcerptOffField || 120),
            weibo: Number(qualityForm.minExcerptWeibo || 40)
          },
          min_match_score_by_source: minScoreMap
        }
      }),
      updateAliasDictionary({
        dictionary: {
          league: leagueAliasMap,
          team: teamAliasMap
        }
      })
    ])
    ElMessage.success('高级配置已保存并即时生效')
    await loadAdvancedSettings()
  } catch (e) {
    console.error(e)
    ElMessage.error('保存高级配置失败，请检查 JSON 格式')
  } finally {
    loading.saveAdvancedSettings = false
  }
}

const openAdvancedSettings = async () => {
  advancedSettingsVisible.value = true
  await loadAdvancedSettings()
}

const loadMatches = async () => {
  loading.matches = true
  try {
    const searchKeyword = (query.search || '').trim()
    const result = await getJczqMatches({
      page: 1,
      size: 100,
      search: searchKeyword,
      date_from: query.date,
      date_to: query.date
    })
    matches.value = result.items || []
    matchesWithItems.value = new Set()
    if (onlyMatchesWithItems.value && matches.value.length) {
      await buildMatchesWithItemsIndex()
    }
    if (searchKeyword) {
      ElMessage.info(`已按关键词“${searchKeyword}”筛选，当前命中 ${matches.value.length} 场`)
    }
  } catch (e) {
    console.error(e)
    ElMessage.error('加载赛程失败')
  } finally {
    loading.matches = false
  }
}

const clearKeywordAndReload = async () => {
  query.search = ''
  await loadMatches()
}

const onMatchSelectionChange = (rows) => {
  selectedMatchIds.value = rows.map((x) => x.id)
}

const onSelectMatch = (row) => {
  activeMatchId.value = row.id
  loadResult('')
}

const getResultCacheKey = (matchId, category) => `${matchId}:${category || 'all'}`

const getCachedResult = (matchId, category) => {
  const key = getResultCacheKey(matchId, category)
  const hit = resultCache.value.get(key)
  if (!hit) return null
  if (Date.now() - hit.ts > RESULT_CACHE_TTL_MS) {
    resultCache.value.delete(key)
    return null
  }
  return hit.data
}

const setCachedResult = (matchId, category, data) => {
  const key = getResultCacheKey(matchId, category)
  resultCache.value.set(key, { ts: Date.now(), data })
}

const clearMatchResultCache = (matchId) => {
  if (!matchId) return
  const next = new Map()
  resultCache.value.forEach((value, key) => {
    if (!key.startsWith(`${matchId}:`)) next.set(key, value)
  })
  resultCache.value = next
}

const buildMatchesWithItemsIndex = async () => {
  if (!onlyMatchesWithItems.value) return
  const targetMatches = [...matches.value]
  if (!targetMatches.length) {
    matchesWithItems.value = new Set()
    return
  }

  indexingMatches.value = true
  const idSet = new Set()
  const batchSize = 8
  try {
    for (let i = 0; i < targetMatches.length; i += batchSize) {
      const batch = targetMatches.slice(i, i + batchSize)
      const checks = batch.map(async (m) => {
        try {
          const res = await getMatchCollectionItems(m.id, { limit: 1 })
          const total = Number(res?.total || 0)
          const len = Array.isArray(res?.items) ? res.items.length : 0
          if (total > 0 || len > 0) idSet.add(m.id)
        } catch (e) {
          // Ignore single-match query failures, avoid blocking entire filter.
        }
      })
      await Promise.all(checks)
    }
    matchesWithItems.value = idSet
    ElMessage.success(`已筛出 ${idSet.size} 场有采集结果的比赛`)
  } finally {
    indexingMatches.value = false
  }
}

watch(onlyMatchesWithItems, async (enabled) => {
  if (!enabled) return
  await buildMatchesWithItemsIndex()
})

const updateTaskTracker = ({ taskId, status, action, matchId, detail }) => {
  const statusLabel = statusLabelMap[status] || statusLabelMap.unknown
  const actionLabel = action === 'retry' ? '重试任务' : '创建任务'
  const progress = detail ? `（${detail.success_count || 0}/${detail.total_count || 0}）` : ''
  taskTracker.visible = true
  taskTracker.taskId = taskId
  taskTracker.status = status || 'unknown'
  taskTracker.action = action
  taskTracker.matchId = matchId || taskTracker.matchId
  taskTracker.message = `${actionLabel} #${taskId || '-'}：${statusLabel}${progress}`
}

const submitTask = async () => {
  if (!selectedMatchIds.value.length) {
    ElMessage.warning('请先选择至少一场比赛')
    return
  }
  if (!taskForm.sources.length || !taskForm.intelTypes.length) {
    ElMessage.warning('请完善来源和情报类型')
    return
  }

  loading.createTask = true
  try {
    const preferredMatchId = activeMatchId.value || selectedMatchIds.value[0] || null
    const payload = {
      match_ids: selectedMatchIds.value,
      sources: taskForm.sources,
      intel_types: taskForm.intelTypes,
      mode: taskForm.mode,
      offset_hours: taskForm.mode === 'scheduled' ? taskForm.offsetHours : []
    }
    if (taskForm.mode === 'scheduled') {
      await createCollectionSchedule(payload)
      ElMessage.success('计划任务创建成功')
    } else {
      const createdTask = await createCollectionTask(payload, { timeout: 180000 })
      const createdTaskId = createdTask?.id
      if (createdTaskId) {
        updateTaskTracker({
          taskId: createdTaskId,
          status: createdTask?.status || 'running',
          action: 'create',
          matchId: preferredMatchId,
          detail: createdTask
        })
        ElMessage.info(`任务 ${createdTaskId} 已提交，系统正在跟踪执行状态`)
        await trackTaskUntilStable(createdTaskId, { action: 'create', matchId: preferredMatchId })
      } else {
        ElMessage.success('即时任务已提交，后台执行中')
      }
    }
    await loadTasks()
    if (preferredMatchId) {
      activeMatchId.value = preferredMatchId
      clearMatchResultCache(preferredMatchId)
      await loadResult('', { force: true })
    }
  } catch (e) {
    console.error(e)
    const msg = String(e?.message || '')
    if (e?.code === 'ECONNABORTED' || msg.includes('timeout')) {
      ElMessage.warning('创建请求超时，任务可能仍在后台执行，请稍后刷新任务列表确认状态')
      await loadTasks()
      return
    }
    ElMessage.error('任务创建失败')
  } finally {
    loading.createTask = false
  }
}

const loadTasks = async (options = {}) => {
  const silent = !!options.silent
  const timeout = options.timeout || 60000
  loading.tasks = true
  try {
    const result = await getCollectionTasks({
      page: 1,
      size: 100,
      status: taskQuery.status || undefined
    }, {
      timeout,
      silentError: silent
    })
    tasks.value = result.items || []
  } catch (e) {
    console.error(e)
    const msg = String(e?.message || '')
    if (e?.code === 'ECONNABORTED' || msg.includes('timeout')) {
      if (!silent) ElMessage.warning('加载任务超时，请稍后重试')
      return
    }
    if (!silent) ElMessage.error('加载任务失败')
  } finally {
    loading.tasks = false
  }
}

const openTaskLogs = async (row) => {
  try {
    const result = await getCollectionTaskLogs(row.id, {
      decision: ''
    })
    taskLogs.value = result.logs || []
    logDialogVisible.value = true
  } catch (e) {
    console.error(e)
    ElMessage.error('加载任务日志失败')
  }
}

const openTaskDetail = async (row) => {
  taskDetailDialogVisible.value = true
  taskDetailLoading.value = true
  taskSubtasksLoading.value = true
  loading.taskFailureSummary = true
  taskDetail.value = { ...row }
  taskSubtasks.value = []
  taskFailureSummary.value = null
  try {
    const [detail, subtasksResp, failureSummary] = await Promise.all([
      getCollectionTask(row.id, { timeout: 60000 }),
      getCollectionTaskSubtasks(row.id, {}, { timeout: 60000 }),
      getCollectionTaskFailureSummary(row.id, { timeout: 60000 }).catch(() => null)
    ])
    taskDetail.value = detail || { ...row }
    taskSubtasks.value = subtasksResp?.items || []
    taskFailureSummary.value = failureSummary || null
  } catch (e) {
    ElMessage.warning('加载任务详情失败，已展示列表快照')
    taskDetail.value = { ...row }
    taskSubtasks.value = []
    taskFailureSummary.value = null
  } finally {
    taskDetailLoading.value = false
    taskSubtasksLoading.value = false
    loading.taskFailureSummary = false
  }
}

const loadTaskFailureSummary = async (taskId) => {
  if (!taskId) return
  loading.taskFailureSummary = true
  try {
    taskFailureSummary.value = await getCollectionTaskFailureSummary(taskId, { timeout: 60000 })
  } catch (e) {
    console.error(e)
    ElMessage.warning('加载失败摘要失败')
  } finally {
    loading.taskFailureSummary = false
  }
}

const retryTask = async (row) => {
  if (isTaskRetrying(row.id)) return
  retryingTaskMap.value = { ...retryingTaskMap.value, [row.id]: true }
  ElMessage.info(`任务 ${row.id} 重试请求已提交，正在确认状态...`)
  try {
    await retryCollectionTask(row.id, { timeout: 180000 })
    const finalStatus = await trackTaskUntilStable(row.id, {
      action: 'retry',
      matchId: activeMatchId.value || row?.match_ids?.[0] || null
    })
    if (finalStatus === 'success') {
      ElMessage.success(`任务 ${row.id} 重试完成`)
      if (activeMatchId.value || row?.match_ids?.[0]) {
        activeMatchId.value = activeMatchId.value || row.match_ids[0]
        clearMatchResultCache(activeMatchId.value)
        await loadResult('', { force: true })
      }
    } else if (finalStatus === 'partial') {
      ElMessage.warning(`任务 ${row.id} 部分成功，请查看失败摘要定位问题`)
      if (activeMatchId.value || row?.match_ids?.[0]) {
        activeMatchId.value = activeMatchId.value || row.match_ids[0]
        clearMatchResultCache(activeMatchId.value)
        await loadResult('', { force: true })
      }
    } else if (finalStatus === 'failed') {
      ElMessage.warning(`任务 ${row.id} 重试失败，请查看日志`)
    } else if (finalStatus === 'running' || finalStatus === 'pending') {
      ElMessage.info(`任务 ${row.id} 已进入 ${finalStatus}，请稍后查看结果`)
    } else {
      ElMessage.success('任务重试已触发')
    }
    await loadTasks({ silent: true, timeout: 20000 })
  } catch (e) {
    console.error(e)
    const msg = String(e?.message || '')
    if (e?.code === 'ECONNABORTED' || msg.includes('timeout')) {
      ElMessage.warning('重试请求超时，任务可能仍在后台执行，请稍后刷新任务列表确认状态')
      await loadTasks({ silent: true, timeout: 20000 })
      return
    }
    ElMessage.error('任务重试失败')
  } finally {
    const next = { ...retryingTaskMap.value }
    delete next[row.id]
    retryingTaskMap.value = next
  }
}

const isTaskRetrying = (taskId) => !!retryingTaskMap.value[taskId]

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const parseTaskSseChunk = (rawChunk) => {
  const lines = String(rawChunk || '')
    .split('\n')
    .map((line) => line.trimEnd())
  let event = 'message'
  const dataRows = []
  for (const line of lines) {
    if (!line || line.startsWith(':')) continue
    if (line.startsWith('event:')) {
      event = line.slice(6).trim() || 'message'
      continue
    }
    if (line.startsWith('data:')) {
      dataRows.push(line.slice(5).trim())
    }
  }
  if (!dataRows.length) return null
  const dataText = dataRows.join('\n')
  let data = null
  try {
    data = JSON.parse(dataText)
  } catch (e) {
    data = null
  }
  return { event, data }
}

const trackTaskViaSse = async (taskId, options = {}) => {
  const action = options.action || 'create'
  const matchId = options.matchId || null
  const terminal = new Set(['success', 'partial', 'failed', 'cancelled'])
  const controller = new AbortController()

  try {
    const response = await openCollectionTaskEventsStream(taskId, {
      intervalMs: 2500,
      maxDurationSeconds: 120,
      signal: controller.signal
    })
    if (!response?.ok || !response.body) {
      return ''
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''
    let latestStatus = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const chunks = buffer.split('\n\n')
      buffer = chunks.pop() || ''

      for (const chunk of chunks) {
        const parsed = parseTaskSseChunk(chunk)
        if (!parsed) continue
        if (parsed.event === 'timeout') {
          return ''
        }
        if (parsed.event === 'error') {
          return ''
        }
        if (parsed.event !== 'progress') {
          continue
        }
        const detail = parsed.data || {}
        const status = detail.status || latestStatus
        latestStatus = status || latestStatus
        updateTaskTracker({ taskId, status: latestStatus || 'running', action, matchId, detail })
        if (latestStatus && terminal.has(latestStatus)) {
          await loadTasks({ silent: true, timeout: 20000 })
          if ((latestStatus === 'success' || latestStatus === 'partial') && matchId) {
            activeMatchId.value = matchId
            clearMatchResultCache(matchId)
            await loadResult('', { force: true })
          }
          return latestStatus
        }
      }
    }

    return latestStatus && terminal.has(latestStatus) ? latestStatus : ''
  } catch (e) {
    const msg = String(e?.message || '')
    if (!msg.includes('aborted')) {
      console.warn('SSE 任务跟踪失败，降级为轮询模式', e)
    }
    return ''
  } finally {
    controller.abort()
  }
}

const trackTaskUntilStable = async (taskId, options = {}) => {
  const action = options.action || 'create'
  const matchId = options.matchId || null
  const terminal = new Set(['success', 'partial', 'failed', 'cancelled'])
  const sseStatus = await trackTaskViaSse(taskId, options)
  if (sseStatus) {
    return sseStatus
  }
  const maxRounds = 24
  for (let i = 0; i < maxRounds; i += 1) {
    try {
      const detail = await getCollectionTask(taskId, {
        timeout: 15000,
        lightweight: true,
        silentError: true
      })
      const status = detail?.status
      updateTaskTracker({ taskId, status, action, matchId, detail })
      if (status && terminal.has(status)) {
        await loadTasks({ silent: true, timeout: 20000 })
        if ((status === 'success' || status === 'partial') && matchId) {
          activeMatchId.value = matchId
          clearMatchResultCache(matchId)
          await loadResult('', { force: true })
        }
        return status
      }
      if (i === maxRounds - 1) {
        await loadTasks({ silent: true, timeout: 20000 })
        return status || ''
      }
    } catch (e) {
      const msg = String(e?.message || '')
      updateTaskTracker({ taskId, status: 'unknown', action, matchId })
      if (!(e?.code === 'ECONNABORTED' || msg.includes('timeout'))) {
        console.warn('轮询任务状态失败', e)
      }
      if (i === maxRounds - 1) {
        await loadTasks({ silent: true, timeout: 20000 })
        return ''
      }
    }
    const waitMs = i <= 0 ? 2500 : i === 1 ? 4000 : 6000
    await sleep(waitMs)
  }
  return ''
}

const cancelTask = async (row) => {
  await cancelCollectionTask(row.id)
  ElMessage.success('任务已取消')
  loadTasks()
}

const applyResultItems = (rows) => {
  items.value = rows || []
  itemStats.article = items.value.filter((x) => x.__parsed?.qualityStatus === 'accepted').length
  itemStats.fallback = items.value.filter((x) => x.__parsed?.qualityStatus === 'blocked').length
  itemStats.sourceView = items.value.filter((x) => x.__parsed?.qualityStatus === 'source_view').length
  itemStats.highQuality = items.value.filter((x) => Number(x.__parsed?.qualityScore || 0) >= 1.8).length
  itemStats.aiEnhanced = items.value.filter((x) => x.__parsed?.aiEnhanced).length
  if (items.value.length) {
    setActiveItem(items.value[0])
  } else {
    activeItemRow.value = null
    activeItemParsed.value = null
  }
}

const loadResult = async (category, options = {}) => {
  if (!activeMatchId.value) return
  const normalizedCategory = category || ''
  activeResultCategory.value = normalizedCategory
  const force = !!options.force

  if (!force) {
    const cached = getCachedResult(activeMatchId.value, normalizedCategory)
    if (cached) {
      applyResultItems(cached)
      return
    }
  }

  loading.items = true
  try {
    const result = await getMatchCollectionItems(activeMatchId.value, {
      category: normalizedCategory || undefined
    })
    const normalizedItems = (result.items || []).map((row) => {
      const parsed = resolveItemDetail(row)
      return { ...row, __parsed: parsed }
    })
    setCachedResult(activeMatchId.value, normalizedCategory, normalizedItems)
    applyResultItems(normalizedItems)
  } catch (e) {
    console.error(e)
    ElMessage.error('加载结果失败')
  } finally {
    loading.items = false
  }
}

const resolveItemDetail = (row) => {
  const raw = row?.content_raw || ''
  const rowHitTerms = Array.isArray(row?.match_hit_terms) ? row.match_hit_terms : []
  const rowQualityScore = row?.quality_score
  const rowQualityPassReason = row?.quality_pass_reason
  const rowQualityBlockReason = row?.quality_block_reason
  const rowSourceParser = row?.source_parser
  const rowQualityStatus = row?.quality_status
  const rowAiEnhanced = row?.ai_enhanced
  const rowAiProvider = row?.ai_provider
  const rowAiModel = row?.ai_model
  const rowAiSummary = row?.ai_summary
  const rowAiViewpoint = row?.ai_viewpoint
  const rowAiRiskLevel = row?.ai_risk_level
  const rowAiConfidence = row?.ai_confidence
  const rowAiReason = row?.ai_reason
  const detail = {
    viewType: '',
    viewTypeLabel: '未知',
    articleUrl: row?.source_url || '',
    title: row?.title || '',
    summary: '',
    matchScore: null,
    fallbackReason: '',
    qualityScore: rowQualityScore ?? null,
    qualityPassReason: rowQualityPassReason || '',
    qualityBlockReason: rowQualityBlockReason || '',
    sourceParser: rowSourceParser || '',
    matchHitTerms: rowHitTerms,
    qualityStatus: rowQualityStatus || '',
    aiEnhanced: !!rowAiEnhanced,
    aiProvider: rowAiProvider || '',
    aiModel: rowAiModel || '',
    aiSummary: rowAiSummary || '',
    aiViewpoint: rowAiViewpoint || '',
    aiRiskLevel: rowAiRiskLevel || '',
    aiConfidence: rowAiConfidence ?? null,
    aiReason: rowAiReason || ''
  }
  if (!raw) return detail

  const typeMatch = raw.match(/^\[([^\]]+)\]/)
  if (typeMatch?.[1]) {
    detail.viewType = typeMatch[1]
    detail.viewTypeLabel =
      typeMatch[1] === 'match-article'
        ? '文章页命中'
        : typeMatch[1] === 'match-article-fallback'
          ? '兜底摘要'
          : typeMatch[1] === 'source-view'
            ? '来源摘要'
            : typeMatch[1]
    if (!detail.qualityStatus) {
      detail.qualityStatus =
        typeMatch[1] === 'match-article'
          ? 'accepted'
          : typeMatch[1] === 'match-article-fallback'
            ? 'blocked'
            : 'source_view'
    }
  }

  const summaryMatch = raw.match(/summary=([^;]+);/)
  if (summaryMatch?.[1]) detail.summary = summaryMatch[1].trim()

  const scoreMatch = raw.match(/match_score=([^;]+);/)
  if (scoreMatch?.[1]) detail.matchScore = scoreMatch[1].trim()
  const qualityScoreMatch = raw.match(/quality_score=([^;]+);/)
  if (qualityScoreMatch?.[1] && detail.qualityScore == null) {
    const parsed = Number(qualityScoreMatch[1].trim())
    detail.qualityScore = Number.isNaN(parsed) ? null : parsed
  }

  const titleMatch = raw.match(/article_title=([^;]+);/)
  if (titleMatch?.[1]) detail.title = titleMatch[1].trim()

  const urlMatch = raw.match(/article_url=([^;]+);/)
  if (urlMatch?.[1]) detail.articleUrl = urlMatch[1].trim()

  const fallbackMatch = raw.match(/fetch_error=\((.*?)\);/)
  if (fallbackMatch?.[1]) detail.fallbackReason = fallbackMatch[1].trim()

  const passReasonMatch = raw.match(/quality_pass_reason=([^;]+);/)
  if (passReasonMatch?.[1] && !detail.qualityPassReason) detail.qualityPassReason = passReasonMatch[1].trim()

  const blockReasonMatch = raw.match(/quality_block_reason=([^;]+);/)
  if (blockReasonMatch?.[1] && !detail.qualityBlockReason) detail.qualityBlockReason = blockReasonMatch[1].trim()

  const parserMatch = raw.match(/source_parser=([^;]+);/)
  if (parserMatch?.[1] && !detail.sourceParser) detail.sourceParser = parserMatch[1].trim()

  const aiEnhancedMatch = raw.match(/ai_enhanced=([^;]+);/)
  if (aiEnhancedMatch?.[1]) detail.aiEnhanced = ['1', 'true', 'True'].includes(aiEnhancedMatch[1].trim())

  const aiProviderMatch = raw.match(/ai_provider=([^;]+);/)
  if (aiProviderMatch?.[1] && !detail.aiProvider) detail.aiProvider = aiProviderMatch[1].trim()

  const aiModelMatch = raw.match(/ai_model=([^;]+);/)
  if (aiModelMatch?.[1] && !detail.aiModel) detail.aiModel = aiModelMatch[1].trim()

  const aiSummaryMatch = raw.match(/ai_summary=([^;]+);/)
  if (aiSummaryMatch?.[1] && !detail.aiSummary) detail.aiSummary = aiSummaryMatch[1].trim()

  const aiViewpointMatch = raw.match(/ai_viewpoint=([^;]+);/)
  if (aiViewpointMatch?.[1] && !detail.aiViewpoint) detail.aiViewpoint = aiViewpointMatch[1].trim()

  const aiRiskMatch = raw.match(/ai_risk_level=([^;]+);/)
  if (aiRiskMatch?.[1] && !detail.aiRiskLevel) detail.aiRiskLevel = aiRiskMatch[1].trim()

  const aiConfidenceMatch = raw.match(/ai_confidence=([^;]+);/)
  if (aiConfidenceMatch?.[1] && detail.aiConfidence == null) {
    const parsed = Number(aiConfidenceMatch[1].trim())
    detail.aiConfidence = Number.isNaN(parsed) ? null : parsed
  }

  const aiReasonMatch = raw.match(/ai_reason=([^;]+);/)
  if (aiReasonMatch?.[1] && !detail.aiReason) detail.aiReason = aiReasonMatch[1].trim()

  const hitTermsMatch = raw.match(/hit_terms=([^;]+);/)
  if (hitTermsMatch?.[1] && (!detail.matchHitTerms || !detail.matchHitTerms.length)) {
    detail.matchHitTerms = hitTermsMatch[1]
      .split(/[|,]/)
      .map((x) => x.trim())
      .filter(Boolean)
  }

  return detail
}

const setActiveItem = (row) => {
  activeItemRow.value = row
  activeItemParsed.value = row?.__parsed || resolveItemDetail(row)
}

const openItemDetail = (row) => {
  const parsed = row?.__parsed || resolveItemDetail(row)
  itemDetail.value = { ...row, ...parsed }
  itemDialogVisible.value = true
  setActiveItem(row)
}

const refreshResult = () => loadResult(activeResultCategory.value, { force: true })

const openCandidateDebug = async () => {
  if (!activeMatchId.value) {
    ElMessage.warning('请先选择比赛再调试候选抓取')
    return
  }
  loading.debugCandidates = true
  try {
    const payload = {
      match_id: activeMatchId.value,
      source: debugForm.source,
      intel_type: debugForm.intelType,
      max_candidates: Number(debugForm.maxCandidates || 20)
    }
    const result = await debugMatchCandidates(payload, { timeout: 90000 })
    debugResult.value = result || {}
    debugCandidates.value = (result?.top_candidates || []).map((x, idx) => ({
      ...x,
      __index: idx + 1,
      __hitTermsText: Array.isArray(x?.hit_terms) ? x.hit_terms.join(' / ') : '',
      __timePassLabel:
        x?.time_window_pass === true ? '通过' : x?.time_window_pass === false ? '拦截' : '-'
    }))
    debugDialogVisible.value = true
  } catch (e) {
    console.error(e)
    ElMessage.error('候选调试失败')
  } finally {
    loading.debugCandidates = false
  }
}

const openReplayDebug = async () => {
  if (!activeMatchId.value) {
    ElMessage.warning('请先选择比赛再执行回放调试')
    return
  }
  loading.debugReplay = true
  try {
    const payload = {
      match_id: activeMatchId.value,
      source: debugForm.source,
      intel_type: debugForm.intelType,
      max_candidates: Number(debugForm.maxCandidates || 20)
    }
    const replay = await debugReplay(payload, { timeout: 90000 })
    const result = replay?.result || replay || {}
    debugResult.value = result
    debugCandidates.value = (result?.top_candidates || []).map((x, idx) => ({
      ...x,
      __index: idx + 1,
      __hitTermsText: Array.isArray(x?.hit_terms) ? x.hit_terms.join(' / ') : '',
      __timePassLabel:
        x?.time_window_pass === true ? '通过' : x?.time_window_pass === false ? '拦截' : '-'
    }))
    debugDialogVisible.value = true
  } catch (e) {
    console.error(e)
    ElMessage.error('回放调试失败')
  } finally {
    loading.debugReplay = false
  }
}

const buildPreview = async () => {
  if (!activeMatchId.value) return
  try {
    const result = await getPushPreview(activeMatchId.value, {
      user_risk_profile: 'balanced',
      max_evidence: 3
    })
    preview.value = result
    ElMessage.success('已生成推送预览卡')
  } catch (e) {
    console.error(e)
    ElMessage.error('生成推送预览失败')
  }
}

const loadBindings = async () => {
  const bindings = await getDingTalkBindings()
  if (bindings?.length) {
    const first = bindings[0]
    currentBindingId.value = first.id
    dingtalkForm.webhook = first.webhook || ''
    dingtalkForm.secret = first.secret || ''
  }
}

const saveBinding = async () => {
  if (!dingtalkForm.webhook) {
    ElMessage.warning('请先填写 webhook')
    return
  }
  loading.saveBinding = true
  try {
    if (currentBindingId.value) {
      await updateDingTalkBinding(currentBindingId.value, { ...dingtalkForm, enabled: true })
    } else {
      const result = await createDingTalkBinding({ ...dingtalkForm, enabled: true })
      currentBindingId.value = result.id
    }
    ElMessage.success('钉钉绑定已保存')
  } catch (e) {
    console.error(e)
    ElMessage.error('保存钉钉绑定失败')
  } finally {
    loading.saveBinding = false
  }
}

const testBinding = async () => {
  if (!currentBindingId.value) return
  loading.testBinding = true
  try {
    await testDingTalkBinding(currentBindingId.value)
    ElMessage.success('测试发送成功')
  } catch (e) {
    console.error(e)
    ElMessage.error('测试发送失败')
  } finally {
    loading.testBinding = false
  }
}

const pushPreview = async () => {
  if (!activeMatchId.value || !preview.value) return
  loading.push = true
  try {
    const result = await createPushTask({
      match_id: activeMatchId.value,
      channel: 'dingtalk',
      target_users: [],
      binding_id: currentBindingId.value,
      preview: preview.value
    })
    ElMessage.success(`推送任务已提交（状态：${result.status}）`)
  } catch (e) {
    console.error(e)
    ElMessage.error('推送失败')
  } finally {
    loading.push = false
  }
}

const reloadAll = async () => {
  await Promise.all([
    loadSources(),
    loadMatches(),
    loadTasks(),
    loadBindings(),
    loadTimeWindowConfig(),
    loadAdvancedSettings()
  ])
}

onMounted(async () => {
  await reloadAll()
})
</script>

<style scoped>
.collection-page {
  padding: 20px;
}

.block {
  margin-bottom: 16px;
}

.block-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.block-header h3 {
  margin: 0;
  font-size: 18px;
}

.block-header p {
  margin: 4px 0 0;
  color: #667085;
  font-size: 13px;
}

.block-header-inline {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.time-window-config {
  display: flex;
  align-items: center;
  gap: 6px;
}

.debug-toolbar {
  margin-top: 10px;
  margin-bottom: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.task-tracker {
  margin-bottom: 10px;
}

.selection-tip {
  margin-top: 8px;
  color: #3b82f6;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.selection-sub-tip {
  color: #64748b;
}

.coverage-rate-text {
  display: block;
  font-size: 11px;
  color: #64748b;
  line-height: 1.2;
}

.row {
  margin-top: 8px;
}

.preview-box {
  margin-top: 12px;
  border: 1px solid #dbe3f0;
  border-radius: 8px;
  background: #f8fbff;
  padding: 10px 12px;
}

.preview-title {
  font-weight: 600;
  margin-bottom: 6px;
}

.preview-meta {
  display: flex;
  gap: 12px;
  color: #5b6472;
  font-size: 12px;
  margin-bottom: 8px;
}

.preview-box ul {
  margin: 0;
  padding-left: 16px;
}

.preview-box li {
  margin: 2px 0;
  color: #1f2937;
  font-size: 12px;
}

.result-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.item-inspector {
  margin-top: 10px;
  padding: 10px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fafcff;
}

.item-inspector-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  font-weight: 600;
  color: #334155;
}

.raw-box {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fafafa;
  padding: 10px 12px;
}

.raw-title {
  font-weight: 600;
  margin-bottom: 6px;
}

.raw-box pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 12px;
  color: #334155;
  max-height: 240px;
  overflow: auto;
}
</style>
