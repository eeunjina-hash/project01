import os
from pathlib import Path
import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv
import pandas as pd

# ==========================================
# 1. 환경 설정 및 API 키 로드 (로컬 + 클라우드 겸용)
# ==========================================
st.set_page_config(
    page_title="스마트 여행 올인원 플래너",
    page_icon="✈️",
    layout="wide"
)

# 로컬 환경용 .env 로드
current_dir = Path(__file__).resolve().parent
parent_env_path = current_dir.parent / '.env'
if parent_env_path.exists():
    load_dotenv(dotenv_path=parent_env_path)

# [배포 필수] Streamlit Cloud Secrets 우선 조회 후 os.getenv 탐색
# [수정] secrets 파일이 없어도 에러 없이 .env로 넘어가는 안전 함수
def get_env_or_secret(key_name):
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        # secrets.toml 파일이 없는 로컬 환경에서는 예외를 무시하고 통과
        pass
    return os.getenv(key_name)

KAKAO_KEY = get_env_or_secret("KAKAO_REST_API_KEY")
WEATHER_KEY = get_env_or_secret("OPENWEATHER_API_KEY")
EXCHANGE_KEY = get_env_or_secret("EXCHANGERATE_API_KEY")
KAKAO_KEY = get_env_or_secret("KAKAO_REST_API_KEY")
WEATHER_KEY = get_env_or_secret("OPENWEATHER_API_KEY")
EXCHANGE_KEY = get_env_or_secret("EXCHANGERATE_API_KEY")

# ==========================================
# 2. API 연동 함수 정의 (국내 + 해외 하이브리드)
# ==========================================

# (1) 국내/해외 통합 위치 검색 (카카오 1차 -> Nominatim 2차)
def search_global_place(query, kakao_key):
    if kakao_key:
        headers = {"Authorization": f"KakaoAK {kakao_key}"}
        try:
            url = "https://dapi.kakao.com/v2/local/search/keyword.json"
            res = requests.get(url, headers=headers, params={"query": query, "size": 1}, timeout=3)
            if res.status_code == 200 and res.json().get("documents"):
                doc = res.json()["documents"][0]
                return float(doc["y"]), float(doc["x"]), doc["place_name"], doc.get("address_name", ""), "KR"
            
            url_addr = "https://dapi.kakao.com/v2/local/search/address.json"
            res_addr = requests.get(url_addr, headers=headers, params={"query": query, "size": 1}, timeout=3)
            if res_addr.status_code == 200 and res_addr.json().get("documents"):
                doc = res_addr.json()["documents"][0]
                return float(doc["y"]), float(doc["x"]), doc["address_name"], doc["address_name"], "KR"
        except Exception:
            pass

    try:
        nom_url = "https://nominatim.openstreetmap.org/search"
        nom_headers = {"User-Agent": "MyTravelPlannerApp/1.0"}
        nom_params = {
            "q": query,
            "format": "json",
            "limit": 1,
            "accept-language": "ko,en"
        }
        nom_res = requests.get(nom_url, headers=nom_headers, params=nom_params, timeout=5)
        if nom_res.status_code == 200 and nom_res.json():
            doc = nom_res.json()[0]
            lat = float(doc["lat"])
            lng = float(doc["lon"])
            full_name = doc.get("display_name", "")
            short_name = full_name.split(",")[0].strip()
            return lat, lng, short_name, full_name, "GLOBAL"
    except Exception:
        pass

    return None, None, None, None, None

# (2) 카카오 REST API: 카테고리별 주변 시설 검색 (국내 전용)
def search_category_places(lat, lng, category_code, api_key, radius=1500, size=5):
    if not api_key:
        return []
    url = "https://dapi.kakao.com/v2/local/search/category.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {
        "category_group_code": category_code,
        "x": str(lng),
        "y": str(lat),
        "radius": radius,
        "size": size
    }
    try:
        res = requests.get(url, headers=headers, params=params, timeout=3)
        if res.status_code == 200:
            return res.json().get("documents", [])
    except Exception:
        pass
    return []

# (3) OpenWeatherMap API: 현재 날씨 조회
def get_weather_data(lat, lon, api_key):
    if not api_key:
        return None
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",
        "lang": "kr"
    }
    try:
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            data = res.json()
            return {
                "temp": round(data["main"]["temp"], 1),
                "feels_like": round(data["main"]["feels_like"], 1),
                "humidity": data["main"]["humidity"],
                "desc": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"],
                "wind": data["wind"]["speed"]
            }
    except Exception:
        pass
    return None

# (4) OpenWeatherMap API: 5일간 예보 데이터 수집
def get_weather_forecast(lat, lon, api_key):
    if not api_key:
        return None
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",
        "lang": "kr"
    }
    try:
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            list_data = res.json().get("list", [])
            records = []
            for item in list_data:
                records.append({
                    "시간": item["dt_txt"][5:16],
                    "기온(°C)": round(item["main"]["temp"], 1),
                    "날씨": item["weather"][0]["description"]
                })
            return pd.DataFrame(records)
    except Exception:
        pass
    return None

# (5) 실시간 환율 조회
@st.cache_data(ttl=3600)
def get_exchange_rates(base_currency="KRW", api_key=None):
    headers = {"User-Agent": "Mozilla/5.0"}
    if api_key:
        try:
            url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200 and "conversion_rates" in res.json():
                return res.json()["conversion_rates"]
            elif res.status_code == 200 and "rates" in res.json():
                return res.json()["rates"]
        except Exception:
            pass

    try:
        url = f"https://open.er-api.com/v6/latest/{base_currency}"
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200 and "rates" in res.json():
            return res.json()["rates"]
    except Exception:
        pass

    try:
        url = f"https://api.frankfurter.dev/v1/latest?from={base_currency}"
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200 and "rates" in res.json():
            rates = res.json()["rates"]
            rates[base_currency] = 1.0
            return rates
    except Exception:
        pass

    return {}

# ==========================================
# 3. 사이드바 구성 (여행 설정 & 환율 계산기)
# ==========================================
with st.sidebar:
    st.header("🧳 여행 관리 도구")
    
    st.subheader("📍 목적지 검색")
    destination_input = st.text_input(
        "국내 또는 해외 여행지를 입력하세요", 
        value="도쿄 타워"
    )
    
    st.markdown("---")
    st.subheader("💵 실시간 환율 계산기")
    
    rates = get_exchange_rates("KRW", EXCHANGE_KEY)
    
    if rates:
        target_currency = st.selectbox(
            "목표 통화 선택",
            options=["USD", "JPY", "EUR", "CNY", "VND", "THB", "TWD", "GBP"],
            index=1
        )
        
        krw_amount = st.number_input("금액 (KRW 원)", min_value=1000, value=100000, step=10000)
        
        rate = rates.get(target_currency, 0)
        if rate > 0:
            converted = krw_amount * rate
            st.metric(
                label=f"환전 환산액 ({target_currency})",
                value=f"{converted:,.2f} {target_currency}"
            )
            base_rate = 1 / rate
            if target_currency in ["JPY", "VND"]:
                st.caption(f"기준 환율: 100{target_currency} = {base_rate * 100:,.2f}원")
            else:
                st.caption(f"기준 환율: 1 {target_currency} = {base_rate:,.2f}원")
    else:
        st.warning("환율 데이터를 불러오는 중 오류가 발생했습니다.")

# ==========================================
# 4. 메인 대시보드 화면
# ==========================================
st.title("🌍 스마트 여행 올인원 플래너")
st.caption("국내 및 해외 전 세계 지도 탐색, 실시간 날씨 예보 및 환율·준비물 관리 시스템")

lat, lng, place_name, addr_name, location_type = search_global_place(destination_input, KAKAO_KEY)

if not lat or not lng:
    st.error(f"'{destination_input}'의 위치 정보를 찾을 수 없습니다. 영문 표기(예: Tokyo Tower, Paris)나 정확한 명칭으로 다시 검색해보세요.")
    st.stop()

weather = get_weather_data(lat, lng, WEATHER_KEY)

# 상단 요약 카드
col1, col2, col3, col4 = st.columns(4)
with col1:
    region_tag = " [국내]" if location_type == "KR" else " [해외]"
    st.metric(label="선택 목적지", value=f"{place_name}{region_tag}")
with col2:
    if weather:
        st.metric(label="현재 기온", value=f"{weather['temp']}°C", delta=f"체감 {weather['feels_like']}°C")
    else:
        st.metric(label="현재 기온", value="날씨 키 필요")
with col3:
    if weather:
        st.metric(label="날씨 상태", value=weather['desc'].capitalize())
    else:
        st.metric(label="날씨 상태", value="연동 대기")
with col4:
    if rates and 'target_currency' in locals():
        current_rate = 1 / rates.get(target_currency, 1)
        unit = 100 if target_currency in ["JPY", "VND"] else 1
        st.metric(label=f"{target_currency} 환율 ({unit}{target_currency})", value=f"{current_rate * unit:,.1f}원")

st.markdown("---")

tab_map, tab_weather, tab_currency, tab_checklist = st.tabs([
    "🗺️ 지도 & 핫플 탐색", 
    "☀️ 날씨 & 5일 예보", 
    "📊 환율 분석", 
    "📝 여행 준비물 & 메모"
])

# TAB 1: 지도 및 핫플
with tab_map:
    col_addr, col_btn = st.columns([3, 1])
    with col_addr:
        st.markdown(f"**상세 주소:** {addr_name}")
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
        st.info("💡 해외 지역은 구글맵 길찾기와 글로벌 Folium 지도 마커를 기본 제공합니다.")

    m = folium.Map(location=[lat, lng], zoom_start=14)
    
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

# TAB 2: 날씨 상세 및 5일 예보
with tab_weather:
    if weather:
        w1, w2 = st.columns([1, 2])
        with w1:
            icon_url = f"https://openweathermap.org/img/wn/{weather['icon']}@4x.png"
            st.image(icon_url, width=130)
            st.subheader(weather['desc'].capitalize())
        with w2:
            st.write(f"- **현재 기온:** {weather['temp']}°C (체감: {weather['feels_like']}°C)")
            st.write(f"- **습도:** {weather['humidity']}% | **풍속:** {weather['wind']} m/s")
            
            if weather['temp'] >= 27:
                outfit = "민소매, 반팔, 린넨 옷, 자외선 차단제"
            elif weather['temp'] >= 20:
                outfit = "얇은 가디건, 반팔 티셔츠, 면바지"
            elif weather['temp'] >= 12:
                outfit = "자켓, 셔츠, 가디건, 간절기 외투"
            elif weather['temp'] >= 6:
                outfit = "코트, 가죽 자켓, 니트, 히트텍"
            else:
                outfit = "패딩, 목도리, 장갑, 방한 의류"
            st.info(f"💡 **추천 옷차림:** {outfit}")

        st.markdown("---")
        st.subheader("📈 향후 5일간 기온 추이 예보")
        forecast_df = get_weather_forecast(lat, lng, WEATHER_KEY)
        if forecast_df is not None and not forecast_df.empty:
            chart_data = forecast_df.set_index("시간")[["기온(°C)"]]
            st.line_chart(chart_data)
            with st.expander("⏱️ 상세 3시간 단위 예보표 보기"):
                st.dataframe(forecast_df, use_container_width=True)
    else:
        st.info("`.env` 파일에 `OPENWEATHER_API_KEY`를 등록하면 실시간 날씨 및 5일 예보 차트가 활성화됩니다.")

# TAB 3: 통화 및 환전 팁
with tab_currency:
    st.subheader("주요 여행 국가 실시간 환율 비교표")
    if rates:
        target_list = ["USD", "JPY", "EUR", "CNY", "VND", "THB", "GBP"]
        curr_data = []
        for code in target_list:
            r = rates.get(code)
            if r:
                unit = 100 if code in ["JPY", "VND"] else 1
                krw_val = (1 / r) * unit
                curr_data.append({
                    "통화": code,
                    "기준 단위": f"{unit} {code}",
                    "원화 환산 금액 (KRW)": f"{krw_val:,.2f}원"
                })
        st.table(curr_data)
        st.caption("* 환율 정보는 1시간 주기로 자동 캐싱 및 갱신됩니다.")

# TAB 4: 여행 준비물 체크리스트 & 메모장
with tab_checklist:
    col_check, col_memo = st.columns(2)
    
    with col_check:
        st.subheader("✅ 여행 필수 준비물 체크리스트")
        if "checklist" not in st.session_state:
            st.session_state.checklist = {
                "여권 및 신분증 지참": True,
                "비행기/열차 E-티켓 발권 확인": False,
                "현지 통화 환전 또는 트래블카드 준비": False,
                "보조배터리 및 국가별 110V/220V 어댑터": False,
                "상비약 (감기약, 소화제, 진통제)": False,
                "해외 로밍 / eSIM / 유심 구매 확인": False,
                "여행자 보험 가입 여부 체크": False
            }
            
        for item, checked in list(st.session_state.checklist.items()):
            new_val = st.checkbox(item, value=checked, key=f"chk_{item}")
            st.session_state.checklist[item] = new_val
            
        new_item = st.text_input("새 준비물 항목 추가", placeholder="예: 비짓재팬 등록, 비옷")
        if st.button("추가하기"):
            if new_item and new_item not in st.session_state.checklist:
                st.session_state.checklist[new_item] = False
                st.rerun()

    with col_memo:
        st.subheader("📝 여행 일정 & 지출 메모장")
        if "travel_memo" not in st.session_state:
            st.session_state.travel_memo = "1일차: 공항 도착 후 호텔 체크인 & 주변 명소 둘러보기\n예산 메모: 1일 식비 5,000엔 / 교통카드 충전"
            
        memo_content = st.text_area(
            "자유롭게 여행 계획과 예산을 메모하세요 (새로고침 시에도 유지)",
            value=st.session_state.travel_memo,
            height=280
        )
        st.session_state.travel_memo = memo_content
        st.success("메모가 세션에 안전하게 저장되었습니다.")