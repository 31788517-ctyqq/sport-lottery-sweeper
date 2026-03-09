<template>
  <div :class="tagsClasses">
    <!-- 标签标题 -->
    <div v-if="showTitle && title" class="intel-tags__title">
      <h4 class="intel-tags__title-text">{{ title }}</h4>
    </div>

    <!-- 标签列表 -->
    <div class="intel-tags__list">
      <button
        v-for="tag in displayedTags"
        :key="tag.id || tag"
        :class="['intel-tags__tag', `intel-tags__tag--${getTagType(tag)}`, { 'intel-tags__tag--active': isTagActive(tag) }]"
        @click="handleTagClick(tag)"
        @mouseenter="$emit('tag-hover', tag)"
        @mouseleave="$emit('tag-leave', tag)"
      >
        <span class="intel-tags__tag-text">{{ getTagLabel(tag) }}</span>
        
        <!-- 标签计数 -->
        <span v-if="showCount && tag.count !== undefined" class="intel-tags__count">
          {{ tag.count }}
        </span>
        
        <!-- 关闭按钮 -->
        <span v-if="removable && isTagActive(tag)" class="intel-tags__remove" @click.stop="removeTag(tag)">
          <svg width="12" height="12" viewBox="0 0 24 24">
            <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </span>
      </button>

      <!-- 显示更多标签 -->
      <button
        v-if="showMoreButton && hiddenTagsCount > 0"
        class="intel-tags__more"
        @click="showAll = true"
      >
        +{{ hiddenTagsCount }} 更多
      </button>

      <!-- 添加标签按钮 -->
      <button
        v-if="showAddButton"
        class="intel-tags__add"
        @click="$emit('add')"
        aria-label="添加标签"
      >
        <svg width="14" height="14" viewBox="0 0 24 24">
          <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
        </svg>
        <span v-if="!compact">添加</span>
      </button>
    </div>

    <!-- 标签描述 -->
    <div v-if="showDescription && selectedTag && selectedTag.description" class="intel-tags__description">
      {{ selectedTag.description }}
    </div>

    <!-- 无标签状态 -->
    <div v-if="showEmptyState && tags.length === 0" class="intel-tags__empty">
      <EmptyState
        :title="emptyTitle"
        :description="emptyDescription"
        icon="🏷️"
        variant="compact"
        :action-text="addButtonText"
        @action="$emit('add')"
      />
    </div>

    <!-- 全屏标签选择器 -->
    <BaseModal
      v-if="showFullscreenSelector"
      v-model="showFullscreenSelector"
      title="选择标签"
      size="large"
    >
      <div class="intel-tags__fullscreen">
        <!-- 搜索框 -->
        <div v-if="searchable" class="intel-tags__search">
          <BaseInput
            v-model="searchQuery"
            placeholder="搜索标签..."
            size="small"
            prepend-icon="search"
            clearable
          />
        </div>

        <!-- 分类标签 -->
        <div v-if="showCategories" class="intel-tags__categories">
          <button
            v-for="category in categories"
            :key="category.id"
            :class="['intel-tags__category', { 'intel-tags__category--active': activeCategory === category.id }]"
            @click="activeCategory = category.id"
          >
            {{ category.name }}
            <span v-if="category.count" class="intel-tags__category-count">{{ category.count }}</span>
          </button>
        </div>

        <!-- 标签网格 -->
        <div class="intel-tags__grid">
          <div
            v-for="tag in filteredTags"
            :key="tag.id || tag"
            :class="['intel-tags__grid-item', { 'intel-tags__grid-item--selected': isTagActive(tag) }]"
            @click="toggleTagSelection(tag)"
          >
            <div class="intel-tags__grid-content">
              <div class="intel-tags__grid-label">{{ getTagLabel(tag) }}</div>
              <div v-if="tag.description" class="intel-tags__grid-description">{{ tag.description }}</div>
              <div v-if="showCount && tag.count" class="intel-tags__grid-count">
                使用次数: {{ tag.count }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="intel-tags__modal-actions">
          <BaseButton variant="outline" @click="showFullscreenSelector = false">取消</BaseButton>
          <BaseButton variant="primary" @click="confirmSelection">确认选择</BaseButton>
        </div>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import BaseInput from '../common/BaseInput.vue'
import BaseButton from '../common/BaseButton.vue'
import BaseModal from '../common/BaseModal.vue'
import EmptyState from '../common/EmptyState.vue'

const props = defineProps({
  tags: {
    type: Array,
    default: () => []
  },
  selectedTags: {
    type: Array,
    default: () => []
  },
  title: {
    type: String,
    default: '标签'
  },
  limit: {
    type: Number,
    default: null
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'outlined', 'filled', 'pill'].includes(value)
  },
  compact: {
    type: Boolean,
    default: false
  },
  showTitle: {
    type: Boolean,
    default: false
  },
  showCount: {
    type: Boolean,
    default: false
  },
  showDescription: {
    type: Boolean,
    default: false
  },
  showAddButton: {
    type: Boolean,
    default: false
  },
  showMoreButton: {
    type: Boolean,
    default: true
  },
  showEmptyState: {
    type: Boolean,
    default: false
  },
  clickable: {
    type: Boolean,
    default: true
  },
  removable: {
    type: Boolean,
    default: false
  },
  selectable: {
    type: Boolean,
    default: false
  },
  multiple: {
    type: Boolean,
    default: true
  },
  emptyTitle: {
    type: String,
    default: '暂无标签'
  },
  emptyDescription: {
    type: String,
    default: '添加标签以便更好地分类和管理'
  },
  addButtonText: {
    type: String,
    default: '添加标签'
  },
  searchable: {
    type: Boolean,
    default: false
  },
  showCategories: {
    type: Boolean,
    default: false
  },
  categories: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits([
  'tag-click',
  'tag-hover',
  'tag-leave',
  'tag-select',
  'tag-remove',
  'add',
  'update:selectedTags'
])

const showAll = ref(false)
const searchQuery = ref('')
const activeCategory = ref(null)
const showFullscreenSelector = ref(false)
const tempSelectedTags = ref([...props.selectedTags])

// 计算属性
const tagsClasses = computed(() => ({
  'intel-tags': true,
  'intel-tags--compact': props.compact,
  [`intel-tags--${props.size}`]: true,
  [`intel-tags--${props.variant}`]: true,
  'intel-tags--selectable': props.selectable,
  'intel-tags--multiple': props.multiple
}))

const displayedTags = computed(() => {
  let tags = props.tags
  
  // 应用搜索
  if (searchQuery.value) {
    tags = tags.filter(tag => {
      const label = getTagLabel(tag).toLowerCase()
      return label.includes(searchQuery.value.toLowerCase())
    })
  }
  
  // 应用分类筛选
  if (activeCategory.value && props.showCategories) {
    tags = tags.filter(tag => tag.category === activeCategory.value)
  }
  
  // 应用数量限制
  if (!showAll.value && props.limit && tags.length > props.limit) {
    return tags.slice(0, props.limit)
  }
  
  return tags
})

const hiddenTagsCount = computed(() => {
  if (!props.limit || props.tags.length <= props.limit) return 0
  return props.tags.length - props.limit
})

const selectedTag = computed(() => {
  if (props.selectedTags.length === 0) return null
  if (!props.multiple && props.selectedTags.length > 0) {
    return props.selectedTags[0]
  }
  return null
})

const filteredTags = computed(() => {
  let tags = props.tags
  
  // 应用搜索
  if (searchQuery.value) {
    tags = tags.filter(tag => {
      const label = getTagLabel(tag).toLowerCase()
      return label.includes(searchQuery.value.toLowerCase())
    })
  }
  
  // 应用分类筛选
  if (activeCategory.value && props.showCategories) {
    tags = tags.filter(tag => tag.category === activeCategory.value)
  }
  
  return tags
})

// 方法
const getTagLabel = (tag) => {
  if (typeof tag === 'string') return tag
  return tag.label || tag.name || tag.id || '未知标签'
}

const getTagType = (tag) => {
  if (typeof tag === 'string') return 'default'
  return tag.type || tag.category || 'default'
}

const isTagActive = (tag) => {
  const tagId = typeof tag === 'string' ? tag : tag.id || tag.label
  return props.selectedTags.some(selectedTag => {
    const selectedId = typeof selectedTag === 'string' ? selectedTag : selectedTag.id || selectedTag.label
    return selectedId === tagId
  })
}

const handleTagClick = (tag) => {
  if (!props.clickable) return
  
  if (props.selectable) {
    toggleTagSelection(tag)
  } else {
    emit('tag-click', tag)
  }
}

const toggleTagSelection = (tag) => {
  const tagId = typeof tag === 'string' ? tag : tag.id || tag.label
  
  if (!props.multiple) {
    // 单选模式
    if (isTagActive(tag)) {
      tempSelectedTags.value = []
    } else {
      tempSelectedTags.value = [tag]
    }
  } else {
    // 多选模式
    if (isTagActive(tag)) {
      tempSelectedTags.value = tempSelectedTags.value.filter(t => {
        const tId = typeof t === 'string' ? t : t.id || t.label
        return tId !== tagId
      })
    } else {
      tempSelectedTags.value.push(tag)
    }
  }
}

const removeTag = (tag) => {
  emit('tag-remove', tag)
}

const confirmSelection = () => {
  emit('update:selectedTags', [...tempSelectedTags.value])
  emit('tag-select', tempSelectedTags.value)
  showFullscreenSelector.value = false
}

const openFullscreenSelector = () => {
  tempSelectedTags.value = [...props.selectedTags]
  showFullscreenSelector.value = true
}

// 监听选中的标签变化
watch(() => props.selectedTags, (newVal) => {
  tempSelectedTags.value = [...newVal]
}, { deep: true })

// 暴露方法
defineExpose({
  openFullscreenSelector,
  closeFullscreenSelector: () => { showFullscreenSelector.value = false }
})
</script>

<style scoped>
.intel-tags {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.intel-tags--compact {
  gap: var(--spacing-2);
}

.intel-tags__title {
  margin-bottom: var(--spacing-1);
}

.intel-tags__title-text {
  margin: 0;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-secondary);
}

.intel-tags__list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-2);
}

.intel-tags__tag {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-1);
  padding: var(--spacing-1) var(--spacing-3);
  border: none;
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}

.intel-tags__tag:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.intel-tags__tag--active {
  font-weight: 600;
}

/* 尺寸 */
.intel-tags--small .intel-tags__tag {
  padding: 2px 8px;
  font-size: var(--font-size-xs);
}

.intel-tags--medium .intel-tags__tag {
  padding: 4px 12px;
  font-size: var(--font-size-sm);
}

.intel-tags--large .intel-tags__tag {
  padding: 6px 16px;
  font-size: var(--font-size-base);
}

/* 变体 */
.intel-tags--default .intel-tags__tag {
  background-color: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.intel-tags--outlined .intel-tags__tag {
  background-color: transparent;
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.intel-tags--filled .intel-tags__tag {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

.intel-tags--pill .intel-tags__tag {
  border-radius: var(--radius-full);
}

/* 标签类型 */
.intel-tags__tag--injury {
  background-color: var(--color-danger-light);
  color: var(--color-danger-dark);
}

.intel-tags__tag--lineup {
  background-color: var(--color-primary-light);
  color: var(--color-primary-dark);
}

.intel-tags__tag--suspension {
  background-color: var(--color-warning-light);
  color: var(--color-warning-dark);
}

.intel-tags__tag--weather {
  background-color: var(--color-info-light);
  color: var(--color-info-dark);
}

.intel-tags__tag--referee {
  background-color: var(--color-success-light);
  color: var(--color-success-dark);
}

.intel-tags__tag--venue {
  background-color: var(--color-secondary-light);
  color: var(--color-secondary-dark);
}

.intel-tags__tag--manager {
  background-color: var(--color-purple-light);
  color: var(--color-purple-dark);
}

.intel-tags__tag--transfer {
  background-color: var(--color-pink-light);
  color: var(--color-pink-dark);
}

.intel-tags__tag--form {
  background-color: var(--color-orange-light);
  color: var(--color-orange-dark);
}

/* 选中状态 */
.intel-tags__tag--active {
  box-shadow: 0 0 0 2px currentColor;
}

.intel-tags__tag-text {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.intel-tags__count {
  font-size: var(--font-size-xs);
  background-color: rgba(0, 0, 0, 0.1);
  padding: 1px 4px;
  border-radius: var(--radius-sm);
  margin-left: 2px;
}

.intel-tags__remove {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, 0.1);
  margin-left: 4px;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.intel-tags__remove:hover {
  opacity: 1;
}

.intel-tags__more,
.intel-tags__add {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-1);
  padding: var(--spacing-1) var(--spacing-3);
  border: 1px dashed var(--color-border);
  background-color: transparent;
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.intel-tags__more:hover,
.intel-tags__add:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.intel-tags__description {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin-top: var(--spacing-1);
  padding: var(--spacing-2);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
}

.intel-tags__empty {
  padding: var(--spacing-6) 0;
}

/* 全屏选择器 */
.intel-tags__fullscreen {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-6);
  min-height: 400px;
  max-height: 70vh;
  overflow-y: auto;
}

.intel-tags__search {
  position: sticky;
  top: 0;
  background-color: var(--color-bg-card);
  padding-bottom: var(--spacing-4);
  z-index: 1;
}

.intel-tags__categories {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-2);
}

.intel-tags__category {
  padding: var(--spacing-2) var(--spacing-3);
  border: 1px solid var(--color-border);
  background-color: transparent;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.intel-tags__category:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.intel-tags__category--active {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.intel-tags__category-count {
  margin-left: var(--spacing-1);
  font-size: var(--font-size-xs);
  background-color: rgba(0, 0, 0, 0.1);
  padding: 1px 4px;
  border-radius: var(--radius-sm);
}

.intel-tags__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--spacing-3);
}

.intel-tags__grid-item {
  padding: var(--spacing-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
  background-color: var(--color-bg-secondary);
}

.intel-tags__grid-item:hover {
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.intel-tags__grid-item--selected {
  border-color: var(--color-primary);
  background-color: rgba(var(--color-primary-rgb), 0.1);
}

.intel-tags__grid-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.intel-tags__grid-label {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text-primary);
}

.intel-tags__grid-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.4;
}

.intel-tags__grid-count {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.intel-tags__modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-3);
}

/* 响应式 */
@media (max-width: 768px) {
  .intel-tags__grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}
</style>