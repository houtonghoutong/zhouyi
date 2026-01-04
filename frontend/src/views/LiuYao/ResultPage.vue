<script setup lang="ts">
/**
 * 六爻占卜 - 卦象结果页面
 * 使用 A2UI 概念动态渲染卦象解读
 */
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDivinationStore } from '@/stores/divination'
import A2UIRenderer from '@/components/A2UIRenderer.vue'
import HexagramVisual from '@/components/HexagramVisual.vue'
import SharePoster from '@/components/SharePoster.vue'

const router = useRouter()
const store = useDivinationStore()

const showContent = ref(false)
const showSharePoster = ref(false)

// 计算属性
const result = computed(() => store.result)
const a2uiData = computed(() => result.value?.a2uiResponse)
const hexagramData = computed(() => a2uiData.value?.data)

// 从 A2UI 组件中提取吉凶信息
const fortuneInfo = computed(() => {
  if (!a2uiData.value?.components) {
    return { text: '平', type: 'warning' as const }
  }
  
  // 查找 badge 组件获取吉凶
  for (const comp of a2uiData.value.components) {
    if (comp.type === 'badge' && comp.props?.label) {
      const label = comp.props.label
      const color = comp.props.color || 'warning'
      const typeMap: Record<string, 'success' | 'warning' | 'error'> = {
        'success': 'success',
        'warning': 'warning',
        'error': 'error'
      }
      return { text: label, type: typeMap[color] || 'warning' }
    }
  }
  
  return { text: '平', type: 'warning' as const }
})

// 检查是否有结果
onMounted(() => {
  if (!store.result) {
    router.replace('/liuyao')
    return
  }
  
  // 延迟显示内容，增加仪式感
  setTimeout(() => {
    showContent.value = true
  }, 500)
})

// 返回首页
function goHome() {
  store.reset()
  router.push('/')
}

// 再问一卦
function askAgain() {
  store.reset()
  router.push('/liuyao')
}

// 打开分享海报
function openShare() {
  showSharePoster.value = true
}

// 关闭分享海报
function closeShare() {
  showSharePoster.value = false
}
</script>

<template>
  <div class="result-page">
    <!-- 加载动画 -->
    <transition name="fade">
      <div v-if="!showContent" class="loading-overlay">
        <div class="loading-content">
          <div class="bagua-spinner">☯</div>
          <p class="loading-text">卦象已成，解读中...</p>
        </div>
      </div>
    </transition>

    <!-- 结果内容 -->
    <transition name="fadeUp">
      <div v-if="showContent && result" class="result-content">
        <!-- 头部 -->
        <header class="result-header">
          <h1 class="title-brush result-title">卦象解读</h1>
          <div class="divider-gold"></div>
        </header>

        <!-- 卦象展示 -->
        <section class="hexagram-section">
          <div class="hexagram-card">
            <HexagramVisual 
              :lines="hexagramData?.lines || []"
              :original-hexagram="hexagramData?.originalHexagram"
              :changed-hexagram="hexagramData?.changedHexagram"
            />
          </div>
        </section>

        <!-- 问题回顾 -->
        <section class="question-section">
          <div class="section-card">
            <h2 class="section-title">
              <span class="title-icon">📜</span>
              所问之事
            </h2>
            <p class="question-text">{{ hexagramData?.question }}</p>
          </div>
        </section>

        <!-- A2UI 动态渲染区域 -->
        <section class="interpretation-section">
          <A2UIRenderer 
            v-if="a2uiData" 
            :data="a2uiData"
          />
        </section>

        <!-- 底部操作 -->
        <footer class="result-footer">
          <!-- 分享按钮（突出显示） -->
          <button class="share-btn" @click="openShare">
            <span class="share-icon">📤</span>
            <span class="share-text">分享到微信</span>
            <span class="share-hint">让好友也测测运势</span>
          </button>
          
          <div class="footer-actions">
            <button class="btn-secondary" @click="goHome">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              返回首页
            </button>
            <button class="btn-primary" @click="askAgain">
              再问一卦
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M23 4v6h-6M1 20v-6h6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
          
          <p class="footer-hint">卦象仅供参考，命运掌握在自己手中</p>
        </footer>
      </div>
    </transition>
    
    <!-- 分享海报弹窗 -->
    <SharePoster
      :visible="showSharePoster"
      :hexagram-name="result?.originalHexagram?.name || ''"
      :changed-hexagram-name="result?.changedHexagram?.name"
      :question="store.question"
      :fortune="fortuneInfo.text"
      :fortune-type="fortuneInfo.type"
      :upper-trigram="result?.originalHexagram?.upperTrigram?.name || ''"
      :lower-trigram="result?.originalHexagram?.lowerTrigram?.name || ''"
      @close="closeShare"
    />
  </div>
</template>

<style scoped>
.result-page {
  min-height: 100vh;
  min-height: 100dvh;
  position: relative;
}

/* 加载动画 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--color-bg-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.loading-content {
  text-align: center;
}

.bagua-spinner {
  font-size: 4rem;
  color: var(--color-accent-gold);
  animation: spin 2s linear infinite;
  margin-bottom: var(--spacing-lg);
}

.loading-text {
  color: var(--color-text-secondary);
  font-size: 1rem;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 结果内容 */
.result-content {
  padding: var(--spacing-lg);
  max-width: 600px;
  margin: 0 auto;
}

/* 头部 */
.result-header {
  text-align: center;
  padding: var(--spacing-lg) 0;
}

.result-title {
  font-size: 2.5rem;
  margin-bottom: var(--spacing-md);
}

/* 卦象展示 */
.hexagram-section {
  margin-bottom: var(--spacing-xl);
}

.hexagram-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-card);
}

/* 问题区域 */
.question-section {
  margin-bottom: var(--spacing-xl);
}

.section-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
}

.section-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 1rem;
  color: var(--color-accent-gold);
  margin-bottom: var(--spacing-md);
  font-weight: 500;
}

.title-icon {
  font-size: 1.2rem;
}

.question-text {
  color: var(--color-text-primary);
  font-size: 1.1rem;
  line-height: 1.6;
}

/* 解读区域 */
.interpretation-section {
  margin-bottom: var(--spacing-xl);
}

/* 底部 */
.result-footer {
  padding: var(--spacing-xl) 0;
  text-align: center;
}

/* 分享按钮（突出显示） */
.share-btn {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
  background: linear-gradient(135deg, rgba(7, 193, 96, 0.15), rgba(7, 193, 96, 0.05));
  border: 1px solid rgba(7, 193, 96, 0.3);
  border-radius: var(--radius-lg);
  transition: all 0.3s ease;
}

.share-btn:hover {
  background: linear-gradient(135deg, rgba(7, 193, 96, 0.25), rgba(7, 193, 96, 0.1));
  border-color: rgba(7, 193, 96, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(7, 193, 96, 0.2);
}

.share-btn:active {
  transform: translateY(0);
}

.share-icon {
  font-size: 1.5rem;
}

.share-text {
  font-size: 1.1rem;
  font-weight: 600;
  color: #07c160;
}

.share-hint {
  font-size: 0.8rem;
  color: rgba(7, 193, 96, 0.7);
}

.footer-actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
  margin-bottom: var(--spacing-lg);
}

.footer-actions button {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
}

.footer-hint {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

/* 动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fadeUp-enter-active {
  transition: all 0.8s ease;
}

.fadeUp-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

/* 响应式 */
@media (max-width: 480px) {
  .result-title {
    font-size: 2rem;
  }
  
  .footer-actions {
    flex-direction: column;
  }
  
  .footer-actions button {
    width: 100%;
    justify-content: center;
  }
}
</style>

