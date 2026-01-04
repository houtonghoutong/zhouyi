/**
 * 占卜状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { LiuYaoResult, AIModel } from '@/services/api'

// 默认 AI 模型
const DEFAULT_MODEL = 'gemini'

export const useDivinationStore = defineStore('divination', () => {
  // 六爻占卜状态
  const question = ref('')
  const coinResults = ref<number[][]>([])
  const currentThrow = ref(0)
  const result = ref<LiuYaoResult | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  
  // AI 模型选择
  const selectedModel = ref(localStorage.getItem('zhouyi_ai_model') || DEFAULT_MODEL)
  const availableModels = ref<AIModel[]>([])

  /**
   * 设置问题
   */
  function setQuestion(q: string) {
    question.value = q
  }

  /**
   * 添加一次掷铜钱结果
   */
  function addCoinResult(coins: number[]) {
    if (coinResults.value.length < 6) {
      coinResults.value.push(coins)
      currentThrow.value = coinResults.value.length
    }
  }

  /**
   * 设置占卜结果
   */
  function setResult(r: LiuYaoResult) {
    result.value = r
  }

  /**
   * 设置加载状态
   */
  function setLoading(loading: boolean) {
    isLoading.value = loading
  }

  /**
   * 设置错误信息
   */
  function setError(err: string | null) {
    error.value = err
  }

  /**
   * 重置占卜状态
   */
  function reset() {
    question.value = ''
    coinResults.value = []
    currentThrow.value = 0
    result.value = null
    isLoading.value = false
    error.value = null
  }

  /**
   * 设置选中的 AI 模型
   */
  function setSelectedModel(model: string) {
    selectedModel.value = model
    localStorage.setItem('zhouyi_ai_model', model)
  }

  /**
   * 设置可用模型列表
   */
  function setAvailableModels(models: AIModel[]) {
    availableModels.value = models
  }

  /**
   * 保存到本地存储
   */
  function saveToLocal() {
    if (result.value) {
      const history = getHistory()
      const record = {
        id: Date.now().toString(),
        question: question.value,
        result: result.value,
        createdAt: new Date().toISOString()
      }
      history.unshift(record)
      // 最多保存 50 条记录
      if (history.length > 50) {
        history.pop()
      }
      localStorage.setItem('zhouyi_history', JSON.stringify(history))
    }
  }

  /**
   * 获取历史记录
   */
  function getHistory(): Array<{
    id: string
    question: string
    result: LiuYaoResult
    createdAt: string
  }> {
    const historyStr = localStorage.getItem('zhouyi_history')
    return historyStr ? JSON.parse(historyStr) : []
  }

  return {
    question,
    coinResults,
    currentThrow,
    result,
    isLoading,
    error,
    selectedModel,
    availableModels,
    setQuestion,
    addCoinResult,
    setResult,
    setLoading,
    setError,
    reset,
    setSelectedModel,
    setAvailableModels,
    saveToLocal,
    getHistory
  }
})

