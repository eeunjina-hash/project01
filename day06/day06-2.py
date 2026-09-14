import os
from pathlib import Path
import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv
import pandas as pd
import unicodedata
from datetime import datetime
import zoneinfo

# ==========================================
# 1. 환경 설정 및 API 키 로드
# ==========================================
st.set_page_config(
    page_title="스마트 여행 올인원 플래너 PRO",
    page_icon="✈️",
    layout="wide"
)

# [디자인 차별화] 고해상도 프리미엄 CSS 주입
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    * {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif !important;
    }

    /* 배경 및 전체 톤 */
    .stApp {
        background-color: #F8FAFC;
    }

    /* 사이드바 스타일링 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #F1F5F9 100%);
        border-right: 1px solid #E2E8F0;
        box-shadow: 2px 0 12px rgba(0, 0, 0, 0.03);
    }

    /* 상단 배너 카드 */
    .hero-banner {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
        padding: 24px 30px;
        border-radius: 18px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.3);
    }
    .hero-banner h1 {
        color: white !important;
        font-weight: 800;
        font-size: 26px;
        margin: 0 0 6px 0;
    }
    .hero-banner p {
        color: #BFDBFE;
        font-size: 14px;
        margin: 0;
    }

    /* 상단 지표 카드 (보딩패스 감성 카드) */
    .stat-card {
        background: white;
        padding: 18px 20px;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 100%;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
    }
    .stat-label {
        color: #64748B;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .stat-val {
        color: #0F172A;
        font-size: 22px;
        font-weight: 800;
        margin-bottom: 4px;
    }
    .stat-sub {
        color: #0EA5E9;
        font-size: 12px;
        font-weight: 600;
    }

    /* 탭 스타일링 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #E2E8F0;
        padding: 6px;
        border-radius: 12px;
        border-bottom: none;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 18px;
        font-weight: 600;
        color: #475569;
        background-color: transparent;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #1E3A8A !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }

    /* 버튼 모던 라운딩 */
    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        border: none;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        opacity: 0.92;
        transform: scale(0.99);
    }
</style>
""", unsafe_allow_html=True)

# 로컬 환경용 .env 로드
current_dir = Path(__file__).resolve().parent
parent_env_path = current_dir.parent / '.env'
if parent_env_path.exists():
    load_dotenv(dotenv_path=parent_env_path)

def get_env_or_secret(key_name):
    val = os.getenv(key_name)
    if val:
        return val
    try:
        if hasattr(st, "secrets") and key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    return None

KAKAO_KEY = get_env_or_secret("KAKAO_REST_API_KEY")
WEATHER_KEY = get_env_or_secret("OPENWEATHER_API_KEY")
EXCHANGE_KEY = get_env_or_secret("EXCHANGERATE_API_KEY")

# ==========================================
# 2. 위치 및 시차/골든타임 엔진
# ==========================================

def search_overseas_place(query):
    clean_query = unicodedata.normalize('NFKC', query).strip()
    overseas_dict = {
        "도쿄": "Tokyo", "도쿄역": "Tokyo Station", "동경": "Tokyo",
        "신주쿠": "Shinjuku", "신주쿠역": "Shinjuku Station",
        "시부야": "Shibuya", "시부야역": "Shibuya Station",
        "후쿠오카": "Fukuoka", "후쿠오카역": "Hakata Station", "하카타": "Hakata Station", "하카타역": "Hakata Station",
        "오사카": "Osaka", "오사카역": "Osaka Station", "난바": "Namba Station",
        "교토": "Kyoto", "교토역": "Kyoto Station",
        "삿포로": "Sapporo", "삿포로역": "Sapporo Station", "나고야": "Nagoya", "오키나와": "Okinawa",
        "파리": "Paris", "런던": "London", "로마": "Rome", "뉴욕": "New York",
        "방콕": "Bangkok", "다낭": "Da Nang", "타이베이": "Taipei"
    }
    search_term = overseas_dict.get(clean_query, clean_query)

    try:
        url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent": "GlobalTravelProUI/4.0 (traveler-contact: student@travelapp.com)"}
        params = {"q": search_term, "format": "json", "limit": 1, "accept-language": "ko,en"}
        res = requests.get(url, headers=headers, params=params, timeout=5)
        if res.status_code == 200 and res.json():
            item = res.json()[0]
            lat = float(item["lat"])
            lng = float(item["lon"])
            full_addr = item.get("display_name", "")
            short_name = full_addr.split(",")[0].strip()
            return lat, lng, short_name, full_addr, "GLOBAL"
    except Exception:
        pass
    return None, None, None, None, None

def search_korea_place(query, kakao_key):
    clean_query = query.strip()
    
    # 1. 카카오 API 키가 유효하게 있으면 카카오 로컬 검색 시도
    if kakao_key:
        headers = {"Authorization": f"KakaoAK {kakao_key}"}
        # 장소명/키워드 검색
        try:
            url = "https://dapi.kakao.com/v2/local/search/keyword.json"
            res = requests.get(url, headers=headers, params={"query": clean_query, "size": 1}, timeout=3)
            if res.status_code == 200 and res.json().get("documents"):
                doc = res.json()["documents"][0]
                return float(doc["y"]), float(doc["x"]), doc["place_name"], doc.get("address_name", ""), "KR"
        except Exception:
            pass

        # 지번/도로명 주소 검색
        try:
            url_addr = "https://dapi.kakao.com/v2/local/search/address.json"
            res_addr = requests.get(url_addr, headers=headers, params={"query": clean_query, "size": 1}, timeout=3)
            if res_addr.status_code == 200 and res_addr.json().get("documents"):
                doc = res_addr.json()["documents"][0]
                return float(doc["y"]), float(doc["x"]), doc["address_name"], doc["address_name"], "KR"
        except Exception:
            pass

    # 2. 카카오 키가 없거나 카카오 검색에 실패한 경우: OpenStreetMap Nominatim으로 대체 검색
    try:
        url_nom = "https://nominatim.openstreetmap.org/search"
        headers_nom = {"User-Agent": "GlobalTravelProUI/4.0 (traveler-contact: student@travelapp.com)"}
        params_nom = {"q": clean_query, "format": "json", "limit": 1, "accept-language": "ko,en"}
        res_nom = requests.get(url_nom, headers=headers_nom, params=params_nom, timeout=4)
        if res_nom.status_code == 200 and res_nom.json():
            item = res_nom.json()[0]
            lat = float(item["lat"])
            lng = float(item["lon"])
            full_addr = item.get("display_name", "")
            short_name = full_addr.split(",")[0].strip()
            return lat, lng, short_name, full_addr, "KR"
    except Exception:
        pass

    return None, None, None, None, None


    clean_query = query.strip()
    headers = {"Authorization": f"KakaoAK {kakao_key}"}
    try:
        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        res = requests.get(url, headers=headers, params={"query": clean_query, "size": 1}, timeout=3)
        if res.status_code == 200 and res.json().get("documents"):
            doc = res.json()["documents"][0]
            return float(doc["y"]), float(doc["x"]), doc["place_name"], doc.get("address_name", ""), "KR"
    except Exception:
        pass

    try:
        url_addr = "https://dapi.kakao.com/v2/local/search/address.json"
        res_addr = requests.get(url_addr, headers=headers, params={"query": clean_query, "size": 1}, timeout=3)
        if res_addr.status_code == 200 and res_addr.json().get("documents"):
            doc = res_addr.json()["documents"][0]
            return float(doc["y"]), float(doc["x"]), doc["address_name"], doc["address_name"], "KR"
    except Exception:
        pass
    return None, None, None, None, None

def search_category_places(lat, lng, category_code, api_key, radius=1500, size=5):
    if not api_key:
        return []
    url = "https://dapi.kakao.com/v2/local/search/category.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"category_group_code": category_code, "x": str(lng), "y": str(lat), "radius": radius, "size": size}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=3)
        if res.status_code == 200:
            return res.json().get("documents", [])
    except Exception:
        pass
    return []

def get_local_time_and_sun(lat, lon):
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {"latitude": lat, "longitude": lon, "daily": "sunrise,sunset", "timezone": "auto"}
        res = requests.get(url, params=params, timeout=4)
        if res.status_code == 200:
            data = res.json()
            tz_name = data.get("timezone", "UTC")
            tz = zoneinfo.ZoneInfo(tz_name)
            local_now = datetime.now(tz)
            kr_now = datetime.now(zoneinfo.ZoneInfo("Asia/Seoul"))
            diff_hours = int((local_now.utcoffset().total_seconds() - kr_now.utcoffset().total_seconds()) / 3600)
            diff_str = "한국과 동일" if diff_hours == 0 else (f"한국보다 +{diff_hours}시간" if diff_hours > 0 else f"한국보다 {diff_hours}시간")
            return {
                "local_time": local_now.strftime("%H:%M"),
                "local_date": local_now.strftime("%m월 %d일"),
                "time_diff": diff_str,
                "sunrise": data["daily"]["sunrise"][0].split("T")[1],
                "sunset": data["daily"]["sunset"][0].split("T")[1]
            }
    except Exception:
        pass
    return None

# ==========================================
# 3. 날씨 및 환율 엔진
# ==========================================

def interpret_wmo_code(code):
    mapping = {
        0: "맑음 ☀️", 1: "대체로 맑음 🌤️", 2: "구름 조금 ⛅", 3: "흐림 ☁️",
        45: "안개 🌫️", 48: "서리 안개 🌫️", 51: "이슬비 🌦️", 53: "약한 비 🌧️", 55: "보통 비 🌧️",
        61: "약한 비 🌧️", 63: "보통 비 🌧️", 65: "강한 비 ⛈️", 71: "약한 눈 🌨️", 73: "보통 눈 ❄️", 75: "강한 눈 ❄️",
        80: "소나기 🌦️", 95: "뇌우 ⚡"
    }
    return mapping.get(code, "흐림 ☁️")

def get_weather_data(lat, lon, api_key):
    if api_key:
        try:
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric", "lang": "kr"}
            res = requests.get(url, params=params, timeout=4)
            if res.status_code == 200:
                data = res.json()
                return {
                    "temp": round(data["main"]["temp"], 1),
                    "feels_like": round(data["main"]["feels_like"], 1),
                    "humidity": data["main"]["humidity"],
                    "desc": data["weather"][0]["description"],
                    "icon": f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@4x.png",
                    "wind": data["wind"]["speed"]
                }
        except Exception:
            pass

    try:
        meteo_url = "https://api.open-meteo.com/v1/forecast"
        m_params = {"latitude": lat, "longitude": lon, "current_weather": True, "hourly": "relativehumidity_2m,apparent_temperature"}
        res = requests.get(meteo_url, params=m_params, timeout=5)
        if res.status_code == 200:
            m_data = res.json()
            curr = m_data.get("current_weather", {})
            hourly = m_data.get("hourly", {})
            temp = round(curr.get("temperature", 20.0), 1)
            feels = round(hourly.get("apparent_temperature", [temp])[0], 1)
            humidity = hourly.get("relativehumidity_2m", [60])[0]
            w_desc = interpret_wmo_code(curr.get("weathercode", 0))
            return {
                "temp": temp,
                "feels_like": feels,
                "humidity": humidity,
                "desc": w_desc,
                "icon": "https://openweathermap.org/img/wn/02d@4x.png",
                "wind": curr.get("windspeed", 2.0)
            }
    except Exception:
        pass
    return None

def get_weather_forecast(lat, lon, api_key):
    if api_key:
        try:
            url = "https://api.openweathermap.org/data/2.5/forecast"
            params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric", "lang": "kr"}
            res = requests.get(url, params=params, timeout=4)
            if res.status_code == 200:
                records = []
                for item in res.json().get("list", []):
                    records.append({
                        "시간": item["dt_txt"][5:16],
                        "기온(°C)": round(item["main"]["temp"], 1),
                        "날씨": item["weather"][0]["description"]
                    })
                return pd.DataFrame(records)
        except Exception:
            pass

    try:
        meteo_url = "https://api.open-meteo.com/v1/forecast"
        m_params = {"latitude": lat, "longitude": lon, "hourly": "temperature_2m,weathercode", "forecast_days": 5}
        res = requests.get(meteo_url, params=m_params, timeout=5)
        if res.status_code == 200:
            m_data = res.json().get("hourly", {})
            times = m_data.get("time", [])
            temps = m_data.get("temperature_2m", [])
            codes = m_data.get("weathercode", [])
            records = []
            for i in range(0, len(times), 3):
                records.append({
                    "시간": times[i][5:16].replace("T", " "),
                    "기온(°C)": round(temps[i], 1),
                    "날씨": interpret_wmo_code(codes[i])
                })
            return pd.DataFrame(records)
    except Exception:
        pass
    return None

@st.cache_data(ttl=3600)
def get_exchange_rates(base_currency="KRW", api_key=None):
    headers = {"User-Agent": "Mozilla/5.0"}
    if api_key:
        try:
            url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200 and "conversion_rates" in res.json():
                return res.json()["conversion_rates"]
        except Exception:
            pass

    try:
        url = f"https://open.er-api.com/v6/latest/{base_currency}"
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200 and "rates" in res.json():
            return res.json()["rates"]
    except Exception:
        pass
    return {}

# ==========================================
# 4. 사이드바 구성
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='font-size:20px; font-weight:800; color:#1E293B;'>✈️ 여행 탐색 콘솔</h2>", unsafe_allow_html=True)
    
    travel_mode = st.radio("여행지 권역", options=["해외 여행 🌐", "국내 여행 🇰🇷"], index=0)
    
    default_val = "도쿄역" if "해외" in travel_mode else "송내역"
    destination_input = st.text_input("목적지 검색", value=default_val)
    
    st.markdown("---")
    st.markdown("<h3 style='font-size:16px; font-weight:700; color:#1E293B;'>💵 실시간 환율 계산기</h3>", unsafe_allow_html=True)
    rates = get_exchange_rates("KRW", EXCHANGE_KEY)
    
    target_currency = "JPY"
    if rates:
        target_currency = st.selectbox("목표 통화", options=["JPY", "USD", "EUR", "CNY", "VND", "THB", "TWD", "GBP"], index=0)
        krw_amount = st.number_input("금액 (KRW 원)", min_value=1000, value=100000, step=10000)
        rate = rates.get(target_currency, 0)
        if rate > 0:
            converted = krw_amount * rate
            base_rate = 1 / rate
            unit = 100 if target_currency in ["JPY", "VND"] else 1
            st.markdown(f"""
            <div style='background:#F8FAFC; border:1px solid #CBD5E1; border-radius:12px; padding:12px; margin-top:10px;'>
                <div style='font-size:12px; color:#64748B;'>환전 예상액</div>
                <div style='font-size:20px; font-weight:800; color:#0284C7;'>{converted:,.2f} {target_currency}</div>
                <div style='font-size:11px; color:#94A3B8; margin-top:4px;'>기준 환율: {unit}{target_currency} = {base_rate * unit:,.2f}원</div>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# 5. 메인 대시보드 화면
# ==========================================

# 상단 프리미엄 헤더 배너
st.markdown("""
<div class="hero-banner">
    <h1>🌍 SMART TRAVEL PLANNER PRO</h1>
    <p>전 세계 지도 탐색 · 실시간 시차 & 골든타임 · AI 스마트 팩커 · 환율 연동 여행 가계부</p>
</div>
""", unsafe_allow_html=True)

if "해외" in travel_mode:
    lat, lng, place_name, addr_name, location_type = search_overseas_place(destination_input)
else:
    lat, lng, place_name, addr_name, location_type = search_korea_place(destination_input, KAKAO_KEY)

if not lat or not lng:
    st.error(f"'{destination_input}'의 위치 정보를 찾을 수 없습니다. 영문 표기나 정확한 명칭으로 다시 검색해 보세요.")
    st.stop()

weather = get_weather_data(lat, lng, WEATHER_KEY)
sun_info = get_local_time_and_sun(lat, lng)

# [디자인 차별화] 보딩패스 감성의 모던 카드 4분할
col1, col2, col3, col4 = st.columns(4)

with col1:
    region_tag = "국내 여행" if location_type == "KR" else "해외 여행"
    badge_bg = "#DCFCE7" if location_type == "KR" else "#E0F2FE"
    badge_color = "#15803D" if location_type == "KR" else "#0369A1"
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">SELECTED DESTINATION</div>
        <div class="stat-val">{place_name}</div>
        <div style="margin-top: 2px;">
            <span style="background:{badge_bg}; color:{badge_color}; font-size:11px; font-weight:700; padding:3px 8px; border-radius:6px;">{region_tag}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if sun_info:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">LOCAL TIME ({sun_info['local_date']})</div>
            <div class="stat-val" style="color:#2563EB;">{sun_info['local_time']}</div>
            <div class="stat-sub">⏱️ {sun_info['time_diff']}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">LOCAL TIME</div>
            <div class="stat-val">동기화 중</div>
        </div>
        """, unsafe_allow_html=True)

with col3:
    if sun_info:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">GOLDEN HOUR (야경/선셋)</div>
            <div class="stat-val" style="color:#D97706;">🌅 {sun_info['sunset']}</div>
            <div class="stat-sub" style="color:#94A3B8;">일출 시각: {sun_info['sunrise']}</div>
        </div>
        """, unsafe_allow_html=True)
    elif weather:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">WEATHER</div>
            <div class="stat-val">{weather['temp']}°C</div>
            <div class="stat-sub">{weather['desc']}</div>
        </div>
        """, unsafe_allow_html=True)

with col4:
    if rates and target_currency in rates:
        current_rate = 1 / rates.get(target_currency, 1)
        unit = 100 if target_currency in ["JPY", "VND"] else 1
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">EXCHANGE RATE ({unit}{target_currency})</div>
            <div class="stat-val" style="color:#059669;">{current_rate * unit:,.1f}원</div>
            <div class="stat-sub" style="color:#94A3B8;">1시간 자동 갱신</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

tab_map, tab_weather, tab_ledger, tab_checklist = st.tabs([
    "🗺️ 지도 & 핫플 탐색", 
    "☀️ 날씨 & 5일 예보", 
    "💰 실시간 환율 여행 가계부", 
    "🎒 AI 짐싸기 & 리포트 내보내기"
])

# ----------------------------------------------------
# TAB 1: 지도 및 핫플 탐색
# ----------------------------------------------------
with tab_map:
    col_addr, col_btn = st.columns([3, 1])
    with col_addr:
        st.markdown(f"**📍 상세 주소:** `{addr_name}`")
        st.caption(f"좌표: 위도 {lat:.4f}, 경도 {lng:.4f}")
    with col_btn:
        if location_type == "KR":
            navi_link = f"https://map.kakao.com/link/to/{place_name},{lat},{lng}"
            btn_label = "🚗 카카오맵 길찾기"
        else:
            navi_link = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}"
            btn_label = "🌐 구글맵 길찾기"
        st.link_button(btn_label, navi_link, use_container_width=True)

    if location_type == "KR":
        categories_cfg = {
            "맛집": {"code": "FD6", "color": "orange", "icon": "cutlery"},
            "카페": {"code": "CE7", "color": "blue", "icon": "coffee"},
            "숙박": {"code": "AD5", "color": "purple", "icon": "home"},
            "관광명소": {"code": "AT4", "color": "green", "icon": "camera"}
        }
        selected_cats = st.multiselect(
            "🔎 주변 편의시설/핫플 탐색 (카카오 로컬 제공 / 반경 1.5km)",
            options=list(categories_cfg.keys()),
            default=["맛집", "카페"]
        )
    else:
        st.info("💡 해외 지역은 구글맵 길찾기와 글로벌 Folium 고해상도 지도를 제공합니다.")

    m = folium.Map(location=[lat, lng], zoom_start=15)
    folium.Marker(
        [lat, lng],
        popup=folium.Popup(f"<b>[목적지] {place_name}</b><br>{addr_name[:40]}...", max_width=250),
        tooltip=f"목적지: {place_name}",
        icon=folium.Icon(color="red", icon="plane", prefix="fa")
    ).add_to(m)

    if location_type == "KR" and 'selected_cats' in locals():
        for cat_name in selected_cats:
            cfg = categories_cfg[cat_name]
            places = search_category_places(lat, lng, cfg["code"], KAKAO_KEY)
            for item in places:
                p_lat = float(item["y"])
                p_lng = float(item["x"])
                popup_html = f"""
                <div style='font-size:12px;'>
                    <b>{item['place_name']}</b><br>
                    <span>{item['address_name']}</span><br>
                    <a href='{item['place_url']}' target='_blank'>🔗 카카오 상세정보</a>
                </div>
                """
                folium.Marker(
                    [p_lat, p_lng],
                    popup=folium.Popup(popup_html, max_width=220),
                    tooltip=f"[{cat_name}] {item['place_name']}",
                    icon=folium.Icon(color=cfg["color"], icon=cfg["icon"], prefix="fa")
                ).add_to(m)

    st_folium(m, width="100%", height=500)

# ----------------------------------------------------
# TAB 2: 날씨 상세 및 5일 예보
# ----------------------------------------------------
with tab_weather:
    if weather:
        w1, w2 = st.columns([1, 2])
        with w1:
            st.image(weather['icon'], width=120)
            st.subheader(weather['desc'])
        with w2:
            st.write(f"- **현재 기온:** **{weather['temp']}°C** (체감: {weather['feels_like']}°C)")
            st.write(f"- **습도:** {weather['humidity']}% | **풍속:** {weather['wind']} m/s")
            
            if weather['temp'] >= 27:
                outfit = "민소매, 반팔, 린넨 의류, 자외선 차단제"
            elif weather['temp'] >= 20:
                outfit = "얇은 가디건, 반팔 티셔츠, 면바지"
            elif weather['temp'] >= 12:
                outfit = "자켓, 셔츠, 가디건, 간절기 외투"
            elif weather['temp'] >= 6:
                outfit = "코트, 가죽 자켓, 니트, 히트텍"
            else:
                outfit = "패딩, 목도리, 장갑, 방한 의류"
            st.info(f"💡 **스타일링 추천 옷차림:** {outfit}")

        st.markdown("---")
        st.subheader("📈 향후 5일간 기온 추이 예보")
        forecast_df = get_weather_forecast(lat, lng, WEATHER_KEY)
        if forecast_df is not None and not forecast_df.empty:
            chart_data = forecast_df.set_index("시간")[["기온(°C)"]]
            st.line_chart(chart_data)
            with st.expander("⏱️ 상세 3시간 단위 예보표 보기"):
                st.dataframe(forecast_df, use_container_width=True)
    else:
        st.info("날씨 데이터를 불러오는 중입니다.")

# ----------------------------------------------------
# TAB 3: 실시간 환율 여행 가계부
# ----------------------------------------------------
with tab_ledger:
    st.subheader(f"💳 현지 지출 기록부 ({target_currency} ➔ KRW 자동 환산)")
    
    if "expenses" not in st.session_state:
        st.session_state.expenses = [
            {"항목": "고속철도 티켓", "현지통화": target_currency, "금액": 3000.0, "결제수단": "트래블카드"},
            {"항목": "편의점 간식 & 음료", "현지통화": target_currency, "금액": 850.0, "결제수단": "현금"}
        ]
    
    with st.form("expense_form", clear_on_submit=True):
        f_col1, f_col2, f_col3, f_col4 = st.columns([3, 2, 2, 1])
        with f_col1:
            e_item = st.text_input("지출 항목", placeholder="예: 시부야 스카이, 스시 오마카세")
        with f_col2:
            e_amount = st.number_input(f"금액 ({target_currency})", min_value=0.0, step=100.0)
        with f_col3:
            e_method = st.selectbox("결제 수단", ["트래블카드", "현금", "신용카드"])
        with f_col4:
            st.write("")
            st.write("")
            submitted = st.form_submit_button("추가")
            if submitted and e_item and e_amount > 0:
                st.session_state.expenses.append({
                    "항목": e_item,
                    "현지통화": target_currency,
                    "금액": float(e_amount),
                    "결제수단": e_method
                })
                st.rerun()

    if st.session_state.expenses:
        exp_df = pd.DataFrame(st.session_state.expenses)
        rate_val = 1 / rates.get(target_currency, 1) if rates else 1
        exp_df["원화 환산액(KRW)"] = (exp_df["금액"] * rate_val).round(-1).astype(int)
        
        st.dataframe(
            exp_df.style.format({"금액": "{:,.2f}", "원화 환산액(KRW)": "{:,}원"}),
            use_container_width=True
        )
        
        total_local = exp_df["금액"].sum()
        total_krw = exp_df["원화 환산액(KRW)"].sum()
        
        c_tot1, c_tot2, c_btn = st.columns([2, 2, 1])
        c_tot1.metric(f"총 지출 합계 ({target_currency})", f"{total_local:,.2f} {target_currency}")
        c_tot2.metric("원화 총 지출 합산", f"{total_krw:,.0f}원")
        with c_btn:
            st.write("")
            if st.button("🗑️ 지출 내역 초기화"):
                st.session_state.expenses = []
                st.rerun()
    else:
        st.caption("아직 기록된 지출 내역이 없습니다. 위 입력창에서 추가해 보세요.")

# ----------------------------------------------------
# TAB 4: AI 짐싸기 & 리포트 내보내기
# ----------------------------------------------------
with tab_checklist:
    col_check, col_memo = st.columns(2)
    
    with col_check:
        st.subheader("🎒 AI 스마트 체크리스트")
        
        if "checklist" not in st.session_state:
            st.session_state.checklist = {
                "여권 및 신분증 지참": True,
                "비행기/열차 E-티켓 발권 확인": False,
                "현지 통화 환전 또는 트래블카드 준비": False,
                "보조배터리 및 110V/220V 어댑터": False,
                "상비약 (감기약, 소화제, 진통제)": False,
                "해외 로밍 / eSIM / 유심 구매 확인": False,
                "여행자 보험 가입 여부 체크": False
            }

        if st.button("✨ 현지 날씨 맞춤 필수 준비물 1초 주입"):
            added_count = 0
            if weather:
                t = weather['temp']
                d = weather['desc']
                if "비" in d or "소나기" in d:
                    for item in ["3단 접이식 우산", "방수 슈즈커버"]:
                        if item not in st.session_state.checklist:
                            st.session_state.checklist[item] = False
                            added_count += 1
                if t <= 12:
                    for item in ["핫팩 세트", "목도리 & 장갑", "보온 내의(히트텍)"]:
                        if item not in st.session_state.checklist:
                            st.session_state.checklist[item] = False
                            added_count += 1
                elif t >= 25:
                    for item in ["자외선 차단 선크림", "선글라스", "휴대용 손선풍기"]:
                        if item not in st.session_state.checklist:
                            st.session_state.checklist[item] = False
                            added_count += 1
            if added_count > 0:
                st.success(f"현지 기온 및 날씨에 맞춘 필수 아이템 {added_count}개가 추가되었습니다!")
                st.rerun()
            else:
                st.info("이미 현재 날씨에 필요한 아이템이 모두 포함되어 있습니다.")

        for item, checked in list(st.session_state.checklist.items()):
            new_val = st.checkbox(item, value=checked, key=f"chk_{item}")
            st.session_state.checklist[item] = new_val

        new_item = st.text_input("직접 준비물 항목 추가", placeholder="예: 비짓재팬 등록, 보조안경")
        if st.button("추가하기"):
            if new_item and new_item not in st.session_state.checklist:
                st.session_state.checklist[new_item] = False
                st.rerun()

    with col_memo:
        st.subheader("📝 일정 메모 & 다운로드")
        if "travel_memo" not in st.session_state:
            st.session_state.travel_memo = "1일차: 도착 후 호텔 체크인 & 명소 산책\n2일차: 랜드마크 방문 & 야경 골든타임 감상\n예산 메모: 1일 식비 6,000엔 / 교통카드 충전"

        memo_content = st.text_area(
            "자유롭게 여행 계획과 예산을 메모하세요",
            value=st.session_state.travel_memo,
            height=200
        )
        st.session_state.travel_memo = memo_content

        st.markdown("---")
        st.subheader("📤 오프라인용 여행 리포트 파일 받기")
        
        checked_items = [k for k, v in st.session_state.checklist.items() if v]
        unchecked_items = [k for k, v in st.session_state.checklist.items() if not v]
        
        report_text = f"""==================================================
🌍 스마트 여행 올인원 플래너 여행 리포트
==================================================
- 목적지: {place_name} ({addr_name})
- 현지 좌표: 위도 {lat:.4f}, 경도 {lng:.4f}
- 현지 일출/일몰: 일출 {sun_info['sunrise'] if sun_info else '-'} / 일몰 {sun_info['sunset'] if sun_info else '-'}
- 현재 기온: {weather['temp'] if weather else '-'}°C ({weather['desc'] if weather else '-'})

--------------------------------------------------
[🎒 여행 준비물 체크 현황]
--------------------------------------------------
[완료된 항목]
{chr(10).join(['  - [V] ' + i for i in checked_items]) if checked_items else '  (없음)'}

[챙겨야 할 항목]
{chr(10).join(['  - [ ] ' + i for i in unchecked_items]) if unchecked_items else '  (모두 챙김!)'}

--------------------------------------------------
[📝 여행 일정 및 메모]
--------------------------------------------------
{st.session_state.travel_memo}
==================================================
"""
        st.download_button(
            label="💾 여행 플랜 텍스트 파일(.txt) 다운로드",
            data=report_text,
            file_name=f"{place_name}_여행플랜.txt",
            mime="text/plain",
            use_container_width=True
        )
        st.caption("비행기 안이나 오프라인 환경에서 열람할 수 있도록 텍스트 파일로 저장됩니다.")