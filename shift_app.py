import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# ==========================
# Google接続
# ==========================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

sheet = client.open_by_key("1WwAUYrZL3dUcIeW98ssN1FhCltVJlPb720N-EBaxtXg").sheet1

# ==========================
# パスワード
# ==========================
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

if "mode" not in st.session_state:
    st.session_state.mode = "view"

st.title("シフト管理アプリ")

year = st.number_input("年", value=datetime.now().year)
month = st.number_input("月", min_value=1, max_value=12, value=datetime.now().month)

members = ["井上", "洪", "原澤", "吉田", "勝村"]

# ==========================
# データ読み込み
# ==========================
data = sheet.get_all_records()
saved_data = {row["date"]: row["members"] for row in data}

days_in_month = calendar.monthrange(int(year), int(month))[1]

# ==========================
# 閲覧モード
# ==========================
if st.session_state.mode == "view":

    cal = calendar.monthcalendar(int(year), int(month))
    weekdays = ["月","火","水","木","金","土","日"]

    cols = st.columns(7)
    for i, day_name in enumerate(weekdays):
        cols[i].markdown(f"### {day_name}")

    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("")
            else:
                date_key = f"{int(year)}-{int(month)}-{day}"
                names = saved_data.get(date_key, "")

                if names:
                    name_text = names.replace(", ", "<br>")
                    count = len(names.split(", "))
                else:
                    name_text = "ー"
                    count = 0

                cols[i].markdown(
                    f"""
                    <div style="background:#f9f9f9;
                                padding:10px;
                                border-radius:10px;
                                min-height:120px;">
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

# ==========================
# 編集モード
# ==========================
elif st.session_state.mode == "edit":

    shift_data = {}

    for day in range(1, days_in_month + 1):
        date_key = f"{int(year)}-{int(month)}-{day}"
        st.markdown(f"### {day}日")

        selected = []
        cols = st.columns(len(members))

        for i, member in enumerate(members):
            default_checked = False
            if date_key in saved_data:
                if member in saved_data[date_key].split(", "):
                    default_checked = True

            if cols[i].checkbox(
                member,
                value=default_checked,
                key=f"{date_key}-{member}"
            ):
                selected.append(member)

        if len(selected) > 4:
            st.error("⚠ 1日は最大4人まで")

        shift_data[date_key] = selected
        st.divider()

    # ===== 保存ボタン（forの外）=====
    if st.button("💾 保存"):

        existing_data = sheet.get_all_records()
        existing_dict = {row["date"]: row["members"] for row in existing_data}

    # 今月分だけ更新
        for k, v in shift_data.items():
            existing_dict[k] = ", ".join(v)

    # ===== 一括書き込み用データ作成 =====
        all_rows = [["date", "members"]]

        for k, v in existing_dict.items():
            all_rows.append([k, v])

    # ===== シート全体を一括更新 =====
        sheet.clear()
        sheet.update("A1", all_rows)

        st.success("保存しました（他の月は消えません）")
        st.session_state.mode = "view"
        st.rerun()

    if st.button("キャンセル"):
        st.session_state.mode = "view"
        st.rerun()


