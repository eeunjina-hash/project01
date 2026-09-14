import streamlit as st
import os
from src.utils.data import COUNTRIES_DATA

st.set_page_config(
    page_title="Global Travel Hub",
    page_icon="✈️",
    layout="wide"
)

# 사이드바 메뉴 네비게이션
st.sidebar.title("🌍 국가 선택")
selected_country = st.sidebar.radio(
    "이동할 국가를 선택하세요:",
    options=list(COUNTRIES_DATA.keys()),
    index=0
)

# 선택된 국가 데이터 추출 (data.py에서 가져온 데이터 사용)
data = COUNTRIES_DATA[selected_country]

# 메인 콘텐츠 헤더
if selected_country == "대한민국":
    st.title("🇰🇷 대한민국 (Home)")
    st.caption("대한민국 여행 가이드 및 주요 국가 허브")
else:
    flags = {"일본": "🇯🇵", "중국": "🇨🇳", "미국": "🇺🇸"}
    st.title(f"{flags.get(selected_country, '🌐')} {selected_country} 여행 정보")

st.markdown("---")

# 좌우 2단 레이아웃
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("📌 국가 기본 정보")
    st.markdown(f"""
    * **수도:** {data['capital']}
    * **공용 화폐:** {data['currency']}
    * **공용 언어:** {data['language']}
    """)
    st.write(data["description"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    # 공식 사이트 외부 링크 버튼
    st.link_button(
        label=f"🔗 {selected_country} 공식 관광청 바로가기",
        url=data["official_site"],
        type="primary"
    )

with col2:
    # 상위 폴더의 images 디렉터리 이미지 경로 참조
    img_path = f"images/{data['image_key']}.jpg"
    if os.path.exists(img_path):
        st.image(img_path, caption=f"{selected_country} 대표 이미지", use_container_width=True)
    else:
        st.info(f"💡 `{img_path}` 경로에 이미지를 넣으면 화면에 표시됩니다.")