import streamlit as st
from skyfield.api import EarthSatellite, load
from datetime import datetime, timedelta
from pytz import timezone
import pandas as pd
import math
import re

# 🗺️ 분석 대상 지역 좌표
locations = {
    "진천읍": (36.8541, 127.4425),
    "대천읍": (36.3340, 126.5977),
    "해운대구": (35.1632, 129.1636),
    "벌교읍": (34.8450, 127.3502)
}

# 📐 거리 계산 (Haversine 공식)
def distance_km(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# 🛰️ 위성 진입/이탈 분석 함수
def analyze_passes(satellites, lat, lon, radius, hours):
    ts = load.timescale()
    t0 = datetime.utcnow()
    t1 = t0 + timedelta(hours=hours)
    step = timedelta(minutes=1)

    utc_times = [t0 + step * i for i in range(int((t1 - t0).total_seconds() / 60) + 1)]
    times = [ts.utc(t.year, t.month, t.day, t.hour, t.minute) for t in utc_times]

    results = []

    for sat in satellites:
        obj = sat["object"]
        in_zone = False
        entry = {}

        for i, t in enumerate(times):
            geo = obj.at(t).subpoint()
            dist = distance_km(lat, lon, geo.latitude.degrees, geo.longitude.degrees)
            vel_vector = obj.at(t).velocity.km_per_s
            horiz_vel = round(math.sqrt(vel_vector[0]**2 + vel_vector[1]**2), 3)  # 방향 제거한 속력

            if dist <= radius:
                if not in_zone:
                    in_zone = True
                    entry = {
                        "NORAD ID": sat["norad_id"],
                        "Common Name": sat["name"],
                        "Start Index": i,
                        "Start Time (LCLG)": t.utc_datetime().astimezone(timezone("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S"),
                        "Start Tgt CBF Lat (deg)": round(geo.latitude.degrees, 4),
                        "Start Tgt CBF Lon (deg)": round(geo.longitude.degrees, 4),
                        "Start Tgt CBF Alt (km)": round(geo.elevation.km, 3),
                        "Start LH HorizVel (km/sec)": horiz_vel
                    }
            else:
                if in_zone:
                    in_zone = False
                    geo2 = obj.at(t).subpoint()
                    vel_vector2 = obj.at(t).velocity.km_per_s
                    horiz_vel2 = round(math.sqrt(vel_vector2[0]**2 + vel_vector2[1]**2), 3)

                    entry.update({
                        "Stop Time (LCLG)": t.utc_datetime().astimezone(timezone("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S"),
                        "Stop Tgt CBF Lat (deg)": round(geo2.latitude.degrees, 4),
                        "Stop Tgt CBF Lon (deg)": round(geo2.longitude.degrees, 4),
                        "Stop Tgt CBF Alt (km)": round(geo2.elevation.km, 3),
                        "Stop LH HorizVel (km/sec)": horiz_vel2,
                        "Duration (sec)": (i - entry["Start Index"]) * 60
                    })
                    del entry["Start Index"]
                    results.append(entry)

    return pd.DataFrame(results)

# 🎨 Streamlit UI
st.title("🛰️ 위성분석 for MSSB")

tle_input = st.text_area("📋 TLE 입력 (3줄씩 여러 개)", height=300, placeholder="SAT1\n1 ...\n2 ...\nSAT2\n1 ...\n2 ...")
selected_location = st.selectbox("📍 분석할 지역", list(locations.keys()))
radius = st.selectbox("📐 분석 반경 (km)", [500, 1000, 1500, 2000])
hours = st.slider("⏰ 예측 시간 (시간)", 24, 168, 48)

if st.button("🔍 분석 시작"):
    if not tle_input.strip():
        st.warning("TLE 데이터를 입력해주세요.")
    else:
        lines = tle_input.strip().splitlines()
        if len(lines) % 3 != 0:
            st.error("TLE는 반드시 3줄씩 입력되어야 합니다.")
        else:
            satellites = []
            ts = load.timescale()
            for i in range(0, len(lines), 3):
                name = lines[i].strip()
                line1 = lines[i + 1].strip()
                line2 = lines[i + 2].strip()
                sat = EarthSatellite(line1, line2, name, ts)
                # NORAD 숫자만 추출
                raw_id = line1.split()[1]
                norad_id = re.search(r"\d+", raw_id).group()
                satellites.append({
                    "name": name,
                    "norad_id": norad_id,
                    "object": sat
                })

            lat, lon = locations[selected_location]
            df = analyze_passes(satellites, lat, lon, radius, hours)

            if df.empty:
                st.info("지정 범위 내 통과한 위성이 없습니다.")
            else:
                st.success(f"✅ {len(df)}개의 이벤트 분석 완료!")
                st.dataframe(df)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 CSV 다운로드", csv, "satellite_pass_events.csv", "text/csv")
