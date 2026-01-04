<script setup lang="ts">
/**
 * 六爻占卜 - 问卦页面
 * 用户在此输入要问的问题
 */
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDivinationStore } from '@/stores/divination'

const router = useRouter()
const store = useDivinationStore()

const question = ref(store.question || '')
const isFocused = ref(false)

// 示例问题
const exampleQuestions = [
  '近期事业发展如何？',
  '此次合作是否顺利？',
  '姻缘何时能到？',
  '投资是否可行？'
]

const canProceed = computed(() => question.value.trim().length >= 2)

// 默认使用 DeepSeek 模型
onMounted(() => {
  // 强制设置为 deepseek
  store.setSelectedModel('deepseek')
})

function setExample(example: string) {
  question.value = example
}

function goBack() {
  router.push('/')
}

function proceed() {
  if (!canProceed.value) return
  store.setQuestion(question.value.trim())
  router.push('/liuyao/divine')
}
</script>

<template>
  <div class="question-page">
    <!-- 返回按钮 -->
    <button class="back-btn" @click="goBack">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span>返回</span>
    </button>

    <!-- 页面内容 -->
    <div class="page-content">
      <!-- 标题区域 -->
      <header class="section-header">
        <div class="icon-wrapper">
          <span class="method-icon">☰</span>
        </div>
        <h1 class="title-brush page-title">六爻占卜</h1>
        <p class="page-subtitle">请静心思考，写下您想问的事情</p>
      </header>

      <!-- 输入区域 -->
      <div class="input-section">
        <div class="input-wrapper" :class="{ focused: isFocused }">
          <textarea
            v-model="question"
            placeholder="请输入您要问的问题..."
            rows="4"
            maxlength="200"
            @focus="isFocused = true"
            @blur="isFocused = false"
          ></textarea>
          <div class="char-count">{{ question.length }}/200</div>
        </div>

        <!-- 提示信息 -->
        <div class="input-tips">
          <p class="tip-title">问卦须知：</p>
          <ul class="tip-list">
            <li>问题应明确具体，如"此次面试是否顺利"</li>
            <li>一事一问，不可同时问多件事</li>
            <li>已问之事，不可重复再问</li>
          </ul>
        </div>
      </div>

      <!-- 示例问题 -->
      <div class="examples-section">
        <p class="examples-title">示例问题：</p>
        <div class="examples-grid">
          <button
            v-for="example in exampleQuestions"
            :key="example"
            class="example-btn"
            @click="setExample(example)"
          >
            {{ example }}
          </button>
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="action-section">
        <button 
          class="btn-primary proceed-btn"
          :disabled="!canProceed"
          @click="proceed"
        >
          <span>开始起卦</span>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.question-page {
  min-height: 100vh;
  min-height: 100dvh;
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
}

/* 返回按钮 */
.back-btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  color: var(--color-text-secondary);
  padding: var(--spacing-sm);
  margin: 0 0 var(--spacing-md) calc(-1 * var(--spacing-sm));
  transition: color var(--transition-fast);
}

.back-btn:hover {
  color: var(--color-accent-gold);
}

/* 页面内容 */
.page-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 500px;
  margin: 0 auto;
  width: 100%;
}

/* 头部区域 */
.section-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.icon-wrapper {
  width: 80px;
  height: 80px;
  margin: 0 auto var(--spacing-md);
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(212, 175, 55, 0.1);
  border: 1px solid var(--color-border);
  border-radius: 50%;
}

.method-icon {
  font-size: 2.5rem;
  color: var(--color-accent-gold);
}

.page-title {
  font-size: 2rem;
  margin-bottom: var(--spacing-sm);
}

.page-subtitle {
  color: var(--color-text-secondary);
  font-size: 0.95rem;
}

/* 输入区域 */
.input-section {
  margin-bottom: var(--spacing-xl);
}

.input-wrapper {
  position: relative;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
  transition: all var(--transition-fast);
}

.input-wrapper.focused {
  border-color: var(--color-accent-gold);
  box-shadow: var(--shadow-glow);
}

.input-wrapper textarea {
  width: 100%;
  background: transparent;
  border: none;
  color: var(--color-text-primary);
  font-size: 1rem;
  line-height: 1.6;
  resize: none;
}

.input-wrapper textarea:focus {
  outline: none;
  box-shadow: none;
}

.input-wrapper textarea::placeholder {
  color: var(--color-text-muted);
}

.char-count {
  text-align: right;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin-top: var(--spacing-sm);
}

/* 提示信息 */
.input-tips {
  margin-top: var(--spacing-md);
  padding: var(--spacing-md);
  background: rgba(212, 175, 55, 0.05);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--color-accent-gold);
}

.tip-title {
  font-size: 0.85rem;
  color: var(--color-accent-gold);
  margin-bottom: var(--spacing-sm);
}

.tip-list {
  list-style: none;
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}

.tip-list li {
  position: relative;
  padding-left: 1em;
  margin-bottom: var(--spacing-xs);
}

.tip-list li::before {
  content: '·';
  position: absolute;
  left: 0;
  color: var(--color-accent-gold);
}

/* 示例问题 */
.examples-section {
  margin-bottom: var(--spacing-xl);
}

.examples-title {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-sm);
}

.examples-grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.example-btn {
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: 20px;
  color: var(--color-text-secondary);
  font-size: 0.85rem;
  transition: all var(--transition-fast);
}

.example-btn:hover {
  border-color: var(--color-accent-gold);
  color: var(--color-accent-gold);
  background: rgba(212, 175, 55, 0.1);
}

/* 底部按钮 */
.action-section {
  margin-top: auto;
  padding-top: var(--spacing-lg);
}

.proceed-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  font-size: 1.1rem;
  padding: var(--spacing-md) var(--spacing-xl);
}

/* 响应式 */
@media (max-width: 480px) {
  .page-title {
    font-size: 1.8rem;
  }
  
  .icon-wrapper {
    width: 70px;
    height: 70px;
  }
  
  .method-icon {
    font-size: 2rem;
  }
}
</style>

