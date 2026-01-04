<script setup lang="ts">
/**
 * A2UI 渲染器组件
 * 
 * 真正的 A2UI 实现：
 * 1. Gemini LLM 直接生成声明式的 A2UI JSON
 * 2. 本渲染器解析 JSON 并映射到 Vue 原生组件
 * 3. 支持递归渲染嵌套组件
 * 
 * A2UI 标准流程：
 * 生成(LLM) → 传输(JSON) → 解析(本组件) → 渲染(Vue组件映射)
 * 
 * 参考: https://github.com/google/A2UI
 */
import { computed } from 'vue'

// A2UI 组件接口定义
interface A2UIComponent {
  id: string
  type: string
  props?: Record<string, any>
  children?: string[]
}

interface A2UIData {
  version: string
  root: string
  components: A2UIComponent[]
  data?: {
    question?: string
    originalHexagram?: any
    changedHexagram?: any
    lines?: any[]
  }
  metadata?: {
    hexagramName?: string
    question?: string
    generatedBy?: string
    isNativeA2UI?: boolean
  }
}

const props = defineProps<{
  data: A2UIData
}>()

// 建立组件 ID 到组件的映射
const componentMap = computed(() => {
  const map = new Map<string, A2UIComponent>()
  if (props.data?.components) {
    for (const component of props.data.components) {
      if (component.id) {
        map.set(component.id, component)
      }
    }
  }
  return map
})

// 获取根级组件（没有被其他组件引用为子组件的组件）
const rootComponents = computed(() => {
  if (!props.data?.components) return []
  
  // 收集所有被引用的子组件 ID
  const childIds = new Set<string>()
  for (const component of props.data.components) {
    if (component.children) {
      for (const childId of component.children) {
        childIds.add(childId)
      }
    }
  }
  
  // 返回没有被引用的组件（即根级组件）
  return props.data.components.filter(c => !childIds.has(c.id))
})

// 获取组件的子组件
function getChildren(component: A2UIComponent): A2UIComponent[] {
  if (!component.children) return []
  return component.children
    .map(id => componentMap.value.get(id))
    .filter((c): c is A2UIComponent => c !== undefined)
}

// 根据 badge 颜色获取 CSS 类
function getBadgeClass(color?: string): string {
  const colorMap: Record<string, string> = {
    'success': 'badge-success',
    'warning': 'badge-warning',
    'error': 'badge-error',
    'info': 'badge-info',
    'primary': 'badge-primary'
  }
  return colorMap[color || ''] || 'badge-default'
}

// 根据 card variant 获取 CSS 类
function getCardClass(variant?: string): string {
  const variantMap: Record<string, string> = {
    'elevated': 'card-elevated',
    'highlighted': 'card-highlighted',
    'warning': 'card-warning',
    'default': 'card-default'
  }
  return variantMap[variant || ''] || 'card-default'
}

// 检查是否是真正的 A2UI（由 LLM 直接生成）
const isNativeA2UI = computed(() => {
  return props.data?.metadata?.isNativeA2UI === true
})

// 格式化文本内容（处理换行符等）
function formatContent(content: string): string[] {
  if (!content) return []
  return content.split('\\n').filter(line => line.trim())
}
</script>

<template>
  <div class="a2ui-renderer">
    <!-- A2UI 标识 -->
    <div v-if="isNativeA2UI" class="a2ui-badge">
      <span class="a2ui-icon">⚡</span>
      <span>A2UI 动态渲染</span>
    </div>
    
    <!-- 递归渲染组件 -->
    <template v-for="component in rootComponents" :key="component.id">
      
      <!-- Card 组件 -->
      <div 
        v-if="component.type === 'card'" 
        class="a2ui-card"
        :class="getCardClass(component.props?.variant)"
      >
        <div class="card-header">
          <h3 class="card-title">{{ component.props?.title }}</h3>
        </div>
        <div class="card-content">
          <!-- 递归渲染子组件 -->
          <template v-for="child in getChildren(component)" :key="child.id">
            
            <!-- Text 组件 -->
            <div v-if="child.type === 'text'" class="a2ui-text" :class="child.props?.variant">
              <p v-for="(line, idx) in formatContent(child.props?.content || '')" :key="idx">
                {{ line }}
              </p>
            </div>
            
            <!-- Badge 组件 -->
            <div v-else-if="child.type === 'badge'" class="a2ui-badge-wrapper">
              <span class="a2ui-badge-label" :class="getBadgeClass(child.props?.color)">
                {{ child.props?.label }}
              </span>
            </div>
            
            <!-- List 组件 -->
            <component
              v-else-if="child.type === 'list'"
              :is="child.props?.ordered ? 'ol' : 'ul'"
              class="a2ui-list"
            >
              <li v-for="(item, idx) in child.props?.items || []" :key="idx">
                {{ item }}
              </li>
            </component>
            
            <!-- Container 组件（递归） -->
            <div 
              v-else-if="child.type === 'container'" 
              class="a2ui-container"
              :class="child.props?.layout"
            >
              <template v-for="grandChild in getChildren(child)" :key="grandChild.id">
                <div v-if="grandChild.type === 'text'" class="a2ui-text">
                  <p v-for="(line, idx) in formatContent(grandChild.props?.content || '')" :key="idx">
                    {{ line }}
                  </p>
                </div>
              </template>
            </div>
            
            <!-- 未知组件类型 -->
            <div v-else class="a2ui-unknown">
              <code>{{ child.type }}: {{ child.id }}</code>
            </div>
          </template>
        </div>
      </div>
      
      <!-- 独立 Text 组件（非 card 子组件） -->
      <div 
        v-else-if="component.type === 'text'" 
        class="a2ui-text standalone"
        :class="component.props?.variant"
      >
        <p v-for="(line, idx) in formatContent(component.props?.content || '')" :key="idx">
          {{ line }}
        </p>
      </div>
      
      <!-- 独立 Container 组件 -->
      <div 
        v-else-if="component.type === 'container'" 
        class="a2ui-container"
        :class="component.props?.layout"
      >
        <template v-for="child in getChildren(component)" :key="child.id">
          <div v-if="child.type === 'text'" class="a2ui-text">
            <p v-for="(line, idx) in formatContent(child.props?.content || '')" :key="idx">
              {{ line }}
            </p>
          </div>
        </template>
      </div>
      
    </template>
  </div>
</template>

<style scoped>
/* A2UI 渲染器容器 */
.a2ui-renderer {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* A2UI 标识 */
.a2ui-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  background: linear-gradient(135deg, rgba(100, 149, 237, 0.15), rgba(147, 112, 219, 0.15));
  border: 1px solid rgba(100, 149, 237, 0.3);
  border-radius: 1rem;
  font-size: 0.75rem;
  color: var(--color-gold, #d4af37);
  margin-bottom: 0.5rem;
  width: fit-content;
}

.a2ui-icon {
  font-size: 0.875rem;
}

/* Card 组件 */
.a2ui-card {
  background: var(--color-bg-card, rgba(26, 26, 26, 0.8));
  border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: 12px;
  padding: 1.25rem;
  transition: all 0.3s ease;
}

.a2ui-card:hover {
  border-color: rgba(212, 175, 55, 0.4);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(212, 175, 55, 0.15);
}

.card-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-gold, #d4af37);
  margin: 0;
}

.card-content {
  color: var(--color-text-secondary, #b8b8b8);
  line-height: 1.8;
}

/* Card 变体 */
.card-elevated {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
}

.card-highlighted {
  background: linear-gradient(135deg, var(--color-bg-card, rgba(26, 26, 26, 0.8)), rgba(212, 175, 55, 0.1));
  border-color: rgba(212, 175, 55, 0.4);
}

.card-warning {
  background: linear-gradient(135deg, var(--color-bg-card, rgba(26, 26, 26, 0.8)), rgba(227, 66, 52, 0.08));
  border-left: 3px solid var(--color-cinnabar, #e34234);
}

/* Text 组件 */
.a2ui-text {
  font-size: 1rem;
  line-height: 1.8;
}

.a2ui-text p {
  margin: 0.5rem 0;
}

.a2ui-text p:first-child {
  margin-top: 0;
}

.a2ui-text p:last-child {
  margin-bottom: 0;
}

.a2ui-text.caption {
  font-size: 0.9rem;
  color: var(--color-text-muted, #888);
}

.a2ui-text.standalone {
  padding: 1rem;
  background: var(--color-bg-card, rgba(26, 26, 26, 0.8));
  border-radius: 8px;
}

/* Badge 组件 */
.a2ui-badge-wrapper {
  margin: 0.75rem 0;
}

.a2ui-badge-label {
  display: inline-block;
  padding: 0.5rem 1.5rem;
  border-radius: 2rem;
  font-size: 1.25rem;
  font-weight: bold;
  text-align: center;
}

.badge-success {
  background: linear-gradient(135deg, rgba(0, 168, 107, 0.2), rgba(0, 168, 107, 0.1));
  color: #00a86b;
  border: 1px solid rgba(0, 168, 107, 0.4);
}

.badge-warning {
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.2), rgba(255, 193, 7, 0.1));
  color: #ffc107;
  border: 1px solid rgba(255, 193, 7, 0.4);
}

.badge-error {
  background: linear-gradient(135deg, rgba(227, 66, 52, 0.2), rgba(227, 66, 52, 0.1));
  color: #e34234;
  border: 1px solid rgba(227, 66, 52, 0.4);
}

.badge-info {
  background: linear-gradient(135deg, rgba(100, 149, 237, 0.2), rgba(100, 149, 237, 0.1));
  color: #6495ed;
  border: 1px solid rgba(100, 149, 237, 0.4);
}

.badge-default, .badge-primary {
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.2), rgba(212, 175, 55, 0.1));
  color: var(--color-gold, #d4af37);
  border: 1px solid rgba(212, 175, 55, 0.4);
}

/* List 组件 */
.a2ui-list {
  margin: 0.75rem 0;
  padding-left: 1.5rem;
  line-height: 1.8;
}

.a2ui-list li {
  margin: 0.5rem 0;
  color: var(--color-text-secondary, #b8b8b8);
}

.a2ui-list li::marker {
  color: var(--color-gold, #d4af37);
}

/* Container 组件 */
.a2ui-container {
  display: flex;
  gap: 1rem;
}

.a2ui-container.vertical {
  flex-direction: column;
}

.a2ui-container.horizontal {
  flex-direction: row;
  align-items: center;
}

/* 未知组件 */
.a2ui-unknown {
  padding: 0.5rem;
  background: rgba(255, 193, 7, 0.1);
  border: 1px dashed rgba(255, 193, 7, 0.3);
  border-radius: 4px;
  font-size: 0.75rem;
  color: #ffc107;
}
</style>
