/**
 * API 服务层
 */
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,  // 120秒超时，AI 生成可能需要较长时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export interface DivinationMethod {
  id: string
  name: string
  description: string
  icon: string
  available: boolean
}

export interface AIModel {
  id: string
  name: string
  description: string
  icon: string
  default: boolean
}

export interface LiuYaoLine {
  value: number
  type: string
  name: string
  symbol: string
  number: number
  changing: boolean
  changedValue: number
  position: number
  positionName: string
}

export interface Trigram {
  name: string
  symbol: string
  nature: string
  attribute: string
}

export interface Hexagram {
  name: string
  number: number
  judgment: string
  lowerTrigram: Trigram
  upperTrigram: Trigram
  lines: number[]
}

export interface A2UIResponse {
  version: string
  root: string
  components: any[]
  data?: {
    question?: string
    originalHexagram?: Hexagram
    changedHexagram?: Hexagram
    lines?: LiuYaoLine[]
    interpretation?: string
    sections?: Record<string, string>
  }
  metadata?: {
    hexagramName?: string
    question?: string
    generatedBy?: string
    isNativeA2UI?: boolean
    title?: string
    generatedAt?: string
    method?: string
  }
}

export interface LiuYaoResult {
  success: boolean
  originalHexagram: Hexagram
  changedHexagram?: Hexagram
  lines: LiuYaoLine[]
  a2uiResponse: A2UIResponse
  model: string  // 使用的 AI 模型
}

/**
 * 获取占卜方式列表
 */
export async function getDivinationMethods(): Promise<DivinationMethod[]> {
  return api.get('/divination/methods')
}

/**
 * 获取可用的 AI 模型列表
 */
export async function getAIModels(): Promise<AIModel[]> {
  return api.get('/divination/models')
}

/**
 * 六爻占卜
 */
export async function liuyaoDivination(
  question: string,
  coinResults: number[][],
  model?: string
): Promise<LiuYaoResult> {
  return api.post('/divination/liuyao', {
    question,
    coin_results: coinResults,
    model: model || undefined
  })
}

export default api

