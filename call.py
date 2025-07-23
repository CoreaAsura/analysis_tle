import streamlit as st
import requests

# 🛰️ 앱 제목
st.title("🛰️ TLE 호출 for MSSB")

# 📥 사용자 입력
user_input = st.text_area("🔎 위성이름 또는 NORAD ID 입력 (한 줄에 하나씩)", height=200,
                          placeholder="STARLINK-32502\n25544\nISS\n...")

# 📦 결과 저장용 리스트
tle_results = []

# 📡 Celestrak TLE 요청 함수
def fetch_tle(query):
    # Celestrak URL (예: https://celestrak.org/NORAD/elements/search.php?search=ISS&FORMAT=tle)
    url = f"https://celestrak.org/NORAD/elements/search.php?search={query}&FORMAT=tle"
    response = requests.get(url)
    if response.status_code == 200 and response.text.strip():
        return response.text.strip()
    else:
        return None

# 🔍 호출 버튼
if st.button("📡 TLE 호출"):
    if not user_input.strip():
        st.warning("위성 이름 또는 NORAD ID를 입력해주세요.")
    else:
        queries = [line.strip() for line in user_input.strip().splitlines() if line.strip()]
        for q in queries:
            tle = fetch_tle(q)
            if tle:
                tle_results.append(tle)
            else:
                tle_results.append(f"# ❌ '{q}'에 대한 TLE 데이터를 찾을 수 없습니다.")

        # 📋 결과 출력
        st.subheader("📄 호출된 TLE 결과")
        for block in tle_results:
            st.text(block)
