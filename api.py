import os
import json
import traceback
from typing import AsyncGenerator
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from starlette.templating import Jinja2Templates
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
# @app.get("/", response_class=HTMLResponse)
# async def root():
#     html_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
#     with open(html_path, "r", encoding="utf-8") as f:
#         html_content = f.read()
#     return HTMLResponse(content=html_content)

@app.get("/", response_class=HTMLResponse)
async def root():
    # 构造 index.html 的绝对路径
    current_dir = os.path.dirname(__file__)  # api.py 所在目录
    html_path = os.path.join(current_dir, "templates", "index.html")

    # 调试：打印路径和文件是否存在
    print(f"✅ HTML 文件路径：{html_path}")
    print(f"✅ 文件是否存在：{os.path.exists(html_path)}")

    # 读取文件内容
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(html_content)
    except Exception as e:
        return HTMLResponse(f"<h1>错误：{str(e)}</h1>路径：{html_path}", status_code=500)

@app.post("/chat/stream")
async def chat_stream(request: Request):
    body = await request.json()
    messages = body.get("messages", [])

    async with httpx.AsyncClient(timeout=None) as client:
        resp = await client.post(
            URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-r1",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *messages
                ],
                "stream": False
            }
        )

    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    return JSONResponse({"content": content})