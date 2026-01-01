# badminton_planner.py
import os
import argparse
from datetime import date

from openai import OpenAI

SYSTEM = """你是一名专业羽毛球教练，擅长为不同水平学员制定可执行、可量化的训练计划。
输出必须是 CSV，且只输出 CSV，不要多余解释。
CSV列固定为：
Day,Theme,Drills,DurationMin,Intensity,Notes

规则：
- Day 用 01,02...格式
- DurationMin 必须是整数
- Intensity 只能是 低/中/高
- Drills 用中文、用分号分隔多个练习点
- Notes 写注意事项/常见错误纠正
"""

def build_prompt(level: str, goal: str, days: int, minutes: int, days_per_week: int, equipment: str) -> str:
    return f"""
请为羽毛球学员制定训练计划，要求可直接拿来练。

学员水平：{level}
目标：{goal}
总天数：{days} 天
每次训练时长：{minutes} 分钟
每周训练频率：{days_per_week} 次/周（若总天数>7，请按周循环安排）
器材/场地：{equipment}

请输出CSV（仅CSV），从 Day=01 开始，连续到 Day={days:02d}。
""".strip()

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("ERROR: 没找到 OPENAI_API_KEY。请先在PowerShell里运行：$env:OPENAI_API_KEY=\"sk-...\"")

    parser = argparse.ArgumentParser(description="Badminton Training Plan Generator (CSV)")
    parser.add_argument("--level", default="初学者", help="初学者/进阶/中级/高级")
    parser.add_argument("--goal", default="正手高远球更稳定", help="训练目标，例如：步法更快、网前更细、杀球更有力")
    parser.add_argument("--days", type=int, default=7, help="计划天数，例如 7 或 14")
    parser.add_argument("--minutes", type=int, default=30, help="每次训练分钟数，例如 30/45/60")
    parser.add_argument("--freq", type=int, default=3, help="每周训练次数，例如 3/4/5")
    parser.add_argument("--equipment", default="标准羽毛球场；球拍；羽毛球；可用墙/发球机则更好", help="器材场地描述")
    parser.add_argument("--model", default="gpt-4o-mini", help="模型名，例如 gpt-4o-mini")
    parser.add_argument("--out", default="", help="输出文件名，例如 plan.csv；留空则自动命名")
    args = parser.parse_args()

    prompt = build_prompt(args.level, args.goal, args.days, args.minutes, args.freq, args.equipment)

    client = OpenAI(api_key=api_key)
    resp = client.responses.create(
        model=args.model,
        input=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
    )

    csv_text = resp.output_text.strip()

    # 简单兜底：如果模型不小心加了多余文字，尽量截取从表头开始
    header = "Day,Theme,Drills,DurationMin,Intensity,Notes"
    idx = csv_text.find(header)
    if idx != -1:
        csv_text = csv_text[idx:]

    out = args.out.strip()
    if not out:
        out = f"plan_{args.level}_{args.days}d_{date.today().isoformat()}.csv".replace(" ", "_")

    with open(out, "w", encoding="utf-8") as f:
        f.write(csv_text + "\n")

    print(f"\n✅ 已生成：{out}\n")
    print(csv_text)

if __name__ == "__main__":
    main()
