<script setup lang="ts">
/**
 * 卦象可视化组件
 * 展示卦象图形和基本信息
 */
import { computed } from 'vue'

interface Trigram {
  name: string
  symbol: string
  nature: string
  attribute: string
}

interface Hexagram {
  name: string
  number: number
  judgment: string
  lowerTrigram: Trigram
  upperTrigram: Trigram
  lines: number[]
}

interface Line {
  value: number
  changing: boolean
  position: number
  positionName: string
  name: string
  symbol: string
}

const props = defineProps<{
  lines: Line[]
  originalHexagram?: Hexagram
  changedHexagram?: Hexagram
}>()

// 爻位名称
const lineNames = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻']

// 反转显示（从上到下）
const displayLines = computed(() => {
  return [...props.lines].reverse()
})

// 是否有变卦
const hasChanged = computed(() => !!props.changedHexagram)
</script>

<template>
  <div class="hexagram-visual">
    <!-- 卦名展示 -->
    <div class="hexagram-names">
      <div class="hexagram-name original">
        <span class="name-label">本卦</span>
        <span class="name-value title-brush">{{ originalHexagram?.name || '未知卦' }}</span>
      </div>
      <div v-if="hasChanged" class="hexagram-arrow">→</div>
      <div v-if="hasChanged" class="hexagram-name changed">
        <span class="name-label">变卦</span>
        <span class="name-value title-brush">{{ changedHexagram?.name }}</span>
      </div>
    </div>

    <!-- 卦象图形 -->
    <div class="hexagram-diagram">
      <!-- 本卦 -->
      <div class="hexagram-box">
        <div class="trigram-label upper">{{ originalHexagram?.upperTrigram?.name }}（{{ originalHexagram?.upperTrigram?.symbol }}）</div>
        <div class="yao-lines">
          <div 
            v-for="(line, index) in displayLines" 
            :key="index"
            class="yao-row"
          >
            <span class="yao-position">{{ lineNames[5 - index] }}</span>
            <div 
              class="yao-line"
              :class="{ 
                yang: line.value === 1, 
                yin: line.value === 0,
                changing: line.changing
              }"
            >
              <div class="line-bar"></div>
              <span v-if="line.changing" class="changing-mark">○</span>
            </div>
          </div>
        </div>
        <div class="trigram-label lower">{{ originalHexagram?.lowerTrigram?.name }}（{{ originalHexagram?.lowerTrigram?.symbol }}）</div>
      </div>

      <!-- 变卦（如有） -->
      <div v-if="hasChanged" class="hexagram-box changed-box">
        <div class="trigram-label upper">{{ changedHexagram?.upperTrigram?.name }}（{{ changedHexagram?.upperTrigram?.symbol }}）</div>
        <div class="yao-lines">
          <div 
            v-for="(line, index) in displayLines" 
            :key="`changed-${index}`"
            class="yao-row"
          >
            <div 
              class="yao-line"
              :class="{ 
                yang: line.changing ? (line.value === 0) : (line.value === 1), 
                yin: line.changing ? (line.value === 1) : (line.value === 0)
              }"
            >
              <div class="line-bar"></div>
            </div>
          </div>
        </div>
        <div class="trigram-label lower">{{ changedHexagram?.lowerTrigram?.name }}（{{ changedHexagram?.lowerTrigram?.symbol }}）</div>
      </div>
    </div>

    <!-- 卦辞 -->
    <div class="hexagram-judgment">
      <div class="judgment-item">
        <span class="judgment-label">本卦卦辞</span>
        <span class="judgment-text">{{ originalHexagram?.judgment || '—' }}</span>
      </div>
      <div v-if="hasChanged" class="judgment-item">
        <span class="judgment-label">变卦卦辞</span>
        <span class="judgment-text">{{ changedHexagram?.judgment }}</span>
      </div>
    </div>

    <!-- 卦象属性 -->
    <div class="hexagram-attributes">
      <div class="attribute-row">
        <div class="attribute-item">
          <span class="attr-label">上卦</span>
          <span class="attr-value">{{ originalHexagram?.upperTrigram?.name }} · {{ originalHexagram?.upperTrigram?.nature }}</span>
        </div>
        <div class="attribute-item">
          <span class="attr-label">下卦</span>
          <span class="attr-value">{{ originalHexagram?.lowerTrigram?.name }} · {{ originalHexagram?.lowerTrigram?.nature }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.hexagram-visual {
  text-align: center;
}

/* 卦名 */
.hexagram-names {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.hexagram-name {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.name-label {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin-bottom: var(--spacing-xs);
}

.name-value {
  font-size: 1.8rem;
  color: var(--color-accent-gold);
}

.hexagram-arrow {
  font-size: 1.5rem;
  color: var(--color-accent-gold);
  opacity: 0.6;
}

/* 卦象图形 */
.hexagram-diagram {
  display: flex;
  justify-content: center;
  gap: var(--spacing-xl);
  margin-bottom: var(--spacing-xl);
}

.hexagram-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-md);
  background: rgba(212, 175, 55, 0.05);
  border-radius: var(--radius-md);
  min-width: 150px;
}

.trigram-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.trigram-label.upper {
  margin-bottom: var(--spacing-sm);
}

.trigram-label.lower {
  margin-top: var(--spacing-sm);
}

.yao-lines {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.yao-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.yao-position {
  width: 40px;
  font-size: 0.7rem;
  color: var(--color-text-muted);
  text-align: right;
}

.changed-box .yao-row {
  justify-content: center;
}

.yao-line {
  width: 80px;
  height: 12px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.line-bar {
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, var(--color-accent-gold-dark), var(--color-accent-gold), var(--color-accent-gold-dark));
  border-radius: 6px;
  position: relative;
}

.yao-line.yin .line-bar::after {
  content: '';
  position: absolute;
  left: 50%;
  top: 0;
  width: 20%;
  height: 100%;
  background: var(--color-bg-card);
  transform: translateX(-50%);
}

.yao-line.changing .line-bar {
  animation: pulse 1.5s ease-in-out infinite;
}

.changing-mark {
  position: absolute;
  right: -20px;
  font-size: 0.8rem;
  color: var(--color-cinnabar);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 卦辞 */
.hexagram-judgment {
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-md);
  background: rgba(212, 175, 55, 0.05);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--color-accent-gold);
}

.judgment-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-bottom: var(--spacing-sm);
}

.judgment-item:last-child {
  margin-bottom: 0;
}

.judgment-label {
  font-size: 0.75rem;
  color: var(--color-accent-gold);
  margin-bottom: var(--spacing-xs);
}

.judgment-text {
  font-size: 0.95rem;
  color: var(--color-text-primary);
  text-align: left;
}

/* 卦象属性 */
.hexagram-attributes {
  text-align: left;
}

.attribute-row {
  display: flex;
  gap: var(--spacing-lg);
}

.attribute-item {
  display: flex;
  gap: var(--spacing-sm);
  font-size: 0.85rem;
}

.attr-label {
  color: var(--color-text-muted);
}

.attr-value {
  color: var(--color-text-secondary);
}

/* 响应式 */
@media (max-width: 480px) {
  .hexagram-diagram {
    flex-direction: column;
    align-items: center;
  }
  
  .hexagram-names {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
  
  .hexagram-arrow {
    transform: rotate(90deg);
  }
  
  .name-value {
    font-size: 1.5rem;
  }
  
  .attribute-row {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
}
</style>

