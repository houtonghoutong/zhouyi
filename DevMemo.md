# 开发备忘录

记录开发过程中遇到的问题及解决方案。

---

## 2026-01-03 多模型支持实现

### 问题描述
用户希望支持多个 AI 模型，可以在前端选择使用 Gemini 或 DeepSeek。

### 架构设计

**服务层抽象**:
```
BaseAIService (基类)
├── GeminiService (Google Gemini)
└── DeepSeekService (DeepSeek - OpenAI 兼容接口)
```

**工厂模式**:
```python
class AIServiceFactory:
    _services = {
        "gemini": GeminiService,
        "deepseek": DeepSeekService,
    }
    
    @classmethod
    def get_service(cls, model_name: str) -> BaseAIService:
        return cls._services[model_name]()
```

### DeepSeek 集成要点

DeepSeek 使用 OpenAI 兼容接口，可直接用 `openai` 库：

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[...],
    temperature=0.7
)
```

### 前端模型选择

```vue
<div class="model-grid">
  <button
    v-for="model in store.availableModels"
    :key="model.id"
    :class="{ active: store.selectedModel === model.id }"
    @click="selectModel(model.id)"
  >
    <span class="model-icon">{{ model.icon }}</span>
    <span class="model-name">{{ model.name }}</span>
  </button>
</div>
```

### 日志命名规则

文件名增加模型标识：
```
YYYYMMDD_HHMMSS_卦名_模型.md
例: 20260103_210409_山泽损_deepseek.md
```

---

## 2025-12-31 真正的 A2UI 标准实现

### A2UI 是什么

A2UI (Agent-to-User Interface) 是一个开放标准，允许智能体"用语言描述用户界面"。核心流程：

```
生成(LLM) → 传输(JSON) → 解析(客户端) → 渲染(原生组件映射)
```

### 关键要点

| 项目 | 伪 A2UI | 真正的 A2UI |
|------|---------|-------------|
| JSON 生成者 | 后端代码手动构建 | **LLM 直接输出** |
| 组件结构 | 固定模板 | **LLM 动态决定** |
| 前端渲染 | 只读固定字段 | **解析任意组件** |

### 实现方式

**1. Prompt 让 Gemini 直接输出 A2UI JSON**

```python
prompt = """
请直接输出一个有效的 JSON 对象，格式如下：
{
  "version": "1.0",
  "components": [
    { "id": "card-overview", "type": "card", "props": {...}, "children": [...] },
    { "id": "badge-fortune", "type": "badge", "props": { "label": "中吉", "color": "success" } },
    { "id": "list-advice", "type": "list", "props": { "items": [...], "ordered": true } }
  ]
}
"""
```

**2. 后端直接解析 Gemini 返回的 JSON**

```python
def _parse_a2ui_response(self, raw_response: str, ...) -> Dict:
    # 移除 markdown 代码块标记
    json_str = raw_response.strip()
    if json_str.startswith("```json"):
        json_str = json_str[7:].strip()
    # 直接解析 JSON
    a2ui_data = json.loads(json_str)
    return a2ui_data
```

**3. 前端动态渲染任意 A2UI 组件**

```vue
<template v-for="component in rootComponents">
  <div v-if="component.type === 'card'" class="a2ui-card">
    <h3>{{ component.props?.title }}</h3>
    <template v-for="child in getChildren(component)">
      <p v-if="child.type === 'text'">{{ child.props?.content }}</p>
      <span v-else-if="child.type === 'badge'" :class="getBadgeClass(child.props?.color)">
        {{ child.props?.label }}
      </span>
      <ol v-else-if="child.type === 'list'">
        <li v-for="item in child.props?.items">{{ item }}</li>
      </ol>
    </template>
  </div>
</template>
```

### 支持的组件类型

- `card` - 卡片容器（支持 elevated/highlighted/warning 变体）
- `text` - 文本内容（支持 body/caption 样式）
- `badge` - 徽章标签（支持 success/warning/error/info 颜色）
- `list` - 列表组件（支持有序/无序）
- `container` - 布局容器（支持 horizontal/vertical）

---

## 2025-12-31 AI 交互日志功能

### 功能说明
每次调用 Gemini API 时，自动保存完整的输入输出日志，方便调试和分析。

### 日志位置
`backend/logs/ai_interactions/YYYYMMDD_HHMMSS_卦名.json`

### 日志结构

```json
{
  "metadata": {
    "timestamp": "2025-12-31T17:35:55.087090",
    "timestamp_readable": "2025年12月31日 17:35:55",
    "success": true,
    "error_message": null
  },
  "input": {
    "question": "用户问题",
    "original_hexagram": { ... },
    "changed_hexagram": { ... },
    "lines": [ ... ],
    "prompt": "完整的 Gemini prompt"
  },
  "output": {
    "raw_response": "AI 原始响应文本",
    "parsed_sections": { ... },
    "a2ui_response": { ... }
  }
}
```

### 关键代码

```python
# 在 GeminiService 类中添加日志保存方法
def _save_interaction_log(
    self,
    question: str,
    original_hexagram: Dict,
    # ...更多参数
):
    timestamp = datetime.now()
    log_filename = timestamp.strftime("%Y%m%d_%H%M%S") + f"_{original_hexagram.get('name', 'unknown')}.json"
    log_path = self.LOG_DIR / log_filename
    # 保存 JSON 文件
```

---

## 2025-12-31 snake_case vs camelCase 数据格式问题

### 问题描述
前端结果页显示"未知卦"，即使后端返回了正确的卦象数据。

### 原因分析
- Python/FastAPI 后端默认使用 `snake_case` 命名（如 `original_hexagram`）
- Vue/TypeScript 前端期望 `camelCase` 命名（如 `originalHexagram`）
- Pydantic 模型直接返回时使用了 Python 属性名，导致 JSON 字段名不匹配

### 解决方案
在 Pydantic 响应模型中使用 `Field` 的 `alias` 参数：

```python
from pydantic import BaseModel, Field

class LiuYaoResponse(BaseModel):
    success: bool
    original_hexagram: dict = Field(..., alias="originalHexagram")
    changed_hexagram: Optional[dict] = Field(None, alias="changedHexagram")
    # ...
    
    class Config:
        populate_by_name = True  # 允许通过别名赋值
```

返回时使用别名：
```python
return LiuYaoResponse(
    success=True,
    originalHexagram=hexagram_result["original_hexagram"],  # 使用别名
    # ...
)
```

### 经验总结
- 前后端数据交互时，务必统一字段命名规范
- 推荐在 API 边界使用 `camelCase`（JavaScript 惯例）
- 后端内部逻辑保持 `snake_case`（Python 惯例）
- Pydantic 的 `alias` 功能可优雅解决此问题

---

## 2025-12-31 项目初始化

### 技术选型
- 前端：Vue 3 + TypeScript + Vite
- 后端：Python FastAPI
- AI：Google Gemini API + A2UI
- 存储：LocalStorage（本地存储，无需用户登录）

### A2UI 说明
A2UI（Agent-to-User Interface）是 Google 开源的项目，允许 AI Agent 生成动态 UI。
- GitHub: https://github.com/google/A2UI
- 核心理念：声明式 JSON 格式描述 UI，客户端负责渲染
- 安全：数据格式而非可执行代码
- LLM 友好：支持增量更新

### 六爻占卜规则
1. 掷铜钱6次，每次3枚
2. 记录每次结果：
   - 3正0反 = 老阳（变爻）⚊ → ⚋
   - 2正1反 = 少阳 ⚊
   - 1正2反 = 少阴 ⚋
   - 0正3反 = 老阴（变爻）⚋ → ⚊
3. 从下往上排列，形成本卦
4. 如有变爻，生成变卦
5. 根据卦象进行解读

---

