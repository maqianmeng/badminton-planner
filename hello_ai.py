from openai import OpenAI
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

prompt = """
请输出“羽毛球初学者 7 天训练计划”，要求：
- 只输出 CSV（逗号分隔），不要解释文字
- 第一行必须是表头：Day,Theme,Drills,DurationMin,Intensity,Notes
- Day 用 D1~D7
- DurationMin 用数字
- Drills 用“;”分隔多个练习
- 计划要适合完全新手，包含：热身、步法、发球、正手/反手基础、简单多球、拉伸
"""

resp = client.responses.create(
    model="gpt-4o-mini",
    input=prompt
)

print(resp.output_text)

