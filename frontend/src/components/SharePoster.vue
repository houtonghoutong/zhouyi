<script setup lang="ts">
/**
 * 分享海报组件
 * 生成精美的分享图片，包含卦象结果和二维码
 */
import { ref, onMounted, watch } from 'vue'
import html2canvas from 'html2canvas'
import QRCode from 'qrcode'

interface Props {
  visible: boolean
  hexagramName: string
  changedHexagramName?: string
  question: string
  fortune: string  // 吉凶判断
  fortuneType: 'success' | 'warning' | 'error'  // 吉凶类型
  upperTrigram: string
  lowerTrigram: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
}>()

const posterRef = ref<HTMLElement | null>(null)
const qrcodeDataUrl = ref('')
const isGenerating = ref(false)
const generatedImageUrl = ref('')
const showSaveHint = ref(false)

// 应用访问地址
const APP_URL = 'http://223.109.142.31:8866'

// 生成二维码
async function generateQRCode() {
  try {
    qrcodeDataUrl.value = await QRCode.toDataURL(APP_URL, {
      width: 120,
      margin: 1,
      color: {
        dark: '#1a1a2e',
        light: '#ffffff'
      }
    })
  } catch (error) {
    console.error('生成二维码失败:', error)
  }
}

// 生成海报图片
async function generatePoster() {
  if (!posterRef.value || isGenerating.value) return
  
  isGenerating.value = true
  
  try {
    const canvas = await html2canvas(posterRef.value, {
      scale: 2,  // 高清
      backgroundColor: '#0d0d1a',
      useCORS: true,
      logging: false
    })
    
    generatedImageUrl.value = canvas.toDataURL('image/png')
    showSaveHint.value = true
  } catch (error) {
    console.error('生成海报失败:', error)
  } finally {
    isGenerating.value = false
  }
}

// 关闭弹窗
function close() {
  generatedImageUrl.value = ''
  showSaveHint.value = false
  emit('close')
}

// 获取吉凶对应的颜色
function getFortuneColor(type: string): string {
  const colors: Record<string, string> = {
    success: '#00a86b',
    warning: '#ffc107',
    error: '#e34234'
  }
  return colors[type] || '#d4af37'
}

// 获取引导语
function getTagline(): string {
  const taglines = [
    '古老智慧，指引迷津',
    '问苍天，知天命',
    '心诚则灵，卦有定数',
    '天机可测，运势可知'
  ]
  return taglines[Math.floor(Math.random() * taglines.length)]
}

// 监听显示状态
watch(() => props.visible, async (visible) => {
  if (visible) {
    await generateQRCode()
    // 等待 DOM 渲染完成后生成海报
    setTimeout(() => {
      generatePoster()
    }, 300)
  }
})

onMounted(() => {
  if (props.visible) {
    generateQRCode()
  }
})
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="share-modal" @click.self="close">
        <div class="modal-content">
          <!-- 关闭按钮 -->
          <button class="close-btn" @click="close">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
          
          <!-- 海报预览/生成的图片 -->
          <div class="poster-wrapper">
            <!-- 生成的图片 -->
            <img 
              v-if="generatedImageUrl" 
              :src="generatedImageUrl" 
              class="generated-poster"
              alt="分享海报"
            />
            
            <!-- 海报模板（用于生成图片） -->
            <div 
              v-show="!generatedImageUrl"
              ref="posterRef" 
              class="poster"
            >
              <!-- 背景装饰 -->
              <div class="poster-bg">
                <div class="bg-pattern"></div>
                <div class="bg-glow"></div>
              </div>
              
              <!-- 顶部：应用标识 -->
              <header class="poster-header">
                <div class="app-logo">☯</div>
                <h1 class="app-title">周易占卜</h1>
                <p class="app-tagline">{{ getTagline() }}</p>
              </header>
              
              <!-- 中间：卦象信息 -->
              <main class="poster-main">
                <!-- 卦象名称 -->
                <div class="hexagram-info">
                  <div class="hexagram-name">
                    <span class="name-text">{{ hexagramName }}</span>
                    <template v-if="changedHexagramName">
                      <span class="arrow">→</span>
                      <span class="name-text changed">{{ changedHexagramName }}</span>
                    </template>
                  </div>
                  <div class="trigram-info">
                    上卦 {{ upperTrigram }} · 下卦 {{ lowerTrigram }}
                  </div>
                </div>
                
                <!-- 用户问题 -->
                <div class="question-box">
                  <div class="question-label">所问之事</div>
                  <div class="question-text">"{{ question }}"</div>
                </div>
                
                <!-- 吉凶判断 -->
                <div class="fortune-box">
                  <div class="fortune-label">卦象启示</div>
                  <div 
                    class="fortune-result"
                    :style="{ color: getFortuneColor(fortuneType) }"
                  >
                    {{ fortune }}
                  </div>
                </div>
              </main>
              
              <!-- 底部：引导 + 二维码 -->
              <footer class="poster-footer">
                <div class="cta-section">
                  <p class="cta-text">✨ 测测你的运势 ✨</p>
                  <p class="cta-sub">长按识别二维码，开启你的命运之旅</p>
                </div>
                
                <div class="qrcode-section">
                  <div class="qrcode-wrapper">
                    <img v-if="qrcodeDataUrl" :src="qrcodeDataUrl" class="qrcode" alt="二维码" />
                  </div>
                  <p class="qrcode-hint">长按识别</p>
                </div>
              </footer>
            </div>
          </div>
          
          <!-- 保存提示 -->
          <div v-if="showSaveHint" class="save-hint">
            <div class="hint-icon">📱</div>
            <p class="hint-text">长按图片保存到相册</p>
            <p class="hint-sub">发送给好友或分享到朋友圈</p>
          </div>
          
          <!-- 加载状态 -->
          <div v-if="isGenerating" class="loading-overlay">
            <div class="loading-spinner">☯</div>
            <p>正在生成海报...</p>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
/* 弹窗背景 */
.share-modal {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  padding: 1rem;
}

/* 弹窗内容 */
.modal-content {
  position: relative;
  max-width: 400px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

/* 关闭按钮 */
.close-btn {
  position: absolute;
  top: -40px;
  right: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  color: #fff;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* 海报容器 */
.poster-wrapper {
  width: 100%;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.generated-poster {
  width: 100%;
  display: block;
}

/* 海报模板 */
.poster {
  position: relative;
  width: 100%;
  aspect-ratio: 9 / 16;
  background: linear-gradient(180deg, #0d0d1a 0%, #1a1a2e 50%, #0d0d1a 100%);
  padding: 2rem 1.5rem;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 背景装饰 */
.poster-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.bg-pattern {
  position: absolute;
  inset: 0;
  background-image: 
    radial-gradient(circle at 20% 30%, rgba(212, 175, 55, 0.08) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(212, 175, 55, 0.05) 0%, transparent 40%);
}

.bg-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 300px;
  height: 300px;
  transform: translate(-50%, -50%);
  background: radial-gradient(circle, rgba(212, 175, 55, 0.1) 0%, transparent 70%);
  filter: blur(40px);
}

/* 顶部 */
.poster-header {
  position: relative;
  text-align: center;
  margin-bottom: 1.5rem;
}

.app-logo {
  font-size: 3rem;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #d4af37, #f4d03f);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 2px 10px rgba(212, 175, 55, 0.5));
}

.app-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: #d4af37;
  margin: 0 0 0.25rem;
  letter-spacing: 0.3em;
  text-shadow: 0 2px 10px rgba(212, 175, 55, 0.3);
}

.app-tagline {
  font-size: 0.85rem;
  color: rgba(212, 175, 55, 0.7);
  margin: 0;
  letter-spacing: 0.1em;
}

/* 中间内容 */
.poster-main {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* 卦象信息 */
.hexagram-info {
  text-align: center;
}

.hexagram-name {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.name-text {
  font-size: 2rem;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 2px 15px rgba(255, 255, 255, 0.2);
}

.name-text.changed {
  color: #d4af37;
}

.arrow {
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.5);
}

.trigram-info {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 0.1em;
}

/* 问题框 */
.question-box {
  background: rgba(212, 175, 55, 0.08);
  border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: 12px;
  padding: 1rem;
  text-align: center;
}

.question-label {
  font-size: 0.75rem;
  color: #d4af37;
  margin-bottom: 0.5rem;
  letter-spacing: 0.1em;
}

.question-text {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.5;
  font-style: italic;
}

/* 吉凶框 */
.fortune-box {
  text-align: center;
  padding: 1rem;
}

.fortune-label {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 0.75rem;
  letter-spacing: 0.15em;
}

.fortune-result {
  font-size: 2.5rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-shadow: 0 4px 20px currentColor;
}

/* 底部 */
.poster-footer {
  position: relative;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid rgba(212, 175, 55, 0.15);
}

.cta-section {
  flex: 1;
}

.cta-text {
  font-size: 1rem;
  color: #d4af37;
  margin: 0 0 0.25rem;
  font-weight: 600;
}

.cta-sub {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
  line-height: 1.4;
}

.qrcode-section {
  text-align: center;
}

.qrcode-wrapper {
  width: 80px;
  height: 80px;
  background: #fff;
  border-radius: 8px;
  padding: 4px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.qrcode {
  width: 100%;
  height: 100%;
  display: block;
}

.qrcode-hint {
  font-size: 0.65rem;
  color: rgba(255, 255, 255, 0.5);
  margin: 0.5rem 0 0;
}

/* 保存提示 */
.save-hint {
  text-align: center;
  padding: 1rem;
  background: rgba(212, 175, 55, 0.1);
  border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: 12px;
  width: 100%;
}

.hint-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.hint-text {
  color: #d4af37;
  font-size: 1rem;
  margin: 0 0 0.25rem;
  font-weight: 600;
}

.hint-sub {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85rem;
  margin: 0;
}

/* 加载状态 */
.loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(13, 13, 26, 0.9);
  color: #d4af37;
  gap: 1rem;
}

.loading-spinner {
  font-size: 3rem;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 动画 */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: scale(0.9);
}
</style>

