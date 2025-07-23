import streamlit as st
import requests

# 앱 제목
st.title("🛰️ TLE 호출 for MSSB")

# 사용자 입력 폼
input_method = st.radio("📌 입력 방식 선택", ["위성이름", "NORAD ID"])
input_values = st.text_area(
    "✍️ 입력하세요 (한 줄에 하나씩 여러 개 가능)", 
    height=200,
    placeholder="예시:\nSTARLINK-32502\n25544\nISS"
)

# 호출 버튼
if st.button("📡 TLE 호출"):
    queries = [line.strip() for line in input_values.strip().splitlines() if line.strip()]
    tle_results = []

    for query in queries:
        # Celestrak 요청 URL
        url = f"https://celestrak.org/NORAD/elements/search.php?search={query}&FORMAT=tle"
        response = requests.get(url)
        if response.status_code == 200 and response.text.strip():
            lines = response.text.strip().splitlines()
            if len(lines) >= 2:
                # 출력 형식을 분석용과 동일하게 3줄 구성
                tle_block = f"{lines[0]}\n{lines[1]}\n{lines[2]}"
                tle_results.append(tle_block)
            else:
                tle_results.append(f"# ❌ '{query}'에 대한 TLE 형식이 올바르지 않습니다.")
        else:
            tle_results.append(f"# ❌ '{query}'에 대한 TLE 데이터를 찾을 수 없습니다.")

    # 결과 출력
    st.subheader("📄 분석용 입력형식 출력")
    st.text("\n\n".join(tle_results))
