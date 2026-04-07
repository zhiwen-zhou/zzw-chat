import os
import json
import re
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import httpx

# ------------------ 基础配置 ------------------
load_dotenv()

API_KEY = os.getenv("DASHSCOPE_API_KEY")
if not API_KEY:
    raise ValueError("❌ 未读取到 DASHSCOPE_API_KEY，请检查 .env 文件")

URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

app = FastAPI()
templates = Jinja2Templates(directory="templates")


# ------------------ Prompt ------------------
SYSTEM_PROMPT = """
你是一个智能助手，支持调用以下技能：

- calc_circle_area(radius): 计算圆的面积
- add(a, b): 两数相加

如果用户请求可以通过技能完成，请返回如下 JSON：
{
  "skill": "skill_name",
  "args": {...}
}

否则请用自然语言直接回答。
"""

# ------------------ 根路径 ------------------
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ------------------ 流式聊天 ------------------
@app.post("/chat/stream")
async def chat_stream(request: Request):
    body = await request.json()
    user_message = body.get("message", "")

    async def event_generator():
        async with httpx.AsyncClient(timeout=None) as client:
            resp = await client.post(
                URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream"
                },
                json={
                    "model": "deepseek-r1",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_message}
                    ],
                    "stream": True
                },
                timeout=None
            )

            # ✅ 关键修复点
            async for chunk in resp.aiter_bytes():
                if chunk:
                    yield chunk.decode("utf-8")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )