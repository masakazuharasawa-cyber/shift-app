import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# ==============================
# ページ設定
# ==============================
st.set_page_config(page_title="シフト保存アプリ", layout="wide")

st.title("シフト保存アプリ")

# ==============================
# Google認証
# ==============================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

# ==============================
# シートをIDで開く
# ==============================
SHEET_ID = "1WwAUYrZL3dUcIeW98ssN1FhCltVJlPb720N-EBaxtXg"
sheet = client.open_by_key(SHEET_ID).sheet1

# ==============================
# 入力フォーム
# ==============================
st.subheader("新規保存")

col1, col2 = st.columns(2)

with col1:
    date = st.date_input("日付")

with col2:
    members = st.text_input("メンバー（カンマ区切り）")

# ==============================
# 保存処理（追記方式）
# ==============================
if st.button("保存"):
    if members.strip() == "":
        st.warning("井上","洪","原澤","吉田","勝村")
    else:
        sheet.append_row(
            [str(date), members],
            value_input_option="USER_ENTERED"
        )
        st.success("保存しました（過去データは消えません）")

# ==============================
# データ表示
# ==============================
st.subheader("保存済みデータ")

data = sheet.get_all_records()

if data:
    df = pd.DataFrame(data)

    # 月でフィルター（任意）
    selected_month = st.selectbox(
        "表示する月を選択",
        options=sorted(
            {d[:7] for d in df["date"]},
            reverse=True
        )
    )

    filtered_df = df[df["date"].str.startswith(selected_month)]

    st.dataframe(filtered_df, use_container_width=True)

else:
    st.info("まだデータがありません")
