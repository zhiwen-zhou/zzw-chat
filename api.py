import os
import json
import traceback
from typing import AsyncGenerator

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

# ------------------ 流式聊天（最终稳定版） ------------------
@app.post("/chat/stream")
async def chat_stream(request: Request):
    try:
        body = await request.json()
        user_message = body.get("message", "")

        async def event_generator() -> AsyncGenerator[str, None]:
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

                # ✅ Windows + httpx + Starlette 最稳写法
                async for chunk in resp.iter_raw():
                    if chunk:
                        yield chunk.decode("utf-8", errors="ignore")

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )

    except Exception:
        # ✅ 强制在控制台打印完整 Traceback
        traceback.print_exc()
        raise

@app.post("/chat/no-stream")
async def chat_no_stream(request: Request):
    try:
        body = await request.json()
        user_message = body.get("message", "")

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
                        {"role": "user", "content": user_message}
                    ]
                }
            )

            # 非流式，直接返回完整 JSON
            result = resp.json()
            reply = result["choices"][0]["message"]["content"]
            return {"reply": reply}

    except Exception as e:
        # 这里一定会打印错误，帮你定位问题
        print("❌ /chat/no-stream 异常：", str(e))
        print(traceback.format_exc())
        return {"error": str(e), "trace": traceback.format_exc()}

@app.get("/ping")
async def ping():
    return {"status": "ok"}