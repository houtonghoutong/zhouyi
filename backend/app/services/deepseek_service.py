"""
DeepSeek AI 服务

使用 DeepSeek API 生成卦象解读，并返回 A2UI 格式的动态 UI 数据
DeepSeek API 兼容 OpenAI 接口格式
"""
import os
from typing import Dict, Optional
from openai import OpenAI
from app.services.base_ai_service import BaseAIService


class DeepSeekService(BaseAIService):
    """DeepSeek AI 服务"""
    
    MODEL_NAME = "deepseek"
    MODEL_DISPLAY_NAME = "DeepSeek"
    
    # DeepSeek API 配置
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"
    DEEPSEEK_MODEL = "deepseek-chat"
    
    def __init__(self):
        """初始化 DeepSeek 服务"""
        super().__init__()
        
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if api_key:
            self.client = OpenAI(
                api_key=api_key,
                base_url=self.DEEPSEEK_BASE_URL
            )
        else:
            self.client = None
    
    async def generate_liuyao_interpretation(
        self,
        question: str,
        original_hexagram: Dict,
        changed_hexagram: Optional[Dict],
        lines: list
    ) -> Dict:
        """
        生成六爻占卜的 AI 解读，返回 A2UI 格式
        
        使用 DeepSeek API，真正的 A2UI 实现
        """
        prompt = ""
        raw_response = ""
        parsed_sections = {}
        
        if not self.client:
            # 使用回退响应
            a2ui_response = self._generate_fallback_response(question, original_hexagram, changed_hexagram, lines)
            self._save_interaction_log(
                question=question,
                original_hexagram=original_hexagram,
                changed_hexagram=changed_hexagram,
                lines=lines,
                prompt="[DeepSeek API 未配置，使用回退响应]",
                raw_response="[回退响应]",
                parsed_sections={},
                a2ui_response=a2ui_response,
                success=True,
                error_message="DeepSeek API key 未配置"
            )
            return a2ui_response
        
        try:
            # 构建 A2UI 格式的提示词
            prompt = self._build_a2ui_prompt(question, original_hexagram, changed_hexagram, lines)
            
            # 调用 DeepSeek API（同步调用，但在 async 函数中使用）
            response = self.client.chat.completions.create(
                model=self.DEEPSEEK_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位精通周易的占卜大师，擅长用通俗易懂的语言解读卦象。你需要直接输出 JSON 格式的 A2UI 响应，不要输出任何其他文字。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            raw_response = response.choices[0].message.content
            
            # 解析 A2UI JSON
            a2ui_response = self._parse_a2ui_response(
                raw_response=raw_response,
                question=question,
                original_hexagram=original_hexagram,
                changed_hexagram=changed_hexagram,
                lines=lines
            )
            
            # 提取 sections 用于日志
            parsed_sections = self._extract_sections_from_a2ui(a2ui_response)
            
            # 保存成功的交互日志
            self._save_interaction_log(
                question=question,
                original_hexagram=original_hexagram,
                changed_hexagram=changed_hexagram,
                lines=lines,
                prompt=prompt,
                raw_response=raw_response,
                parsed_sections=parsed_sections,
                a2ui_response=a2ui_response,
                success=True
            )
            
            return a2ui_response
            
        except Exception as e:
            error_msg = str(e)
            print(f"DeepSeek API 调用失败: {error_msg}")
            
            # 使用回退响应
            a2ui_response = self._generate_fallback_response(question, original_hexagram, changed_hexagram, lines)
            
            # 保存失败的交互日志
            self._save_interaction_log(
                question=question,
                original_hexagram=original_hexagram,
                changed_hexagram=changed_hexagram,
                lines=lines,
                prompt=prompt,
                raw_response=raw_response,
                parsed_sections={},
                a2ui_response=a2ui_response,
                success=False,
                error_message=error_msg
            )
            
            return a2ui_response

