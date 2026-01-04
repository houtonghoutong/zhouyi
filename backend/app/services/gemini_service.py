"""
Gemini AI 服务

使用 Google Gemini API 生成卦象解读，并返回 A2UI 格式的动态 UI 数据
"""
import os
from typing import Dict, Optional
import google.generativeai as genai
from app.services.base_ai_service import BaseAIService


class GeminiService(BaseAIService):
    """Gemini AI 服务"""
    
    MODEL_NAME = "gemini"
    MODEL_DISPLAY_NAME = "Google Gemini"
    
    def __init__(self):
        """初始化 Gemini 服务"""
        super().__init__()
        
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash")
        else:
            self.model = None
    
    async def generate_liuyao_interpretation(
        self,
        question: str,
        original_hexagram: Dict,
        changed_hexagram: Optional[Dict],
        lines: list
    ) -> Dict:
        """
        生成六爻占卜的 AI 解读，返回 A2UI 格式
        
        使用 Gemini API，真正的 A2UI 实现
        """
        prompt = ""
        raw_response = ""
        parsed_sections = {}
        
        if not self.model:
            # 使用回退响应
            a2ui_response = self._generate_fallback_response(question, original_hexagram, changed_hexagram, lines)
            self._save_interaction_log(
                question=question,
                original_hexagram=original_hexagram,
                changed_hexagram=changed_hexagram,
                lines=lines,
                prompt="[Gemini API 未配置，使用回退响应]",
                raw_response="[回退响应]",
                parsed_sections={},
                a2ui_response=a2ui_response,
                success=True,
                error_message="Gemini API key 未配置"
            )
            return a2ui_response
        
        try:
            # 构建 A2UI 格式的提示词
            prompt = self._build_a2ui_prompt(question, original_hexagram, changed_hexagram, lines)
            
            # 调用 Gemini API
            response = self.model.generate_content(prompt)
            raw_response = response.text
            
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
            print(f"Gemini API 调用失败: {error_msg}")
            
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
