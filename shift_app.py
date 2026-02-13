import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import os

# ===== パスワード =====
PASSWORD = "shift2026"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password = st.text_input("パスワードを入力してください", type="password")
    if password == PASSWORD:
        st.session_state.authenticated = True
    else:
        st.stop()

st.title("シフト管理アプリ")

# ===== 月選択 =====
year = st.number_input("年", value=datetime.now().year)
month = st.number_input("月", min_value=1, max_value=12, value=datetime.now().month)

members = ["井上", "洪", "原澤", "吉田", "勝村"]

filename = "shift_data.csv"

if os.path.exists(filename):
    saved_df = pd.read_csv(filename)
    saved_data = dict(zip(saved_df["date"], saved_df["members"]))
else:
    saved_data = {}

cal = calendar.monthrange(year, month)[1]

shift_data = {}

st.divider()

# ===== 縦スクロール型UI =====
for day in range(1, cal + 1):
    date_key = f"{year}-{month}-{day}"
    weekday = datetime(year, month, day).strftime("%a")

    with st.container():
        st.markdown(f"### {day}日 ({weekday})")

        selected = []

        cols = st.columns(len(members))
        for i, member in enumerate(members):

            default_checked = False
            if date_key in saved_data:
                if member in str(saved_data[date_key]).split(", "):
                    default_checked = True

            if cols[i].checkbox(
                member,
                value=default_checked,
                key=f"{date_key}-{member}"
            ):
                selected.append(member)

        if len(selected) > 4:
            st.error("⚠ 1日は最大4人までです")

        shift_data[date_key] = selected

    st.divider()

# ===== 保存 =====
if st.button("保存"):
    df = pd.DataFrame([
        {"date": k, "members": ", ".join(v)}
        for k, v in shift_data.items()
    ])
    df.to_csv(filename, index=False)
    st.success("保存しました！")

# ===== 集計 =====
st.subheader("勤務日数集計")

count_dict = {member: 0 for member in members}

for v in shift_data.values():
    for member in v:
        count_dict[member] += 1

for member, count in count_dict.items():
    st.write(f"{member}: {count}日")