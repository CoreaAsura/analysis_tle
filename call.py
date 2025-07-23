import streamlit as st
import requests

st.title("🛰️ TLE 호출 for MSSB")

# 📌 입력 방식: 위성명칭 또는 NORAD ID
sat_name = st.text_input("🛰️ 위성명칭 (예: STARLINK-32502)")
norad_id = st.text_input("🔢 NORAD ID (예: 62116)")

def fetch_tle(query):
    url = f"https://celestrak.org/NORAD/elements/search.php?search={query}&FORMAT=tle"
    response = requests.get(url)
    if response.status_code == 200 and response.text.strip():
        lines = response.text.strip().splitlines()
        if len(lines) >= 3:
            return f"{lines[0]}\n{lines[1]}\n{lines[2]}"
    return None

# 📡 호출 버튼
if st.button("📡 TLE 호출"):
    query = ""
    if sat_name.strip():
        query = sat_name.strip()
    elif norad_id.strip():
        query = norad_id.strip()

    if not query:
        st.warning("위성명칭 또는 NORAD ID 중 하나를 입력해주세요.")
    else:
        tle = fetch_tle(query)
        if tle:
            st.subheader("📄 분석용 TLE 형식 출력")
            st.text(tle)
        else:
            st.error(f"❌ '{query}'에 대한 TLE 데이터를 찾을 수 없습니다.")
