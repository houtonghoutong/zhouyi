<script setup lang="ts">
/**
 * 六爻占卜 - 掷铜钱页面
 * 模拟掷铜钱动画，用户点击6次完成起卦
 */
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useDivinationStore } from '@/stores/divination'
import { liuyaoDivination } from '@/services/api'

const router = useRouter()
const store = useDivinationStore()

// 状态
const isThrowingAnimation = ref(false)
const currentCoins = ref<number[]>([])
const throwHistory = ref<Array<{ coins: number[], type: string, symbol: string }>>([])
const showMeditationHint = ref(true)
const isSubmitting = ref(false)
const errorMessage = ref<string | null>(null)

// 计算属性
const currentThrow = computed(() => throwHistory.value.length + 1)
const isComplete = computed(() => throwHistory.value.length >= 6)
const canThrow = computed(() => !isThrowingAnimation.value && !isComplete.value && !isSubmitting.value)

// 爻类型判断
function getYaoType(coins: number[]): { type: string; symbol: string; name: string } {
  const heads = coins.reduce((sum, c) => sum + c, 0)
  
  if (heads === 3) {
    return { type: 'old_yang', symbol: '⚊', name: '老阳' }
  } else if (heads === 2) {
    return { type: 'young_yang', symbol: '⚊', name: '少阳' }
  } else if (heads === 1) {
    return { type: 'young_yin', symbol: '⚋', name: '少阴' }
  } else {
    return { type: 'old_yin', symbol: '⚋', name: '老阴' }
  }
}

// 掷铜钱动画
async function throwCoins() {
  if (!canThrow.value) return
  
  showMeditationHint.value = false
  isThrowingAnimation.value = true
  currentCoins.value = []
  
  // 动画：模拟铜钱翻转
  const animationDuration = 1500
  const flipInterval = 100
  let elapsed = 0
  
  const animationTimer = setInterval(() => {
    // 随机显示铜钱状态
    currentCoins.value = [
      Math.random() > 0.5 ? 1 : 0,
      Math.random() > 0.5 ? 1 : 0,
      Math.random() > 0.5 ? 1 : 0
    ]
    
    elapsed += flipInterval
    if (elapsed >= animationDuration) {
      clearInterval(animationTimer)
      
      // 最终结果
      const finalCoins = [
        Math.random() > 0.5 ? 1 : 0,
        Math.random() > 0.5 ? 1 : 0,
        Math.random() > 0.5 ? 1 : 0
      ]
      currentCoins.value = finalCoins
      
      // 记录结果
      const yaoType = getYaoType(finalCoins)
      throwHistory.value.push({
        coins: finalCoins,
        type: yaoType.type,
        symbol: yaoType.symbol
      })
      
      // 保存到 store
      store.addCoinResult(finalCoins)
      
      isThrowingAnimation.value = false
    }
  }, flipInterval)
}

// 提交占卜
async function submitDivination() {
  if (!isComplete.value || isSubmitting.value) return
  
  isSubmitting.value = true
  errorMessage.value = null
  store.setLoading(true)
  
  try {
    const result = await liuyaoDivination(
      store.question,
      throwHistory.value.map(t => t.coins),
      store.selectedModel  // 传入选中的 AI 模型
    )
    
    store.setResult(result)
    store.saveToLocal()
    router.push('/liuyao/result')
  } catch (error: any) {
    console.error('占卜失败:', error)
    const errMsg = error?.response?.data?.detail || error?.message || '占卜失败，请稍后重试'
    errorMessage.value = errMsg
    store.setError(errMsg)
  } finally {
    isSubmitting.value = false
    store.setLoading(false)
  }
}

// 重试
function retrySubmit() {
  errorMessage.value = null
  submitDivination()
}

// 返回
function goBack() {
  router.push('/liuyao')
}

// 检查是否有问题
onMounted(() => {
  if (!store.question) {
    router.replace('/liuyao')
  }
})

// 完成后自动提交
watch(isComplete, (complete) => {
  if (complete) {
    // 延迟一下让用户看到最后一爻
    setTimeout(() => {
      submitDivination()
    }, 1000)
  }
})
</script>

<template>
  <div class="divine-page">
    <!-- 神秘背景效果 -->
    <div class="mystic-bg">
      <div class="stars"></div>
      <div class="mist mist-1"></div>
      <div class="mist mist-2"></div>
      <div class="bagua-watermark">☯</div>
      <div class="energy-ring ring-1"></div>
      <div class="energy-ring ring-2"></div>
      <div class="energy-ring ring-3"></div>
    </div>

    <!-- 返回按钮 -->
    <button class="back-btn" @click="goBack" :disabled="isThrowingAnimation || isSubmitting">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span>返回</span>
    </button>

    <div class="page-content">
      <!-- 问题展示 -->
      <div class="question-display">
        <span class="question-label">所问之事</span>
        <p class="question-text">{{ store.question }}</p>
      </div>

      <!-- 进度指示 -->
      <div class="progress-section">
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: `${(throwHistory.length / 6) * 100}%` }"
          ></div>
        </div>
        <span class="progress-text">第 {{ Math.min(currentThrow, 6) }} 爻 / 共 6 爻</span>
      </div>

      <!-- 掷铜钱区域 -->
      <div class="coin-area">
        <!-- 冥想提示 -->
        <div v-if="showMeditationHint" class="meditation-hint">
          <div class="hint-icon">🧘</div>
          <p class="hint-text">请静心冥想，心中默念所问之事</p>
          <p class="hint-subtext">准备好后，点击下方开始掷铜钱</p>
        </div>

        <!-- 铜钱展示 - 真实铜钱设计 -->
        <div class="coins-display" :class="{ throwing: isThrowingAnimation }">
          <div 
            v-for="index in 3" 
            :key="index - 1"
            class="coin"
            :class="{ 
              heads: currentCoins[index - 1] === 1, 
              tails: currentCoins[index - 1] === 0,
              flipping: isThrowingAnimation
            }"
            :style="{ animationDelay: `${(index - 1) * 0.15}s` }"
          >
            <div class="coin-inner">
              <!-- 正面：有字的一面 -->
              <div class="coin-front">
                <div class="coin-outer-ring"></div>
                <div class="coin-square-hole"></div>
                <span class="coin-text top">開</span>
                <span class="coin-text bottom">元</span>
                <span class="coin-text left">通</span>
                <span class="coin-text right">寶</span>
              </div>
              <!-- 反面：光滑面 -->
              <div class="coin-back">
                <div class="coin-outer-ring"></div>
                <div class="coin-square-hole"></div>
                <div class="coin-pattern"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 当前结果 -->
        <div v-if="currentCoins.length === 3 && !isThrowingAnimation" class="current-result">
          <span class="result-coins">
            {{ currentCoins.map(c => c === 1 ? '字' : '背').join(' · ') }}
          </span>
          <span class="result-yao">
            {{ getYaoType(currentCoins).name }}
            <span class="yao-symbol">{{ getYaoType(currentCoins).symbol }}</span>
          </span>
        </div>
      </div>

      <!-- 已掷结果 - 卦象展示 -->
      <div class="history-section">
        <div class="hexagram-preview">
          <div 
            v-for="(item, index) in throwHistory" 
            :key="index"
            class="yao-row"
            :class="{ changing: item.type.startsWith('old') }"
          >
            <span class="yao-position">{{ ['初', '二', '三', '四', '五', '上'][index] }}爻</span>
            <div class="yao-visual" :class="[
              item.type.includes('yang') ? 'yang' : 'yin',
              item.type.startsWith('old') ? 'old' : 'young'
            ]">
              <!-- 阳爻：一条完整的线 -->
              <template v-if="item.type.includes('yang')">
                <div class="yao-bar full"></div>
              </template>
              <!-- 阴爻：中间断开的线 -->
              <template v-else>
                <div class="yao-bar left"></div>
                <div class="yao-gap"></div>
                <div class="yao-bar right"></div>
              </template>
              <!-- 动爻标记：老阳用○，老阴用× -->
              <span v-if="item.type === 'old_yang'" class="yao-marker yang-marker">○</span>
              <span v-if="item.type === 'old_yin'" class="yao-marker yin-marker">×</span>
            </div>
            <span class="yao-name" :class="{ 'is-changing': item.type.startsWith('old') }">
              {{ getYaoType(item.coins).name }}
            </span>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="action-section">
        <button 
          v-if="!isComplete"
          class="btn-primary throw-btn"
          :disabled="!canThrow"
          @click="throwCoins"
        >
          <span v-if="isThrowingAnimation" class="throwing-text">
            <span class="coin-spin">🪙</span>
            掷卦中...
          </span>
          <span v-else>
            {{ showMeditationHint ? '开始掷卦' : '继续掷卦' }}
          </span>
        </button>

        <div v-else class="complete-section">
          <!-- 加载中 -->
          <div v-if="isSubmitting" class="loading-state">
            <div class="loading-bagua">☯</div>
            <span class="loading-text">正在解读卦象...</span>
            <span class="loading-hint">AI 大师正在为您推演</span>
          </div>
          
          <!-- 错误状态 -->
          <div v-else-if="errorMessage" class="error-state">
            <div class="error-icon">⚠️</div>
            <p class="error-text">{{ errorMessage }}</p>
            <button class="btn-primary retry-btn" @click="retrySubmit">
              <span>重新解卦</span>
            </button>
            <button class="btn-secondary back-home-btn" @click="goBack">
              返回重问
            </button>
          </div>
          
          <!-- 完成状态 -->
          <div v-else class="complete-message">
            <p class="complete-text">六爻已成，卦象已定</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.divine-page {
  min-height: 100vh;
  min-height: 100dvh;
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

/* ========== 神秘背景效果 ========== */
.mystic-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

/* 星星背景 */
.stars {
  position: absolute;
  inset: 0;
  background-image: 
    radial-gradient(2px 2px at 20px 30px, rgba(255, 255, 255, 0.3), transparent),
    radial-gradient(2px 2px at 40px 70px, rgba(212, 175, 55, 0.2), transparent),
    radial-gradient(1px 1px at 90px 40px, rgba(255, 255, 255, 0.2), transparent),
    radial-gradient(2px 2px at 130px 80px, rgba(212, 175, 55, 0.15), transparent),
    radial-gradient(1px 1px at 160px 120px, rgba(255, 255, 255, 0.25), transparent);
  background-size: 200px 200px;
  animation: twinkle 4s ease-in-out infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* 云雾效果 */
.mist {
  position: absolute;
  width: 100%;
  height: 100%;
  background: radial-gradient(ellipse at center, rgba(212, 175, 55, 0.05) 0%, transparent 70%);
}

.mist-1 {
  animation: mistFloat 20s ease-in-out infinite;
  transform-origin: 30% 30%;
}

.mist-2 {
  animation: mistFloat 25s ease-in-out infinite reverse;
  transform-origin: 70% 70%;
  opacity: 0.5;
}

@keyframes mistFloat {
  0%, 100% { transform: scale(1) translate(0, 0); }
  50% { transform: scale(1.2) translate(5%, 5%); }
}

/* 八卦水印 */
.bagua-watermark {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 30rem;
  color: rgba(212, 175, 55, 0.03);
  animation: slowRotate 120s linear infinite;
}

@keyframes slowRotate {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

/* 能量环 */
.energy-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border: 1px solid rgba(212, 175, 55, 0.1);
  border-radius: 50%;
  animation: ringPulse 4s ease-in-out infinite;
}

.ring-1 {
  width: 200px;
  height: 200px;
  animation-delay: 0s;
}

.ring-2 {
  width: 300px;
  height: 300px;
  animation-delay: 1s;
}

.ring-3 {
  width: 400px;
  height: 400px;
  animation-delay: 2s;
}

@keyframes ringPulse {
  0%, 100% { 
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.8);
  }
  50% { 
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
}

/* ========== 返回按钮 ========== */
.back-btn {
  position: relative;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  color: var(--color-text-secondary);
  padding: var(--spacing-sm);
  margin: 0 0 var(--spacing-md) calc(-1 * var(--spacing-sm));
  transition: color var(--transition-fast);
}

.back-btn:hover:not(:disabled) {
  color: var(--color-accent-gold);
}

.back-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ========== 页面内容 ========== */
.page-content {
  position: relative;
  z-index: 10;
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 500px;
  margin: 0 auto;
  width: 100%;
}

/* 问题展示 */
.question-display {
  text-align: center;
  padding: var(--spacing-md);
  background: rgba(212, 175, 55, 0.08);
  border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-lg);
  backdrop-filter: blur(10px);
}

.question-label {
  font-size: 0.75rem;
  color: var(--color-accent-gold);
  display: block;
  margin-bottom: var(--spacing-xs);
  letter-spacing: 0.1em;
}

.question-text {
  color: var(--color-text-primary);
  font-size: 1rem;
}

/* 进度区域 */
.progress-section {
  margin-bottom: var(--spacing-xl);
}

.progress-bar {
  height: 4px;
  background: rgba(212, 175, 55, 0.1);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: var(--spacing-sm);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-accent-gold-dark), var(--color-accent-gold));
  transition: width var(--transition-normal);
  box-shadow: 0 0 10px rgba(212, 175, 55, 0.5);
}

.progress-text {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  text-align: center;
  display: block;
}

/* ========== 铜钱区域 ========== */
.coin-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl) 0;
  min-height: 280px;
}

/* 冥想提示 */
.meditation-hint {
  text-align: center;
  animation: fadeIn 0.5s ease;
}

.hint-icon {
  font-size: 3rem;
  margin-bottom: var(--spacing-md);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.hint-text {
  color: var(--color-text-primary);
  font-size: 1.1rem;
  margin-bottom: var(--spacing-sm);
}

.hint-subtext {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

/* ========== 铜钱设计 - 古代方孔圆钱 ========== */
.coins-display {
  display: flex;
  gap: var(--spacing-xl);
  margin-bottom: var(--spacing-lg);
}

.coin {
  width: 90px;
  height: 90px;
  perspective: 1000px;
  filter: drop-shadow(0 10px 20px rgba(0, 0, 0, 0.4));
}

.coin-inner {
  width: 100%;
  height: 100%;
  position: relative;
  transform-style: preserve-3d;
  transition: transform 0.6s ease;
}

.coin.flipping .coin-inner {
  animation: coinFlip3D 0.4s ease infinite;
}

@keyframes coinFlip3D {
  0% { transform: rotateY(0deg) rotateX(0deg); }
  25% { transform: rotateY(90deg) rotateX(10deg); }
  50% { transform: rotateY(180deg) rotateX(0deg); }
  75% { transform: rotateY(270deg) rotateX(-10deg); }
  100% { transform: rotateY(360deg) rotateX(0deg); }
}

.coin.heads .coin-inner {
  transform: rotateY(0deg);
}

.coin.tails .coin-inner {
  transform: rotateY(180deg);
}

/* 铜钱正反面通用样式 */
.coin-front,
.coin-back {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  backface-visibility: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  /* 铜钱金属质感 */
  background: 
    radial-gradient(ellipse at 30% 30%, #c9a227 0%, transparent 50%),
    radial-gradient(ellipse at 70% 70%, #5c4a0f 0%, transparent 50%),
    linear-gradient(135deg, 
      #8b7355 0%, 
      #c9a227 15%, 
      #dfc47d 30%, 
      #c9a227 45%, 
      #8b6914 60%, 
      #5c4a0f 75%, 
      #8b6914 90%, 
      #c9a227 100%
    );
  box-shadow: 
    inset 0 3px 6px rgba(255, 255, 255, 0.3),
    inset 0 -3px 6px rgba(0, 0, 0, 0.4),
    0 2px 4px rgba(0, 0, 0, 0.3),
    0 0 20px rgba(212, 175, 55, 0.2);
}

/* 外圈 */
.coin-outer-ring {
  position: absolute;
  inset: 3px;
  border-radius: 50%;
  border: 2px solid rgba(92, 74, 15, 0.5);
  box-shadow: inset 0 0 3px rgba(0, 0, 0, 0.3);
}

/* 方孔 */
.coin-square-hole {
  position: absolute;
  width: 22px;
  height: 22px;
  background: linear-gradient(135deg, #1a1a2e 0%, #0d0d1a 100%);
  border: 2px solid #5c4a0f;
  box-shadow: 
    inset 0 2px 4px rgba(0, 0, 0, 0.8),
    0 1px 2px rgba(201, 162, 39, 0.3);
}

/* 正面文字 */
.coin-front .coin-text {
  position: absolute;
  font-size: 0.7rem;
  font-weight: bold;
  color: #3d2e0a;
  text-shadow: 0 1px 1px rgba(255, 255, 255, 0.3);
  font-family: 'Ma Shan Zheng', 'KaiTi', serif;
}

.coin-text.top { top: 10px; }
.coin-text.bottom { bottom: 10px; }
.coin-text.left { left: 12px; }
.coin-text.right { right: 12px; }

/* 反面 */
.coin-back {
  transform: rotateY(180deg);
}

.coin-back .coin-pattern {
  position: absolute;
  width: 60%;
  height: 60%;
  border: 1px solid rgba(92, 74, 15, 0.3);
  border-radius: 50%;
}

/* ========== 当前结果 ========== */
.current-result {
  text-align: center;
  animation: fadeIn 0.3s ease;
}

.result-coins {
  display: block;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
  margin-bottom: var(--spacing-sm);
}

.result-yao {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  color: var(--color-accent-gold);
  font-size: 1.2rem;
}

.yao-symbol {
  font-size: 1.5rem;
}

/* ========== 卦象预览 ========== */
.history-section {
  padding: var(--spacing-lg) 0;
}

.hexagram-preview {
  display: flex;
  flex-direction: column-reverse;
  gap: var(--spacing-sm);
  max-width: 280px;
  margin: 0 auto;
  padding: var(--spacing-md);
  background: rgba(0, 0, 0, 0.2);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(212, 175, 55, 0.1);
}

.yao-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  animation: fadeIn 0.3s ease;
}

.yao-position {
  width: 36px;
  font-size: 0.8rem;
  color: var(--color-text-muted);
  text-align: right;
}

.yao-visual {
  flex: 1;
  height: 10px;
  display: flex;
  align-items: center;
  position: relative;
}

.yao-bar {
  height: 100%;
  background: linear-gradient(90deg, 
    var(--color-accent-gold-dark), 
    var(--color-accent-gold), 
    var(--color-accent-gold-dark)
  );
  border-radius: 5px;
  box-shadow: 0 0 8px rgba(212, 175, 55, 0.4);
}

/* 阳爻：一条完整的线 */
.yao-visual.yang .yao-bar.full {
  flex: 1;
}

/* 阴爻：中间断开的两段线 */
.yao-visual.yin .yao-bar.left,
.yao-visual.yin .yao-bar.right {
  flex: 1;
}

.yao-gap {
  width: 20px;
  flex-shrink: 0;
}

/* 动爻标记 */
.yao-marker {
  position: absolute;
  right: -28px;
  font-size: 0.9rem;
  font-weight: bold;
}

.yao-marker.yang-marker {
  color: #ff6b6b;  /* 老阳用红色圆圈 */
  text-shadow: 0 0 6px rgba(255, 107, 107, 0.6);
}

.yao-marker.yin-marker {
  color: #4ecdc4;  /* 老阴用青色叉号 */
  text-shadow: 0 0 6px rgba(78, 205, 196, 0.6);
}

.yao-name {
  width: 50px;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  text-align: right;
}

/* 动爻名称高亮 */
.yao-name.is-changing {
  color: var(--color-accent-gold);
  font-weight: bold;
}

/* 动爻闪烁效果 */
.yao-row.changing .yao-bar {
  animation: glowPulse 1.5s ease-in-out infinite;
}

@keyframes glowPulse {
  0%, 100% { 
    box-shadow: 0 0 8px rgba(212, 175, 55, 0.4);
  }
  50% { 
    box-shadow: 0 0 20px rgba(212, 175, 55, 0.8);
  }
}

/* ========== 操作按钮 ========== */
.action-section {
  padding: var(--spacing-lg) 0;
}

.throw-btn {
  width: 100%;
  font-size: 1.1rem;
  padding: var(--spacing-md) var(--spacing-xl);
}

.throwing-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
}

.coin-spin {
  animation: spin 0.5s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ========== 完成区域 ========== */
.complete-section {
  text-align: center;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
}

.loading-bagua {
  font-size: 4rem;
  color: var(--color-accent-gold);
  animation: spinSlow 3s linear infinite;
  text-shadow: 0 0 30px rgba(212, 175, 55, 0.5);
}

@keyframes spinSlow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-text {
  color: var(--color-accent-gold);
  font-size: 1.1rem;
}

.loading-hint {
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

/* 错误状态 */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background: rgba(227, 66, 52, 0.1);
  border: 1px solid rgba(227, 66, 52, 0.3);
  border-radius: var(--radius-lg);
}

.error-icon {
  font-size: 2.5rem;
}

.error-text {
  color: #e34234;
  font-size: 0.95rem;
  text-align: center;
}

.retry-btn {
  width: 100%;
  max-width: 200px;
}

.back-home-btn {
  width: 100%;
  max-width: 200px;
  margin-top: var(--spacing-xs);
}

/* 完成消息 */
.complete-message {
  text-align: center;
}

.complete-text {
  color: var(--color-accent-gold);
  font-size: 1.1rem;
}

/* ========== 动画 ========== */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ========== 响应式 ========== */
@media (max-width: 480px) {
  .coin {
    width: 75px;
    height: 75px;
  }
  
  .coins-display {
    gap: var(--spacing-md);
  }
  
  .coin-text {
    font-size: 0.6rem !important;
  }
  
  .coin-square-hole {
    width: 18px;
    height: 18px;
  }
  
  .bagua-watermark {
    font-size: 20rem;
  }
}
</style>
