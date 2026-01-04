"""
AI 服务工厂

根据模型名称创建对应的 AI 服务实例
"""
from typing import Dict, List
from app.services.base_ai_service import BaseAIService
from app.services.gemini_service import GeminiService
from app.services.deepseek_service import DeepSeekService


class AIServiceFactory:
    """AI 服务工厂"""
    
    # 已注册的 AI 服务
    _services: Dict[str, type] = {
        "gemini": GeminiService,
        "deepseek": DeepSeekService,
    }
    
    # 模型信息（用于前端展示）
    _model_info: Dict[str, Dict] = {
        "gemini": {
            "id": "gemini",
            "name": "Google Gemini",
            "description": "Google 最新的 AI 模型，响应快速",
            "icon": "✨",
            "default": True
        },
        "deepseek": {
            "id": "deepseek",
            "name": "DeepSeek",
            "description": "国产大模型，中文理解更优秀",
            "icon": "🔮",
            "default": False
        }
    }
    
    # 默认模型
    DEFAULT_MODEL = "gemini"
    
    # 服务实例缓存
    _instances: Dict[str, BaseAIService] = {}
    
    @classmethod
    def get_service(cls, model_name: str = None) -> BaseAIService:
        """
        获取 AI 服务实例
        
        参数：
            model_name: 模型名称（gemini/deepseek），默认使用 DEFAULT_MODEL
        
        返回：
            对应的 AI 服务实例
        """
        if not model_name:
            model_name = cls.DEFAULT_MODEL
        
        model_name = model_name.lower()
        
        if model_name not in cls._services:
            raise ValueError(f"不支持的模型: {model_name}，可用模型: {list(cls._services.keys())}")
        
        # 使用缓存的实例
        if model_name not in cls._instances:
            cls._instances[model_name] = cls._services[model_name]()
        
        return cls._instances[model_name]
    
    @classmethod
    def get_available_models(cls) -> List[Dict]:
        """
        获取所有可用的模型列表
        
        返回：
            模型信息列表
        """
        return list(cls._model_info.values())
    
    @classmethod
    def get_model_info(cls, model_name: str) -> Dict:
        """
        获取指定模型的信息
        
        参数：
            model_name: 模型名称
        
        返回：
            模型信息
        """
        return cls._model_info.get(model_name, {})
    
    @classmethod
    def is_valid_model(cls, model_name: str) -> bool:
        """
        检查模型名称是否有效
        
        参数：
            model_name: 模型名称
        
        返回：
            是否有效
        """
        return model_name.lower() in cls._services

