# Sport-Lottery-Sweeper 文件生成指令示例清单

> 🚀 **快捷模板**（一句话生成文件）：
> **“在 `[模块类型/别名路径]` 创建 `[文件名.扩展名]`，用于 `[简要用途]`”**
> - `[模块类型/别名路径]`：用 `@/xxx` 别名或绝对路径指定目标文件夹（如 `@/components/common` 或 `src/views/user`）
> - `[文件名.扩展名]`：完整文件名+扩展名
> - `[简要用途]`：可选，但建议填写，帮助 AI 判断类别和规范
> 
> ✅ 示例：
> - `在 @/components/common 创建 LoadingSpinner.vue，用于通用加载动画`
> - `在 src/api 创建 userApi.ts，用于用户相关接口请求`
> - `在 backend/models 创建 betting.py，用于投注数据模型`
> - `在 src/tests/unit/components 创建 MatchCard.spec.ts，用于 MatchCard.vue 的单元测试`
> 
> 按此模板发指令，AI 会自动匹配项目结构规则并生成到正确目录。

> 📌 **目的**：统一团队成员与 AI 的文件生成路径，确保所有新文件都符合项目结构与命名规范。
> 📜 **依据**：`<always_applied_workspace_rules>` 与项目目录规范。

---

## 1️⃣ Vue 组件
| 场景 | 示例指令 | 生成路径（绝对路径） |
|------|----------|---------------------|
| 通用组件 | “在 `@/components/common` 创建一个 `LoadingSpinner.vue` 通用加载组件” | `c:/Users/11581/Downloads/sport-lottery-sweeper/frontend/src/components/common/LoadingSpinner.vue` |
| 业务组件 | “生成一个比赛卡片组件，放到 `src/components/business/MatchCard.vue`” | `c:/Users/11581/Downloads/sport-lottery-sweeper/frontend/src/components/business/MatchCard.vue` |
| 管理后台组件 | “在 `@/components/admin` 创建 `AdminDashboard.vue`” | `c:/Users/11581/Downloads/sport-lottery-sweeper/frontend/src/components/admin/AdminDashboard.vue` |

---

## 2️⃣ 页面组件（Views）
| 场景 | 示例指令 | 生成路径 |
|------|----------|----------|
| 普通页面 | “在 `src/views/user` 创建 `UserProfile.vue` 页面” | `.../frontend/src/views/user/UserProfile.vue` |
| 管理页面 | “生成管理用户页面 `@/views/admin/UserManagement.vue`” | `.../frontend/src/views/admin/UserManagement.vue` |

---

## 3️⃣ 组合式函数（Composables）
| 场景 | 示例指令 | 生成路径 |
|------|----------|----------|
| 通用逻辑 | “在 `@/composables` 创建 `useApi.ts`” | `.../frontend/src/composables/useApi.ts` |
| 业务相关 | “新建 `useMatchData.js` 放到 `src/composables/match/`” | `.../frontend/src/composables/match/useMatchData.js` |

---

## 4️⃣ 状态管理（Store - Pinia）
| 场景 | 示例指令 | 生成路径 |
|------|----------|----------|
| 用户模块 | “在 `@/stores` 创建 `userStore.ts`” | `.../frontend/src/stores/userStore.ts` |
| 比赛模块 | “生成 `matchStore.js` 放到 `src/stores/`” | `.../frontend/src/stores/matchStore.js` |

---

## 5️⃣ 工具函数（Utils）
| 场景 | 示例指令 | 生成路径 |
|------|----------|----------|
| 通用工具 | “在 `@/utils` 创建 `formatters.ts`” | `.../frontend/src/utils/formatters.ts` |
| 日期处理 | “新建 `dateUtil.js` 放到 `src/utils/`” | `.../frontend/src/utils/dateUtil.js` |

---

## 6️⃣ API 接口文件
| 场景 | 示例指令 | 生成路径 |
|------|----------|----------|
| 用户接口 | “在 `@/api` 创建 `userApi.ts`” | `.../frontend/src/api/userApi.ts` |
| 比赛数据接口 | “生成 `matchApi.js` 放到 `src/api/`” | `.../frontend/src/api/matchApi.js` |

---

## 7️⃣ 样式文件（Styles）
| 场景 | 示例指令 | 生成路径 |
|------|----------|----------|
| 全局样式 | “在 `@/styles` 创建 `variables.scss`” | `.../frontend/src/styles/variables.scss` |
| 组件样式 | “新建 `match-card.css` 放到 `src/styles/components/`” | `.../frontend/src/styles/components/match-card.css` |

---

## 8️⃣ 布局组件（Layout）
| 场景 | 示例指令 | 生成路径 |
|------|----------|----------|
| 主布局 | “在 `@/layout` 创建 `MainLayout.vue`” | `.../frontend/src/layout/MainLayout.vue` |
| 管理布局 | “生成 `AdminLayout.vue` 放到 `src/layout/`” | `.../frontend/src/layout/AdminLayout.vue` |

---

## 9️⃣ 单元测试文件
> 规则：测试目录与源码目录**平行组织**  
> 组件测试 → `src/tests/unit/components/`  
> 页面测试 → `src/tests/unit/views/`  
> 组合式函数测试 → `src/tests/unit/composables/`  
> Store 测试 → `src/tests/unit/store/`  
> Utils 测试 → `src/tests/unit/utils/`

| 场景 | 示例指令 | 生成路径 |
|------|----------|----------|
| 组件测试 | “给 `src/components/business/MatchCard.vue` 写单元测试，放到对应测试目录” | `.../frontend/src/tests/unit/components/MatchCard.spec.ts` |
| API 测试 | “给 `src/api/userApi.ts` 写单元测试” | `.../frontend/src/tests/unit/api/userApi.spec.ts` |

---

## 🔟 后端文件（Python）
| 场景 | 示例指令 | 生成路径 |
|------|----------|----------|
| 数据模型 | “在 `backend/models` 创建 `betting.py` 模型文件” | `c:/Users/11581/Downloads/sport-lottery-sweeper/backend/models/betting.py` |
| API 路由 | “生成 `match_routes.py` 放到 `backend/api/`” | `.../backend/api/match_routes.py` |
| 工具脚本 | “在 `scripts/utils` 创建 `cleanup_temp.py`” | `.../scripts/utils/cleanup_temp.py` |

---

## ✅ 使用说明
1. **用项目别名**（如 `@/components`）或直接给**绝对路径**都可以，我会自动转换。  
2. **必须指明文件类型/模块**（component/view/composable/store/util/api/test），以便我匹配规则。  
3. 如果有**新目录需求**，我会在规则允许范围内创建，并遵循标准结构。  
4. 所有路径均为**绝对路径**（规则要求），避免相对路径出错。  
5. 本清单应作为团队与 AI 协作的通用指令模板。

---

**最后更新**：2025-01-22  
**维护者**：开发团队 & AI 编程助手