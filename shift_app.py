import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import os

# ===============================
# 🔐 パスワード設定
# ===============================
PASSWORD = "shift2026"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password = st.text_input("パスワードを入力してください", type="password")
    if password == PASSWORD:
        st.session_state.authenticated = True
        st.rerun()
    else:
        st.stop()

# ===============================
# 🧭 モード管理
# ===============================
if "mode" not in st.session_state:
    st.session_state.mode = "view"

st.title("シフト管理アプリ")

year = st.number_input("年", value=datetime.now().year)
month = st.number_input("月", min_value=1, max_value=12, value=datetime.now().month)

members = ["井上", "洪", "原澤", "吉田", "勝村"]
filename = "shift_data.csv"

# ===============================
# 📂 データ読み込み
# ===============================
if os.path.exists(filename):
    saved_df = pd.read_csv(filename)
    saved_df["members"] = saved_df["members"].fillna("")
    saved_data = dict(zip(saved_df["date"], saved_df["members"]))
else:
    saved_data = {}

days_in_month = calendar.monthrange(year, month)[1]

# ==================================================
# 👀 閲覧モード（カレンダー表示）
# ==================================================
if st.session_state.mode == "view":

    st.subheader("📅 カレンダー")

    cal = calendar.monthcalendar(year, month)
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]

    cols = st.columns(7)
    for i, day_name in enumerate(weekdays):
        cols[i].markdown(f"### {day_name}")

    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):

            if day == 0:
                cols[i].write("")
            else:
                date_key = f"{year}-{month}-{day}"
                names = saved_data.get(date_key, "")

                # ⭐ 安全処理（NaN対策）
                if isinstance(names, str) and names.strip() != "":
                    name_text = names.replace(", ", "<br>")
                    count = len(names.split(", "))
                else:
                    name_text = "ー"
                    count = 0

                # 土日色分け
                if i == 5:
                    bg = "#e0f0ff"
                elif i == 6:
                    bg = "#ffe0e0"
                else:
                    bg = "#f9f9f9"

                cols[i].markdown(
                    f"""
                    <div style="
                        background-color:{bg};
                        padding:10px;
                        border-radius:10px;
                        min-height:120px;
                    ">
                    <b>{day}日</b><br>
                    <small>{count}/4人</small><br><br>
                    {name_text}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    if st.button("✏ 編集する"):
        st.session_state.mode = "edit"
        st.rerun()

# ==================================================
# ✏ 編集モード
# ==================================================
elif st.session_state.mode == "edit":

    st.subheader("✏ シフト編集")

    shift_data = {}

    for day in range(1, days_in_month + 1):
        date_key = f"{year}-{month}-{day}"
        weekday = datetime(year, month, day).strftime("%a")

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

    if st.button("💾 保存"):
        df = pd.DataFrame([
            {"date": k, "members": ", ".join(v)}
            for k, v in shift_data.items()
        ])
        df.to_csv(filename, index=False)
        st.success("保存しました！")
        st.session_state.mode = "view"
        st.rerun()

    if st.button("キャンセル"):
        st.session_state.mode = "view"
        st.rerun()
