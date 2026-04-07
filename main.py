# import json
# import re
# from dashscope_client import chat_completion
# from skills import SKILL_REGISTRY
#
# SYSTEM_PROMPT = """
# 你是一个智能助手，支持调用以下技能：
#
# - calc_circle_area(radius): 计算圆的面积
# - add(a, b): 两数相加
#
# 如果用户请求可以通过技能完成，请返回如下 JSON：
# {
#   "skill": "skill_name",
#   "args": {...}
# }
#
# 否则请用自然语言直接回答。
# """
#
# def extract_json(text: str):
#     match = re.search(r"\{.*\}", text, re.S)
#     if not match:
#         return None
#     try:
#         return json.loads(match.group())
#     except json.JSONDecodeError:
#         return None
#
#
# def handle_user_input(user_input: str) -> str:
#     messages = [
#         {"role": "system", "content": SYSTEM_PROMPT},
#         {"role": "user", "content": user_input}
#     ]
#
#     reply = chat_completion(messages)
#
#     call = extract_json(reply)
#     if call and call.get("skill") in SKILL_REGISTRY:
#         func = SKILL_REGISTRY[call["skill"]]
#         result = func(**call["args"])
#         return f"✅ 调用 {call['skill']} 成功，结果：{result}"
#
#     return reply
#
#
# def main():
#     print("🤖 欢迎使用 ZZW-Chat（输入 exit 退出）")
#     while True:
#         user_input = input("\n你：").strip()
#         if user_input.lower() in ("exit", "quit", "q"):
#             print("👋 再见！")
#             break
#
#         response = handle_user_input(user_input)
#         print("AI：", response)
#
#
# if __name__ == "__main__":
#     main()