import os
import pandas as pd
import streamlit as st
from datetime import date
from openai import OpenAI

st.set_page_config(page_title="羽毛球训练计划生成器", page_icon="🏸")

st.title("🏸 羽毛球训练计划生成器")
st.caption("输入你的需求，一键生成训练计划（可下载 CSV）")

# ---- 输入区 ----
level = st.selectbox("水平", ["初学者", "中级", "进阶"])
days = st.slider("训练天数", 3, 14, 7)
duration = st.slider("每次训练时长（分钟）", 20, 120, 30, step=5)
goal = st.text_input("目标（可选）", placeholder="例如：正手高远球更稳定 / 提升步伐 / 准备比赛")

prompt = f"""
请生成一个羽毛球{level}的{days}天训练计划。
每次训练时长约{duration}分钟。
目标：{goal if goal else "无特别目标，均衡提升"}。
用 CSV 格式输出，必须包含表头：
Day,Theme,Drills,DurationMin,Intensity,Notes
Day 用 01,02,... 这种两位数。
每行一个训练日，不要输出任何多余解释文字，只输出 CSV。
"""

# ---- 按钮区 ----
if st.button("生成计划 ✅", type="primary"):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("没检测到 OPENAI_API_KEY。请先在 PowerShell 设置：$env:OPENAI_API_KEY=\"sk-proj-...\"")
        st.stop()

    client = OpenAI(api_key=api_key)

    with st.spinner("生成中..."):
        resp = client.responses.create(
            model="gpt-4o-mini",
            input=prompt
        )
        csv_text = resp.output_text.strip()

    # 解析 CSV
    try:
        from io import StringIO
        df = pd.read_csv(StringIO(csv_text))
    except Exception:
        st.error("模型输出不是标准 CSV，我把原文给你，你复制检查一下：")
        st.code(csv_text)
        st.stop()

    st.success("生成成功！")
    st.dataframe(df, use_container_width=True)

    filename = f"plan_{level}_{days}d_{date.today().isoformat()}.csv"
    st.download_button(
        "⬇️ 下载 CSV",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name=filename,
        mime="text/csv"
    )
