<template>
  <div style="
    padding: 24px;
    color: #333;
    font-family: 'Arial', sans-serif;
  ">
    <h1>仪表板</h1>
    <p>欢迎来到管理后台</p>
    <div style="
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 16px;
      margin-top: 24px;
    ">
      <div style="
        background: #f5f5f5;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #7a8ca5;
      ">
        <h3>统计信息</h3>
        <p>这里是统计卡片</p>
      </div>
      <div style="
        background: #f5f5f5;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #5a6b5f;
      ">
        <h3>快捷操作</h3>
        <p>常用功能入口</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Dashboard'
}
</script>