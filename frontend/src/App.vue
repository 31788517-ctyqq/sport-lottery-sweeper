<template>
  <div id="app" v-cloak>
    <!-- 登录页单独显示，不显示后台布局 -->
    <div v-if="$route.path === '/admin/login'">
      <router-view key="login" />
    </div>

    <!-- 后台布局仅在非登录页显示 -->
    <div v-else>
    
    <!-- 侧边栏和主内容区 -->
    <div style="display: flex; min-height: calc(100vh - 64px);">
      <!-- 侧边栏 -->
      <aside style="
        width: 220px;
        background: #FFFFFF;
        border-right: 1px solid #E0DDD7;
        display: flex;
        flex-direction: column;
      ">
        <el-menu
          :default-active="$route.path"
          :router="true"
          style="
            border-right: none;
            background: transparent;
            color: #5A5A5A;
            flex: 1;
            font-size: 15px;
          "
          active-text-color="#A8C3A0"
        >
          <!-- 仪表板 -->
          <el-menu-item index="/admin/dashboard" style="margin: 8px 12px; border-radius: 8px; transition: background-color 0.3s ease, transform 0.2s ease;"
            onmouseover="this.style.backgroundColor='#EDE6DD'; this.style.transform='scale(1.02)'" 
            onmouseout="this.style.backgroundColor='transparent'; this.style.transform='scale(1)'">
            <el-icon style="margin-right: 8px; font-size: 18px;"><House /></el-icon>
            <span>仪表板</span>
          </el-menu-item>
          
          <!-- 用户管理 -->
          <el-sub-menu index="/admin/users" style="margin: 4px 12px; border-radius: 8px; transition: background-color 0.3s ease;"
            onmouseover="this.style.backgroundColor='#EDE6DD'" onmouseout="this.style.backgroundColor='transparent'">
            <template #title>
              <el-icon style="margin-right: 8px; font-size: 18px;"><User /></el-icon>
              <span>用户管理</span>
            </template>
            <el-menu-item index="/admin/users/backend" style="padding-left: 4em;">后端用户</el-menu-item>
            <el-menu-item index="/admin/users/frontend" style="padding-left: 4em;">前端用户</el-menu-item>
          </el-sub-menu>

          <!-- 赛程管理 -->
          <el-sub-menu index="/admin/match" style="margin: 4px 12px; border-radius: 8px; transition: background-color 0.3s ease;"
            onmouseover="this.style.backgroundColor='#EDE6DD'" onmouseout="this.style.backgroundColor='transparent'">
            <template #title>
              <el-icon style="margin-right: 8px; font-size: 18px;"><Calendar /></el-icon>
              <span>赛程管理</span>
            </template>
            <el-menu-item index="/admin/match/lottery" style="padding-left: 4em;">彩票赛程</el-menu-item>
            <el-menu-item index="/admin/match/spider" style="padding-left: 4em;">爬虫赛程</el-menu-item>
          </el-sub-menu>

          <!-- 情报管理 -->
          <el-menu-item index="/admin/intelligence" style="margin: 8px 12px; border-radius: 8px; transition: background-color 0.3s ease, transform 0.2s ease;"
            onmouseover="this.style.backgroundColor='#EDE6DD'; this.style.transform='scale(1.02)'" 
            onmouseout="this.style.backgroundColor='transparent'; this.style.transform='scale(1)'">
            <el-icon style="margin-right: 8px; font-size: 18px;"><DataAnalysis /></el-icon>
            <span>情报管理</span>
          </el-menu-item>

          <!-- 数据管理 -->
          <el-menu-item index="/admin/data" style="margin: 8px 12px; border-radius: 8px; transition: background-color 0.3s ease, transform 0.2s ease;"
            onmouseover="this.style.backgroundColor='#EDE6DD'; this.style.transform='scale(1.02)'" 
            onmouseout="this.style.backgroundColor='transparent'; this.style.transform='scale(1)'">
            <el-icon style="margin-right: 8px; font-size: 18px;"><FolderOpened /></el-icon>
            <span>数据管理</span>
          </el-menu-item>

          <!-- 爬虫管理 -->
          <el-sub-menu index="/admin/crawler" style="margin: 4px 12px; border-radius: 8px; padding-left: 0; transition: background-color 0.3s ease;"
            onmouseover="this.style.backgroundColor='#EDE6DD'" onmouseout="this.style.backgroundColor='transparent'">
            <template #title>
              <el-icon style="margin-right: 8px; font-size: 18px;"><SevenStarLadybugIcon /></el-icon>
              <span>爬虫管理</span>
            </template>
            <el-menu-item index="/admin/crawler/sources" style="padding-left: 4em;">数据源管理</el-menu-item>
            <el-menu-item index="/admin/crawler/tasks" style="padding-left: 4em;">任务调度</el-menu-item>
            <el-menu-item index="/admin/crawler/intelligence" style="padding-left: 4em;">数据情报</el-menu-item>
            <el-menu-item index="/admin/crawler/configs" style="padding-left: 4em;">爬虫配置</el-menu-item>
          </el-sub-menu>

          <!-- 足球SP管理 -->
          <el-sub-menu index="/admin/sp" style="margin: 4px 12px; border-radius: 8px; transition: background-color 0.3s ease;"
            onmouseover="this.style.backgroundColor='#EDE6DD'" onmouseout="this.style.backgroundColor='transparent'">
            <template #title>
              <el-icon style="margin-right: 8px; font-size: 18px;"><Soccer /></el-icon>
              <span>足球SP管理</span>
            </template>
            <el-menu-item index="/admin/sp/data-sources" style="padding-left: 4em;">数据源管理</el-menu-item>
            <el-menu-item index="/admin/sp/matches" style="padding-left: 4em;">比赛信息管理</el-menu-item>
            <el-menu-item index="/admin/sp/records" style="padding-left: 4em;">SP值管理</el-menu-item>
            <el-menu-item index="/admin/sp/analysis" style="padding-left: 4em;">数据分析与洞察</el-menu-item>
          </el-sub-menu>

          <!-- 平局预测 -->
          <el-sub-menu index="/admin/draw-prediction">
            <template #title>
              <el-icon style="margin-right: 8px; font-size: 18px;"><Football /></el-icon>
              <span>平局预测</span>
            </template>
            <el-menu-item index="/admin/draw-prediction/data-feature" style="padding-left: 4em;">数据特征工程</el-menu-item>
            <el-menu-item index="/admin/draw-prediction/model-train-eval" style="padding-left: 4em;">模型训练与评估</el-menu-item>
            <el-menu-item index="/admin/draw-prediction/manage-deploy" style="padding-left: 4em;">模型管理与部署</el-menu-item>
            <el-menu-item index="/admin/draw-prediction/prediction-monitor" style="padding-left: 4em;">预测监控</el-menu-item>
          </el-sub-menu>

          <!-- 系统管理 -->
          <el-menu-item index="/admin/system" style="margin: 8px 12px; border-radius: 8px; transition: background-color 0.3s ease, transform 0.2s ease;"
            onmouseover="this.style.backgroundColor='#EDE6DD'; this.style.transform='scale(1.02)'" 
            onmouseout="this.style.backgroundColor='transparent'; this.style.transform='scale(1)'">
            <el-icon style="margin-right: 8px; font-size: 18px;"><Setting /></el-icon>
            <span>系统管理</span>
          </el-menu-item>
        </el-menu>
      </aside>
      
      <!-- 主内容区 -->
      <main style="
        flex: 1;
        padding: 24px;
        background: #F4F2EF;
        overflow-y: auto;
      ">
        <div style="
          background: #FFFFFF;
          border-radius: 16px;
          min-height: calc(100vh - 112px);
          box-shadow: 0 2px 12px rgba(150,150,150,0.08);
          padding: 32px;
          transition: box-shadow 0.3s ease;
        " onmouseover="this.style.boxShadow='0 4px 20px rgba(150,150,150,0.12)'" onmouseout="this.style.boxShadow='0 2px 12px rgba(150,150,150,0.08)'">
          <router-view />
        </div>
    </main>
      </div>
    </div>
  </div>
</template>
