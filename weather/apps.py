import os
from pathlib import Path
import requests
import streamlit as st
from dotenv import load_dotenv

# 1. .env 파일 탐색 (현재 폴더 및 상위 폴더 동시 지원)
current_dir = Path(__file__).resolve().parent
env_in_current = current_dir / ".env"
env_in_parent = current_dir.parent / ".env"

if env_in_current.exists():
    load_dotenv(dotenv_path=env_in_current)
elif env_in_parent.exists():
    load_dotenv(dotenv_path=env_in_parent)
else:
    load_dotenv()

# API 키 가져오기
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY") or os.getenv("openweather_api_key")
EXCHANGE_API_KEY = os.getenv("EXCHANGERATE_API_KEY") or os.getenv("exchangerate_api_key")

# 2. 환율 조회 함수 (USD -> KRW)
def get_exchange_rate(api_key):
    if not api_key:
        return None
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        if data.get("result") == "success":
            return data["conversion_rates"].get("KRW")
    except requests.exceptions.RequestException:
        return None
    return None

# 3. Streamlit 화면 기본 설정
st.set_page_config(page_title="실시간 날씨 & 환율 검색", page_icon="🌤️", layout="centered")
st.title("🌤️ 실시간 날씨 & 환율 정보")

if not WEATHER_API_KEY:
    st.error("⚠️ 날씨 API 키를 찾을 수 없습니다. `.env` 파일의 `OPENWEATHER_API_KEY`를 확인해 주세요.")
    st.stop()

# 4. 사용자 입력 인터페이스
city = st.text_input("도시 이름을 영문으로 입력하세요 (예: Seoul, Tokyo, London):", "Seoul")

if st.button("날씨 및 환율 조회", type="primary"):
    if not city.strip():
        st.warning("도시 이름을 입력해 주세요.")
    else:
        weather_url = "https://api.openweathermap.org/data/2.5/weather"
        weather_params = {
            "q": city.strip(),
            "appid": WEATHER_API_KEY,
            "units": "metric",
            "lang": "kr"
        }

        try:
            weather_res = requests.get(weather_url, params=weather_params, timeout=5)
            weather_data = weather_res.json()

            if weather_res.status_code == 200:
                weather_desc = weather_data["weather"][0]["description"]
                icon_code = weather_data["weather"][0]["icon"]
                temp = weather_data["main"]["temp"]
                feels_like = weather_data["main"]["feels_like"]
                humidity = weather_data["main"]["humidity"]
                wind_speed = weather_data["wind"]["speed"]
                country = weather_data["sys"]["country"]

                krw_rate = get_exchange_rate(EXCHANGE_API_KEY)

                st.subheader(f"📍 {weather_data['name']}, {country}")

                col1, col2, col3 = st.columns([1, 2, 2])
                with col1:
                    icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
                    st.image(icon_url, width=90)
                with col2:
                    st.metric(label="현재 기온", value=f"{temp}°C", delta=f"체감 {feels_like}°C")
                    st.caption(f"**상태:** {weather_desc}")
                with col3:
                    if krw_rate:
                        st.metric(label="💵 USD / KRW 환율", value=f"{krw_rate:,.1f}원")
                        st.caption("ExchangeRate-API 기준")
                    else:
                        st.metric(label="💵 USD / KRW 환율", value="조회 불가")
                        st.caption(".env 환율 키 확인 필요")

                st.divider()

                m_col1, m_col2 = st.columns(2)
                m_col1.metric(label="💧 습도", value=f"{humidity}%")
                m_col2.metric(label="💨 풍속", value=f"{wind_speed} m/s")

            elif weather_res.status_code == 404:
                st.error("도시를 찾을 수 없습니다. 영문 철자를 다시 확인해 주세요.")
            elif weather_res.status_code == 401:
                st.error("유효하지 않은 날씨 API 키입니다. 키 활성화 상태를 확인해 주세요.")
            else:
                st.error(f"오류가 발생했습니다: {weather_data.get('message', '알 수 없는 오류')}")

        except requests.exceptions.RequestException as e:
            st.error(f"네트워크 연결 오류: {e}")