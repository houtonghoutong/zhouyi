"""
AI 服务基类

定义 AI 服务的通用接口，支持多模型切换
"""
import os
import json
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class BaseAIService(ABC):
    """AI 服务基类"""
    
    # 日志目录
    LOG_DIR = Path(__file__).parent.parent.parent / "logs" / "ai_interactions"
    
    # 模型名称（子类需要设置）
    MODEL_NAME = "unknown"
    MODEL_DISPLAY_NAME = "未知模型"
    
    def __init__(self):
        """初始化服务"""
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    async def generate_liuyao_interpretation(
        self,
        question: str,
        original_hexagram: Dict,
        changed_hexagram: Optional[Dict],
        lines: list
    ) -> Dict:
        """
        生成六爻占卜的 AI 解读，返回 A2UI 格式
        
        参数：
            question: 用户的问题
            original_hexagram: 本卦信息
            changed_hexagram: 变卦信息（可选）
            lines: 六爻详情
        
        返回：
            A2UI 格式的动态 UI 数据
        """
        pass
    
    def _save_interaction_log(
        self,
        question: str,
        original_hexagram: Dict,
        changed_hexagram: Optional[Dict],
        lines: list,
        prompt: str,
        raw_response: str,
        parsed_sections: Dict,
        a2ui_response: Dict,
        success: bool,
        error_message: str = None
    ):
        """
        保存 AI 交互日志为 Markdown 文件
        """
        timestamp = datetime.now()
        log_filename = timestamp.strftime("%Y%m%d_%H%M%S") + f"_{original_hexagram.get('name', 'unknown')}_{self.MODEL_NAME}.md"
        log_path = self.LOG_DIR / log_filename
        
        # 构建 Markdown 内容
        md_content = f"""# AI 交互日志

## 元信息

| 项目 | 内容 |
|------|------|
| **时间** | {timestamp.strftime("%Y年%m月%d日 %H:%M:%S")} |
| **状态** | {"✅ 成功" if success else "❌ 失败"} |
| **模型** | {self.MODEL_DISPLAY_NAME} |
| **卦名** | {original_hexagram.get("name", "未知")} |
{"| **错误信息** | " + error_message + " |" if error_message else ""}

---

## 输入参数

### 用户问题

> {question}

### 本卦信息

| 项目 | 内容 |
|------|------|
| **卦名** | {original_hexagram.get("name")} |
| **卦序** | 第 {original_hexagram.get("number")} 卦 |
| **卦辞** | {original_hexagram.get("judgment")} |
| **上卦** | {original_hexagram.get("upperTrigram", {}).get("name")}（{original_hexagram.get("upperTrigram", {}).get("symbol")}）- {original_hexagram.get("upperTrigram", {}).get("nature")} |
| **下卦** | {original_hexagram.get("lowerTrigram", {}).get("name")}（{original_hexagram.get("lowerTrigram", {}).get("symbol")}）- {original_hexagram.get("lowerTrigram", {}).get("nature")} |

"""
        
        # 变卦信息（如果有）
        if changed_hexagram:
            md_content += f"""### 变卦信息

| 项目 | 内容 |
|------|------|
| **卦名** | {changed_hexagram.get("name")} |
| **卦序** | 第 {changed_hexagram.get("number")} 卦 |
| **卦辞** | {changed_hexagram.get("judgment")} |

"""
        
        # 六爻详情
        md_content += """### 六爻详情

| 位置 | 名称 | 符号 | 变爻 |
|------|------|------|------|
"""
        for line in lines:
            changing_mark = "🔄 是" if line.get("changing") else "否"
            md_content += f"| {line.get('positionName')} | {line.get('name')} | {line.get('symbol')} | {changing_mark} |\n"
        
        # Prompt
        md_content += f"""
### 发送给 {self.MODEL_DISPLAY_NAME} 的 Prompt

```
{prompt}
```

---

## 输出结果

### {self.MODEL_DISPLAY_NAME} 原始响应

```
{raw_response}
```

### 解析后的内容

"""
        
        # 解析后的 sections
        for title, content in parsed_sections.items():
            md_content += f"""#### {title}

{content}

"""
        
        # A2UI Response（JSON 格式）
        md_content += f"""### A2UI Response (JSON)

```json
{json.dumps(a2ui_response, ensure_ascii=False, indent=2)}
```

---

*日志生成时间: {timestamp.isoformat()}*
"""
        
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            print(f"[LOG] AI 交互日志已保存: {log_path}")
        except Exception as e:
            print(f"[ERROR] 保存 AI 交互日志失败: {e}")
    
    def _build_a2ui_prompt(
        self,
        question: str,
        original_hexagram: Dict,
        changed_hexagram: Optional[Dict],
        lines: list
    ) -> str:
        """
        构建 A2UI 格式的 Prompt
        
        让 AI 直接输出 A2UI 声明式 JSON 格式
        """
        
        # 构建变爻信息
        changing_lines = [line for line in lines if line.get("changing")]
        changing_info = ""
        if changing_lines:
            changing_positions = [line["positionName"] for line in changing_lines]
            changing_info = f"变爻位置：{', '.join(changing_positions)}"
        
        # 构建变卦信息
        changed_info = ""
        if changed_hexagram:
            changed_info = f"""
变卦：{changed_hexagram['name']}
变卦卦辞：{changed_hexagram.get('judgment', '')}
"""
        
        # 六爻信息
        lines_info = "\n".join([
            f"{'初' if i == 0 else ['二', '三', '四', '五', '上'][i-1] if i < 6 else ''}爻：{lines[i]['name']}（{lines[i]['symbol']}）{'【变爻】' if lines[i]['changing'] else ''}"
            for i in range(6)
        ])
        
        prompt = f"""你是一位精通周易的占卜大师。请为求卦者解读卦象，并直接输出 A2UI 格式的 JSON。

## 卦象信息

**求卦者的问题**：{question}

**本卦**：{original_hexagram['name']}
**卦辞**：{original_hexagram.get('judgment', '')}
**上卦**：{original_hexagram['upperTrigram']['name']}（{original_hexagram['upperTrigram']['symbol']}，{original_hexagram['upperTrigram']['nature']}）
**下卦**：{original_hexagram['lowerTrigram']['name']}（{original_hexagram['lowerTrigram']['symbol']}，{original_hexagram['lowerTrigram']['nature']}）

**六爻详情**：
{lines_info}

{changing_info}
{changed_info}

## A2UI 输出要求

请直接输出一个有效的 JSON 对象，格式如下。注意：
1. 只输出 JSON，不要有任何其他文字
2. JSON 必须合法，可以被直接解析
3. 内容要用大白话，通俗易懂，像长辈跟晚辈聊天一样
4. 每个 card 的内容要详细，不要太简短

```json
{{
  "version": "1.0",
  "root": "interpretation-root",
  "components": [
    {{
      "id": "card-overview",
      "type": "card",
      "props": {{
        "title": "📖 卦象总论",
        "variant": "elevated"
      }},
      "children": ["text-overview"]
    }},
    {{
      "id": "text-overview",
      "type": "text",
      "props": {{
        "content": "这里写2-3段话，解释这个卦的核心含义，打个比喻让人容易理解。比如这个卦就像是...",
        "variant": "body"
      }}
    }},
    {{
      "id": "card-interpretation",
      "type": "card",
      "props": {{
        "title": "🔮 直白解读",
        "variant": "default"
      }},
      "children": ["text-interpretation"]
    }},
    {{
      "id": "text-interpretation",
      "type": "text",
      "props": {{
        "content": "针对'{question}'这个问题：\\n\\n1. 目前情况：...\\n2. 事情发展：...\\n3. 最终结果：...\\n4. 具体分析：...\\n\\n用大白话，至少200字。",
        "variant": "body"
      }}
    }},
    {{
      "id": "card-fortune",
      "type": "card",
      "props": {{
        "title": "⚖️ 吉凶判断",
        "variant": "highlighted"
      }},
      "children": ["badge-fortune", "text-fortune-reason"]
    }},
    {{
      "id": "badge-fortune",
      "type": "badge",
      "props": {{
        "label": "吉/凶/中吉/小凶等",
        "color": "根据吉凶选择：success/warning/error/info"
      }}
    }},
    {{
      "id": "text-fortune-reason",
      "type": "text",
      "props": {{
        "content": "一句话解释为什么是这个吉凶判断",
        "variant": "caption"
      }}
    }},
    {{
      "id": "card-advice",
      "type": "card",
      "props": {{
        "title": "💡 具体建议",
        "variant": "default"
      }},
      "children": ["list-advice"]
    }},
    {{
      "id": "list-advice",
      "type": "list",
      "props": {{
        "items": [
          "建议1：具体可操作的建议",
          "建议2：什么时候做比较好",
          "建议3：找什么样的人帮忙",
          "建议4：不应该做什么"
        ],
        "ordered": true
      }}
    }},
    {{
      "id": "card-warning",
      "type": "card",
      "props": {{
        "title": "⚠️ 特别提醒",
        "variant": "warning"
      }},
      "children": ["text-warning"]
    }},
    {{
      "id": "text-warning",
      "type": "text",
      "props": {{
        "content": "需要特别注意的陷阱或风险，什么事情千万不能做",
        "variant": "body"
      }}
    }}
  ],
  "metadata": {{
    "hexagramName": "{original_hexagram['name']}",
    "question": "{question}",
    "generatedBy": "{self.MODEL_NAME}"
  }}
}}
```

请根据卦象信息，生成完整的 A2UI JSON。内容要丰富、接地气，像有经验的长辈在分析问题。
"""
        return prompt
    
    def _parse_a2ui_response(
        self,
        raw_response: str,
        question: str,
        original_hexagram: Dict,
        changed_hexagram: Optional[Dict],
        lines: list
    ) -> Dict:
        """
        解析 AI 直接生成的 A2UI JSON
        """
        import re
        
        # 尝试从响应中提取 JSON
        json_str = raw_response.strip()
        
        # 移除可能的 markdown 代码块标记
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        elif json_str.startswith("```"):
            json_str = json_str[3:]
        
        if json_str.endswith("```"):
            json_str = json_str[:-3]
        
        json_str = json_str.strip()
        
        # 尝试解析 JSON
        try:
            a2ui_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败: {e}")
            # 尝试用正则表达式提取 JSON 对象
            json_match = re.search(r'\{[\s\S]*\}', raw_response)
            if json_match:
                try:
                    a2ui_data = json.loads(json_match.group())
                except json.JSONDecodeError:
                    raise ValueError(f"无法解析 AI 返回的 A2UI JSON: {raw_response[:500]}")
            else:
                raise ValueError(f"AI 响应中未找到有效的 JSON: {raw_response[:500]}")
        
        # 补充卦象数据（前端需要用来展示卦象图形）
        if "data" not in a2ui_data:
            a2ui_data["data"] = {}
        
        a2ui_data["data"]["question"] = question
        a2ui_data["data"]["originalHexagram"] = original_hexagram
        a2ui_data["data"]["changedHexagram"] = changed_hexagram
        a2ui_data["data"]["lines"] = lines
        
        # 标记这是真正的 A2UI 响应
        if "metadata" not in a2ui_data:
            a2ui_data["metadata"] = {}
        a2ui_data["metadata"]["generatedBy"] = self.MODEL_NAME
        a2ui_data["metadata"]["isNativeA2UI"] = True
        
        return a2ui_data
    
    def _extract_sections_from_a2ui(self, a2ui_response: Dict) -> Dict[str, str]:
        """从 A2UI 组件中提取 sections 用于日志记录"""
        sections = {}
        components = a2ui_response.get("components", [])
        
        # 建立 id -> component 的映射
        component_map = {c.get("id"): c for c in components if c.get("id")}
        
        for component in components:
            if component.get("type") == "card":
                title = component.get("props", {}).get("title", "")
                if title:
                    # 获取子组件的内容
                    children_ids = component.get("children", [])
                    content_parts = []
                    for child_id in children_ids:
                        child = component_map.get(child_id)
                        if child:
                            if child.get("type") == "text":
                                content_parts.append(child.get("props", {}).get("content", ""))
                            elif child.get("type") == "badge":
                                content_parts.append(f"[{child.get('props', {}).get('label', '')}]")
                            elif child.get("type") == "list":
                                items = child.get("props", {}).get("items", [])
                                content_parts.append("\n".join(f"- {item}" for item in items))
                    
                    if content_parts:
                        # 清理标题中的 emoji
                        clean_title = title.replace("📖 ", "").replace("🔮 ", "").replace("⚖️ ", "").replace("💡 ", "").replace("⚠️ ", "")
                        sections[clean_title] = "\n".join(content_parts)
        
        return sections
    
    def _generate_fallback_response(
        self,
        question: str,
        original_hexagram: Dict,
        changed_hexagram: Optional[Dict],
        lines: list
    ) -> Dict:
        """生成回退响应（当 API 调用失败时使用）"""
        upper_nature = original_hexagram['upperTrigram']['nature']
        lower_nature = original_hexagram['lowerTrigram']['nature']
        hexagram_name = original_hexagram['name']
        judgment = original_hexagram.get('judgment', '')
        
        return {
            "version": "1.0",
            "root": "fallback-root",
            "components": [
                {
                    "id": "card-overview",
                    "type": "card",
                    "props": {
                        "title": "📖 卦象总论",
                        "variant": "elevated"
                    },
                    "children": ["text-overview"]
                },
                {
                    "id": "text-overview",
                    "type": "text",
                    "props": {
                        "content": f"您所得之卦为「{hexagram_name}」。上卦为{original_hexagram['upperTrigram']['name']}，代表{upper_nature}；下卦为{original_hexagram['lowerTrigram']['name']}，代表{lower_nature}。卦辞：{judgment}",
                        "variant": "body"
                    }
                },
                {
                    "id": "card-fortune",
                    "type": "card",
                    "props": {
                        "title": "⚖️ 吉凶判断",
                        "variant": "highlighted"
                    },
                    "children": ["badge-fortune"]
                },
                {
                    "id": "badge-fortune",
                    "type": "badge",
                    "props": {
                        "label": "待解读",
                        "color": "info"
                    }
                },
                {
                    "id": "card-warning",
                    "type": "card",
                    "props": {
                        "title": "⚠️ 提示",
                        "variant": "warning"
                    },
                    "children": ["text-warning"]
                },
                {
                    "id": "text-warning",
                    "type": "text",
                    "props": {
                        "content": "AI 服务暂时不可用，显示基础卦象信息。请稍后重试获取详细解读。",
                        "variant": "body"
                    }
                }
            ],
            "data": {
                "question": question,
                "originalHexagram": original_hexagram,
                "changedHexagram": changed_hexagram,
                "lines": lines
            },
            "metadata": {
                "hexagramName": hexagram_name,
                "question": question,
                "generatedBy": "fallback",
                "isNativeA2UI": False
            }
        }

