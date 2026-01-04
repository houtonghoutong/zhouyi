"""
周易占卜 APP 后端服务
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import divination

app = FastAPI(
    title="周易占卜 API",
    description="基于中国传统文化的智能占卜服务",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(divination.router, prefix="/api/divination", tags=["占卜"])


@app.get("/")
async def root():
    """健康检查"""
    return {"status": "ok", "message": "周易占卜服务运行中"}


@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}

