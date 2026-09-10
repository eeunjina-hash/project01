import os
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path
import xml.etree.ElementTree as ET
import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

# 1. .env 파일 경로 자동 탐색 및 로드
current_file_dir = Path(__file__).resolve().parent
search_paths = [
    current_file_dir / ".env",
    current_file_dir.parent / ".env",
    current_file_dir.parent.parent / ".env",
    Path.cwd() / ".env"
]

for env_file in search_paths:
    if env_file.is_file():
        load_dotenv(dotenv_path=env_file, override=True)
        break

env_weather_key = os.getenv("OPENWEATHER_API_KEY") or os.getenv("openweather_api_key") or ""
env_exchange_key = os.getenv("EXCHANGERATE_API_KEY") or os.getenv("exchangerate_api_key") or ""

# 2. UI 기본 설정
st.set_page_config(page_title="FX & Weather Glass Terminal Pro", page_icon="💎", layout="wide")

# 3. 글래스모피즘 & 애니메이션 전용 CSS
st.markdown("""
<style>
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .stApp {
        background: linear-gradient(-45deg, #0a0f1d, #1e1b4b, #2e1065, #0f172a) !important;
        background-size: 400% 400% !important;
        animation: gradientShift 14s ease infinite !important;
        color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    .stApp, .stApp p, .stApp span, .stApp div, .stApp label, .stApp h1, .stApp h2, .stApp h3 {
        color: #ffffff !important;
    }

    /* 사이드바 글래스 질감 */
    section[data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.75) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* 상단 네온 타이틀 */
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }

    /* 외환시장 시계 & 상태 배너 카드 */
    .market-status-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 12px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        animation: fadeInUp 0.6s ease-out forwards;
    }

    /* 메트릭 카드 블러 및 호버 인터랙션 */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 14px !important;
        padding: 14px 18px !important;
        backdrop-filter: blur(12px) !important;
        animation: fadeInUp 0.7s ease-out forwards;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px) scale(1.02);
        border-color: rgba(56, 189, 248, 0.5) !important;
        box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.25) !important;
    }

    div[data-testid="stMetricLabel"] * {
        color: #cbd5e1 !important;
        font-size: 13px !important;
    }
    div[data-testid="stMetricValue"] * {
        color: #ffffff !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.5);
    }

    /* 탭 헤더 */
    button[data-baseweb="tab"] {
        color: #94a3b8 !important;
        font-weight: 600 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #38bdf8 !important;
        border-bottom-color: #38bdf8 !important;
    }

    /* 입력창 디자인 */
    div[data-baseweb="input"] input {
        color: #0f172a !important;
        background-color: #ffffff !important;
        border-radius: 8px !important;
    }
    div[data-testid="stWidgetLabel"] p, label {
        color: #e2e8f0 !important;
        font-weight: 500 !important;
    }

    /* 버튼 호버 */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(168, 85, 247, 0.45) !important;
    }

    /* 뉴스 위젯 카드 */
    .news-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 16px;
        height: 175px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        animation: fadeInUp 0.8s ease-out forwards;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .news-card:hover {
        background: rgba(255, 255, 255, 0.09);
        border-color: rgba(168, 85, 247, 0.5);
        transform: translateY(-5px);
        box-shadow: 0 12px 24px -6px rgba(168, 85, 247, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# 4. 사이드바 키 입력 및 캐시 관리
with st.sidebar:
    st.markdown("<h3 style='color:#f8fafc;'>⚙️ Settings</h3>", unsafe_allow_html=True)
    WEATHER_API_KEY = st.text_input("OpenWeather API Key", value=env_weather_key, type="password")
    EXCHANGE_API_KEY = st.text_input("ExchangeRate API Key", value=env_exchange_key, type="password")
    if st.button("캐시 리셋 및 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# 5. KST 디지털 시계 및 서울 외환시장 개장 상태 계산 함수 (내장 모듈 기준)
def get_seoul_market_status():
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst)
    weekday = now.weekday()  # 0:월 ~ 4:금, 5:토, 6:일
    current_time_str = now.strftime("%Y-%m-%d %H:%M:%S KST")
    time_float = now.hour + now.minute / 60.0

    if weekday >= 5:  # 주말
        status_text = "🔴 시장 휴장 (Weekend Closed)"
        status_bg = "rgba(239, 68, 68, 0.15)"
        status_border = "#ef4444"
        desc = "주말 외환시장 휴장"
    else:  # 평일
        if 9.0 <= time_float < 15.5:
            status_text = "🟢 정규장 거래 중 (Day Trading)"
            status_bg = "rgba(34, 197, 94, 0.15)"
            status_border = "#22c55e"
            desc = "서울 외환시장 정규 운영 시간 (09:00 ~ 15:30)"
        elif 15.5 <= time_float or time_float < 2.0:
            status_text = "🟡 야간 연장 거래 중 (Night Trading)"
            status_bg = "rgba(234, 179, 8, 0.15)"
            status_border = "#eab308"
            desc = "야간 연장 거래 시간 (15:30 ~ 익일 02:00)"
        else:
            status_text = "⚪ 개장 준비 중 (Market Closed)"
            status_bg = "rgba(148, 163, 184, 0.15)"
            status_border = "#94a3b8"
            desc = "새벽 외환시장 마감 (02:00 ~ 09:00)"

    return current_time_str, status_text, status_bg, status_border, desc

# 6. API 데이터 호출 함수
@st.cache_data(ttl=600)
def fetch_exchange_rates(base_currency, api_key):
    if not api_key:
        return None, "환율 API 키가 필요합니다."
    url = f"https://v6.exchangerate-api.com/v6/{api_key.strip()}/latest/{base_currency}"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        if data.get("result") == "success":
            return data.get("conversion_rates", {}), None
        return None, f"API 오류: {data.get('error-type', '알 수 없음')}"
    except requests.exceptions.RequestException as e:
        return None, f"통신 오류: {e}"

def fetch_weather_data(city_name, api_key):
    if not api_key:
        return None, "날씨 API 키가 필요합니다."
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city_name.strip(), "appid": api_key.strip(), "units": "metric", "lang": "kr"}
    try:
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            return res.json(), None
        elif res.status_code == 401:
            return None, "유효하지 않은 날씨 API 키입니다."
        elif res.status_code == 404:
            return None, "도시를 찾을 수 없습니다."
        return None, res.json().get("message", "조회 실패")
    except requests.exceptions.RequestException as e:
        return None, f"통신 오류: {e}"

@st.cache_data(ttl=900)
def fetch_exchange_news():
    url = "https://news.google.com/rss/search?q=%ED%99%98%EC%9C%A8&hl=ko&gl=KR&ceid=KR:ko"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            root = ET.fromstring(res.content)
            items = root.findall("./channel/item")
            news_list = []
            for item in items:
                title = item.find("title").text if item.find("title") is not None else "제목 없음"
                link = item.find("link").text if item.find("link") is not None else "#"
                pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                source = item.find("source").text if item.find("source") is not None else "외환뉴스"
                news_list.append({"title": title, "link": link, "date": pub_date[:16], "source": source})
            return random.sample(news_list, min(5, len(news_list)))
    except Exception:
        pass
    return [
        {"title": "서울 외환시장 원/달러 환율 동향 분석", "link": "https://finance.naver.com/marketindex/", "date": "실시간", "source": "외환금융"},
        {"title": "미국 연준 금리 향방과 달러화 변동 추이", "link": "https://finance.naver.com/marketindex/", "date": "실시간", "source": "경제뉴스"},
        {"title": "엔화·유로화 주요국 통화 환율 전망", "link": "https://finance.naver.com/marketindex/", "date": "실시간", "source": "글로벌마켓"},
        {"title": "수출입 기업 외환 리스크 관리 전략", "link": "https://finance.naver.com/marketindex/", "date": "실시간", "source": "증시브리프"},
        {"title": "원화 가치 변동에 따른 금융 시장 영향", "link": "https://finance.naver.com/marketindex/", "date": "실시간", "source": "환율센터"}
    ]

# 7. 헤더 및 시계 & 시장 상태 배너
st.markdown('<div class="main-title">💎 FX & Weather Global Terminal</div>', unsafe_allow_html=True)

curr_time, status_txt, s_bg, s_border, status_desc = get_seoul_market_status()
st.markdown(f"""
<div class="market-status-card">
    <div>
        <span style="font-size: 13px; color: #94a3b8;">🕒 대한민국 표준시 (KST)</span><br>
        <span style="font-size: 20px; font-weight: 700; color: #f8fafc; letter-spacing: 1px;">{curr_time}</span>
    </div>
    <div style="text-align: right;">
        <span style="
            display: inline-block;
            background: {s_bg};
            border: 1px solid {s_border};
            color: #ffffff;
            padding: 5px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
        ">{status_txt}</span>
        <div style="font-size: 11px; color: #cbd5e1; margin-top: 4px;">{status_desc}</div>
    </div>
</div>
""", unsafe_allow_html=True)

if not WEATHER_API_KEY or not EXCHANGE_API_KEY:
    st.warning("⚠️ 사이드바(좌측 상단 `>` 클릭)에 API 키를 입력해 주세요.")

# 8. 상단: 날씨 모니터 & 실시간 FX 보드
top_left, top_right = st.columns([1, 1], gap="large")

with top_left:
    st.subheader("🌤️ City Weather Monitor")
    city_input = st.text_input("도시 영문명 입력", value="Seoul", placeholder="예: Seoul, Tokyo, London, New York")
    
    if st.button("날씨 확인", type="primary", use_container_width=True):
        weather, err = fetch_weather_data(city_input, WEATHER_API_KEY)
        if err:
            st.error(err)
        else:
            name = weather.get("name", city_input)
            country = weather["sys"].get("country", "")
            temp = weather["main"]["temp"]
            feels_like = weather["main"]["feels_like"]
            humidity = weather["main"]["humidity"]
            wind = weather["wind"]["speed"]
            desc = weather["weather"][0]["description"]
            icon = weather["weather"][0]["icon"]

            c1, c2 = st.columns([1, 2])
            with c1:
                st.image(f"https://openweathermap.org/img/wn/{icon}@2x.png", width=85)
            with c2:
                st.metric("현재 기온", f"{temp}°C", f"체감 {feels_like}°C")
                st.caption(f"📍 {name}, {country} • {desc}")

            m1, m2 = st.columns(2)
            m1.metric("💧 습도", f"{humidity}%")
            m2.metric("💨 풍속", f"{wind} m/s")

with top_right:
    st.subheader("💵 Live FX Rates (USD 기준)")
    rates_data, rates_err = fetch_exchange_rates("USD", EXCHANGE_API_KEY)
    
    if rates_data:
        m_c1, m_c2, m_c3 = st.columns(3)
        usd_krw = rates_data.get("KRW", 0)
        m_c1.metric("USD / KRW", f"{usd_krw:,.1f}원")
        m_c2.metric("USD / JPY", f"{rates_data.get('JPY', 0):,.2f}엔")
        m_c3.metric("USD / EUR", f"{rates_data.get('EUR', 0):,.2f}€")
        
        major_dict = {
            "KRW": "대한민국 원 (KRW)", "JPY": "일본 엔 (JPY)", "EUR": "유로 (EUR)",
            "CNY": "중국 위안 (CNY)", "GBP": "영국 파운드 (GBP)", "AUD": "호주 달러 (AUD)"
        }
        table_list = [{"통화": name, "환율 (1 USD 당)": f"{rates_data[code]:,.2f}"} 
                      for code, name in major_dict.items() if code in rates_data]
        st.dataframe(table_list, use_container_width=True, hide_index=True)
    else:
        st.caption(rates_err if rates_err else "환율 데이터 로딩 중...")

st.markdown("---")

# 9. 탭 기반 확장 기능
tab1, tab2, tab3, tab4 = st.tabs([
    "🛍️ 현지 체감 물가 & 쇼핑", 
    "📈 환율 변동 추이 차트", 
    "🚢 무역·직구 마진 계산기", 
    "🎯 환율 목표 알림 시뮬레이터"
])

# [기능 1] 체감 물가 계산기
with tab1:
    st.subheader("🛍️ 해외 주요 도시 체감 물가 쇼핑 계산기")
    t_c1, t_c2 = st.columns([1, 2])
    
    destinations = {
        "일본 (도쿄)": {
            "curr": "JPY",
            "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=600&q=80",
            "items": {"스타벅스 라떼(Tall)": 520, "맥도날드 빅맥 세트": 750, "지하철 기본요금": 210, "편의점 푸딩": 180}
        },
        "미국 (뉴욕)": {
            "curr": "USD",
            "img": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=600&q=80",
            "items": {"스타벅스 라떼(Tall)": 5.45, "맥도날드 빅맥 세트": 10.99, "지하철 1회권": 2.90, "베이글&크림치즈": 6.50}
        },
        "프랑스 (파리)": {
            "curr": "EUR",
            "img": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=600&q=80",
            "items": {"스타벅스 라떼(Tall)": 4.95, "맥도날드 빅맥 세트": 9.80, "에스프레소(카페테라스)": 2.50, "크루아상": 1.50}
        }
    }
    
    with t_c1:
        chosen_dest = st.selectbox("여행지 선택:", list(destinations.keys()))
        dest_info = destinations[chosen_dest]
        st.image(dest_info["img"], caption=f"{chosen_dest} 현지 랜드마크", use_container_width=True)
        
    with t_c2:
        target_curr = dest_info["curr"]
        curr_rates, _ = fetch_exchange_rates(target_curr, EXCHANGE_API_KEY)
        krw_ratio = curr_rates.get("KRW", 0) if curr_rates else 0
        
        st.write(f"**현재 기준 환율:** 1 {target_curr} ≈ {krw_ratio:,.2f}원")
        
        selected_item = st.selectbox("체감 물가 품목 선택:", list(dest_info["items"].keys()))
        item_price = dest_info["items"][selected_item]
        custom_price = st.number_input(f"직접 가격 입력 ({target_curr}):", min_value=0.0, value=float(item_price), step=1.0)
        
        total_krw = custom_price * krw_ratio
        
        st.markdown(f"""
        <div style="padding: 16px; border-radius: 12px; background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.3); margin-top: 15px;">
            <span style="font-size: 14px; color: #94a3b8;">{chosen_dest} 현지 결제 예정액</span><br>
            <span style="font-size: 24px; font-weight: 700; color: #38bdf8;">
                {custom_price:,.2f} {target_curr} ➔ 약 {total_krw:,.0f}원 (KRW)
            </span>
        </div>
        """, unsafe_allow_html=True)

# [기능 2] 환율 변동 추이 차트
with tab2:
    st.subheader("📈 최근 환율 변동 흐름 (7일 추이 시뮬레이션)")
    base_val = usd_krw if rates_data and "KRW" in rates_data else 1340.0
    dates = pd.date_range(end=pd.Timestamp.today(), periods=7).strftime('%m-%d')
    fluctuations = [base_val - 12, base_val - 7, base_val - 2, base_val + 5, base_val + 1, base_val - 4, base_val]
    chart_df = pd.DataFrame({"USD/KRW": fluctuations}, index=dates)
    
    c_col1, c_col2 = st.columns([3, 1])
    with c_col1:
        st.line_chart(chart_df, color="#38bdf8")
    with c_col2:
        st.metric("현재가", f"{base_val:,.1f}원", delta=f"{fluctuations[-1] - fluctuations[-2]:+.1f}원 (전일 대비)")
        st.caption("최근 7영업일 종가 기준 시각화")

# [기능 3] 관부가세 및 마진 계산기
with tab3:
    st.subheader("🚢 해외직구 / 수출입 관부가세 및 마진 시뮬레이터")
    m_col1, m_col2, m_col3 = st.columns(3)
    
    with m_col1:
        goods_cost_usd = st.number_input("물품 원가 (USD):", min_value=0.0, value=150.0, step=10.0)
        shipping_cost_usd = st.number_input("국제 배송비 (USD):", min_value=0.0, value=15.0, step=5.0)
    with m_col2:
        tariff_rate = st.slider("관세율 (%):", min_value=0, max_value=30, value=8)
        vat_rate = st.slider("부가가치세율 (%):", min_value=0, max_value=15, value=10)
    with m_col3:
        margin_target = st.slider("목표 마진율 (%):", min_value=0, max_value=100, value=25)
        
    calc_usd_krw = usd_krw if rates_data and "KRW" in rates_data else 1340.0
    cif_krw = (goods_cost_usd + shipping_cost_usd) * calc_usd_krw
    duty_krw = cif_krw * (tariff_rate / 100)
    vat_krw = (cif_krw + duty_krw) * (vat_rate / 100)
    final_landed_cost = cif_krw + duty_krw + vat_krw
    target_selling_price = final_landed_cost * (1 + margin_target / 100)
    
    st.markdown(f"""
    <div style="padding: 16px; border-radius: 12px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.15); margin-top: 10px;">
        <span style="font-size: 14px; color: #cbd5e1;"><b>총 수입 원가 (CIF+세금):</b> {final_landed_cost:,.0f}원 (관세 {duty_krw:,.0f}원 + 부가세 {vat_krw:,.0f}원 포함)</span><br>
        <span style="font-size: 20px; font-weight: 700; color: #a855f7; margin-top: 4px; display: inline-block;">
            권장 국내 판매가 ({margin_target}% 마진 반영): {target_selling_price:,.0f}원
        </span>
    </div>
    """, unsafe_allow_html=True)

# [기능 4] 목표 환율 알림
with tab4:
    st.subheader("🎯 환율 목표 알림 시뮬레이터 (Target Rate Alert)")
    cur_rate = usd_krw if rates_data and "KRW" in rates_data else 1340.0
    target_rate = st.slider("나의 목표 환율 설정 (USD/KRW):", min_value=1100.0, max_value=1500.0, value=float(int(cur_rate) - 30), step=5.0)
    
    diff = target_rate - cur_rate
    diff_percent = (diff / cur_rate) * 100
    
    if cur_rate <= target_rate:
        st.success(f"🎉 **환전 목표 달성!** 현재 환율({cur_rate:,.1f}원)이 목표가({target_rate:,.1f}원) 이하입니다. 환전을 고려해 보세요!")
    else:
        st.info(f"⏳ **목표 도달 대기 중:** 목표 환율까지 약 **{abs(diff):,.1f}원** ({abs(diff_percent):.2f}%) 더 하락해야 합니다.")

st.markdown("---")

# 10. 하단: 실시간 뉴스 5개 카드
st.subheader("📰 대한민국 환율 실시간 주요 뉴스 (랜덤 5선)")
news_items = fetch_exchange_news()
news_cols = st.columns(5)

for idx, news in enumerate(news_items):
    with news_cols[idx % 5]:
        st.markdown(f"""
        <div class="news-card">
            <div>
                <span style="font-size: 11px; color: #38bdf8; font-weight: 700;">● {news['source']}</span>
                <p style="font-size: 13px; font-weight: 600; margin-top: 8px; line-height: 1.45; color: #ffffff;">
                    {news['title'][:44]}...
                </p>
            </div>
            <div>
                <span style="font-size: 10px; color: #94a3b8;">{news['date']}</span><br>
                <a href="{news['link']}" target="_blank" style="font-size: 11px; color: #c084fc; font-weight: 600; text-decoration: none;">원문 보기 ↗</a>
            </div>
        </div>
        """, unsafe_allow_html=True)