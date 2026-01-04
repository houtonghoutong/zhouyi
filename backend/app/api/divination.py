"""
占卜相关 API 路由
"""
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any
from app.services.liuyao_service import LiuYaoService
from app.services.ai_factory import AIServiceFactory

router = APIRouter()

# 服务实例
liuyao_service = LiuYaoService()


def snake_to_camel(name: str) -> str:
    """将 snake_case 转换为 camelCase"""
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def convert_keys_to_camel(data: Any) -> Any:
    """递归将字典的 key 从 snake_case 转换为 camelCase"""
    if isinstance(data, dict):
        return {snake_to_camel(k): convert_keys_to_camel(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_keys_to_camel(item) for item in data]
    return data


class LiuYaoRequest(BaseModel):
    """六爻占卜请求"""
    question: str  # 用户的问题
    coin_results: List[List[int]]  # 6次掷铜钱结果，每次3枚铜钱的正反面 [0=反, 1=正]
    model: Optional[str] = None  # AI 模型选择（gemini/deepseek），默认 gemini


class LiuYaoResponse(BaseModel):
    """六爻占卜响应"""
    success: bool
    originalHexagram: dict  # 本卦
    changedHexagram: Optional[dict] = None  # 变卦（如有变爻）
    lines: List[dict]  # 六爻详情
    a2uiResponse: dict  # A2UI 格式的动态 UI 数据
    model: str  # 使用的 AI 模型

    class Config:
        populate_by_name = True


class DivinationMethod(BaseModel):
    """占卜方式"""
    id: str
    name: str
    description: str
    icon: str
    available: bool


class AIModel(BaseModel):
    """AI 模型信息"""
    id: str
    name: str
    description: str
    icon: str
    default: bool


@router.get("/methods")
async def get_divination_methods() -> List[DivinationMethod]:
    """获取所有占卜方式"""
    return [
        DivinationMethod(
            id="liuyao",
            name="六爻占卜",
            description="掷铜钱起卦，传统易经占卜术",
            icon="🪙",
            available=True
        ),
        DivinationMethod(
            id="meihua",
            name="梅花易数",
            description="以数起卦，简洁高效",
            icon="🌸",
            available=False
        ),
        DivinationMethod(
            id="bazi",
            name="生辰八字",
            description="根据出生时间推算命理",
            icon="📅",
            available=False
        ),
        DivinationMethod(
            id="qimen",
            name="奇门遁甲",
            description="古老的预测术数",
            icon="🚪",
            available=False
        ),
    ]


@router.get("/models")
async def get_ai_models() -> List[AIModel]:
    """获取所有可用的 AI 模型"""
    models = AIServiceFactory.get_available_models()
    return [AIModel(**model) for model in models]


@router.post("/liuyao")
async def liuyao_divination(request: LiuYaoRequest) -> LiuYaoResponse:
    """
    六爻占卜
    
    接收用户的问题和6次掷铜钱结果，返回卦象和AI解读
    
    参数：
        question: 用户的问题
        coin_results: 6次掷铜钱结果
        model: AI 模型选择（gemini/deepseek），可选，默认 gemini
    """
    try:
        # 验证输入
        if len(request.coin_results) != 6:
            raise HTTPException(status_code=400, detail="需要6次掷铜钱结果")
        
        for i, coins in enumerate(request.coin_results):
            if len(coins) != 3:
                raise HTTPException(status_code=400, detail=f"第{i+1}次掷铜钱需要3枚铜钱结果")
        
        # 验证模型
        model_name = request.model or AIServiceFactory.DEFAULT_MODEL
        if not AIServiceFactory.is_valid_model(model_name):
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的模型: {model_name}，可用模型: gemini, deepseek"
            )
        
        # 计算卦象
        hexagram_result = liuyao_service.calculate_hexagram(request.coin_results)
        
        # 获取对应的 AI 服务
        ai_service = AIServiceFactory.get_service(model_name)
        
        # 调用 AI 生成 A2UI 解读
        a2ui_response = await ai_service.generate_liuyao_interpretation(
            question=request.question,
            original_hexagram=hexagram_result["original_hexagram"],
            changed_hexagram=hexagram_result.get("changed_hexagram"),
            lines=hexagram_result["lines"]
        )
        
        # 转换为 camelCase
        original_hexagram = convert_keys_to_camel(hexagram_result["original_hexagram"])
        changed_hexagram = convert_keys_to_camel(hexagram_result.get("changed_hexagram")) if hexagram_result.get("changed_hexagram") else None
        lines = convert_keys_to_camel(hexagram_result["lines"])
        
        return LiuYaoResponse(
            success=True,
            originalHexagram=original_hexagram,
            changedHexagram=changed_hexagram,
            lines=lines,
            a2uiResponse=a2ui_response,
            model=model_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"占卜失败: {str(e)}")
