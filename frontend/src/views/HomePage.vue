<script setup lang="ts">
/**
 * 首页 - 占卜方式选择
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDivinationMethods, type DivinationMethod } from '@/services/api'

const router = useRouter()
const methods = ref<DivinationMethod[]>([])
const isLoading = ref(true)

// 方法图标映射（使用更大的图标）
const methodIcons: Record<string, string> = {
  liuyao: '☰',
  meihua: '✿',
  bazi: '命',
  qimen: '門'
}

// 方法背景色映射
const methodColors: Record<string, string> = {
  liuyao: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
  meihua: 'linear-gradient(135deg, #1a2e1a 0%, #163e16 100%)',
  bazi: 'linear-gradient(135deg, #2e1a1a 0%, #3e1616 100%)',
  qimen: 'linear-gradient(135deg, #1a1a2e 0%, #2e163e 100%)'
}

onMounted(async () => {
  try {
    methods.value = await getDivinationMethods()
  } catch (error) {
    // 使用默认数据
    methods.value = [
      { id: 'liuyao', name: '六爻占卜', description: '掷铜钱起卦，传统易经占卜术', icon: '🪙', available: true },
      { id: 'meihua', name: '梅花易数', description: '以数起卦，简洁高效', icon: '🌸', available: false },
      { id: 'bazi', name: '生辰八字', description: '根据出生时间推算命理', icon: '📅', available: false },
      { id: 'qimen', name: '奇门遁甲', description: '古老的预测术数', icon: '🚪', available: false }
    ]
  } finally {
    isLoading.value = false
  }
})

function selectMethod(method: DivinationMethod) {
  if (!method.available) return
  router.push(`/${method.id}`)
}
</script>

<template>
  <div class="home-page">
    <!-- 顶部装饰 -->
    <div class="header-decoration">
      <div class="bagua-circle">
        <svg viewBox="0 0 100 100" class="bagua-svg">
          <circle cx="50" cy="50" r="48" fill="none" stroke="var(--color-accent-gold)" stroke-width="0.5" opacity="0.3"/>
          <circle cx="50" cy="50" r="35" fill="none" stroke="var(--color-accent-gold)" stroke-width="0.5" opacity="0.2"/>
          <text x="50" y="55" text-anchor="middle" fill="var(--color-accent-gold)" font-size="20" class="bagua-text">☯</text>
        </svg>
      </div>
    </div>

    <!-- 标题区域 -->
    <header class="page-header">
      <h1 class="main-title title-brush">周易占卜</h1>
      <p class="subtitle">古老智慧 · 指引迷津</p>
      <div class="divider-gold"></div>
    </header>

    <!-- 占卜方式列表 -->
    <main class="methods-section">
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner">☯</div>
        <p>加载中...</p>
      </div>

      <div v-else class="methods-grid">
        <div
          v-for="(method, index) in methods"
          :key="method.id"
          class="method-card"
          :class="{ 'disabled': !method.available }"
          :style="{ 
            animationDelay: `${index * 0.1}s`,
            background: method.available ? methodColors[method.id] : undefined
          }"
          @click="selectMethod(method)"
        >
          <div class="method-icon">
            <span class="icon-symbol">{{ methodIcons[method.id] || method.icon }}</span>
          </div>
          <div class="method-content">
            <h2 class="method-name">{{ method.name }}</h2>
            <p class="method-desc">{{ method.description }}</p>
          </div>
          <div class="method-status">
            <span v-if="method.available" class="status-badge available">可用</span>
            <span v-else class="status-badge coming">即将上线</span>
          </div>
          <div class="method-arrow" v-if="method.available">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
      </div>
    </main>

    <!-- 底部说明 -->
    <footer class="page-footer">
      <p class="footer-text">心诚则灵 · 问卦须知</p>
      <ul class="tips-list">
        <li>静心凝神，心怀诚意</li>
        <li>问事明确，不可贪多</li>
        <li>同事不二问，信则有验</li>
      </ul>
    </footer>
  </div>
</template>

<style scoped>
.home-page {
  min-height: 100vh;
  min-height: 100dvh;
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

/* 顶部装饰 */
.header-decoration {
  position: absolute;
  top: -50px;
  left: 50%;
  transform: translateX(-50%);
  opacity: 0.3;
  pointer-events: none;
}

.bagua-circle {
  width: 200px;
  height: 200px;
}

.bagua-svg {
  width: 100%;
  height: 100%;
  animation: rotate 60s linear infinite;
}

.bagua-text {
  font-size: 24px;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 页面头部 */
.page-header {
  text-align: center;
  padding: var(--spacing-xxl) 0 var(--spacing-lg);
  position: relative;
  z-index: 1;
}

.main-title {
  font-size: 3rem;
  margin-bottom: var(--spacing-sm);
  letter-spacing: 0.2em;
  background: linear-gradient(180deg, var(--color-accent-gold-light), var(--color-accent-gold));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  color: var(--color-text-secondary);
  font-size: 1rem;
  letter-spacing: 0.3em;
}

/* 方法区域 */
.methods-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: var(--spacing-lg) 0;
}

.loading-state {
  text-align: center;
  color: var(--color-text-secondary);
}

.loading-spinner {
  font-size: 3rem;
  color: var(--color-accent-gold);
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.methods-grid {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  max-width: 500px;
  margin: 0 auto;
  width: 100%;
}

/* 方法卡片 */
.method-card {
  display: flex;
  align-items: center;
  padding: var(--spacing-lg);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.5s ease forwards;
  opacity: 0;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.method-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, transparent, rgba(212, 175, 55, 0.05));
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.method-card:hover::before {
  opacity: 1;
}

.method-card:hover {
  transform: translateX(8px);
  border-color: var(--color-accent-gold);
  box-shadow: var(--shadow-glow);
}

.method-card.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.method-card.disabled:hover {
  transform: none;
  border-color: var(--color-border);
  box-shadow: none;
}

.method-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(212, 175, 55, 0.1);
  border-radius: var(--radius-md);
  margin-right: var(--spacing-md);
  flex-shrink: 0;
}

.icon-symbol {
  font-size: 1.8rem;
  color: var(--color-accent-gold);
  font-family: var(--font-brush);
}

.method-content {
  flex: 1;
}

.method-name {
  font-size: 1.2rem;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xs);
  font-weight: 500;
}

.method-desc {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

.method-status {
  margin-left: var(--spacing-md);
}

.status-badge {
  font-size: 0.7rem;
  padding: 4px 8px;
  border-radius: 20px;
  white-space: nowrap;
}

.status-badge.available {
  background: rgba(0, 168, 107, 0.2);
  color: var(--color-jade);
  border: 1px solid rgba(0, 168, 107, 0.3);
}

.status-badge.coming {
  background: rgba(212, 175, 55, 0.1);
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
}

.method-arrow {
  color: var(--color-accent-gold);
  margin-left: var(--spacing-sm);
  opacity: 0;
  transform: translateX(-10px);
  transition: all var(--transition-fast);
}

.method-card:hover .method-arrow {
  opacity: 1;
  transform: translateX(0);
}

/* 页面底部 */
.page-footer {
  text-align: center;
  padding: var(--spacing-xl) 0 var(--spacing-lg);
  color: var(--color-text-muted);
}

.footer-text {
  font-size: 0.9rem;
  margin-bottom: var(--spacing-md);
  color: var(--color-text-secondary);
}

.tips-list {
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: var(--spacing-sm) var(--spacing-lg);
  font-size: 0.8rem;
}

.tips-list li {
  position: relative;
  padding-left: 1em;
}

.tips-list li::before {
  content: '·';
  position: absolute;
  left: 0;
  color: var(--color-accent-gold);
}

/* 响应式 */
@media (max-width: 480px) {
  .main-title {
    font-size: 2.5rem;
  }
  
  .method-card {
    padding: var(--spacing-md);
  }
  
  .method-icon {
    width: 50px;
    height: 50px;
  }
  
  .icon-symbol {
    font-size: 1.5rem;
  }
}
</style>

