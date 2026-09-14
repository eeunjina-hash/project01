import streamlit as st

st.set_page_config(page_title="세계 여행 포털", page_icon="🌍", layout="centered")

# 사이드바 메뉴 (오타 수정: siderbar -> sidebar)
menu = st.sidebar.radio("메뉴", ["홈", "미국", "중국", "일본"])

# 1. 홈 (대한민국)
if menu == "홈":
    st.title("🇰🇷 대한민국 (Republic of Korea)")
    st.write(
        "대한민국은 동아시아에 위치한 나라로, 유구한 역사와 현대적인 문화가 공존하는 곳입니다. "
        "사계절의 변화가 뚜렷하며, K-컬처와 다채로운 미식, 아름다운 자연경관을 자랑합니다."
    )
    st.link_button(
        "대한민국 관광공사 방문하기",
        "https://korean.visitkorea.or.kr",
        type="primary",
    )

# 2. 미국
elif menu == "미국":
    st.title("🇺🇸 미국 (United States of America)")
    st.write(
        "북아메리카 대륙의 50개 주와 1개 특별구로 이루어진 광대한 연방 국가입니다. "
        "뉴욕, LA 같은 글로벌 대도시부터 그랜드 캐니언, 옐로스톤 등 웅장한 국립공원까지 다양한 매력을 지니고 있습니다."
    )
    st.link_button(
        "미국 공식 관광청 방문하기 (GoUSA)", "https://www.gousa.or.kr"
    )

# 3. 중국
elif menu == "중국":
    st.title("🇨🇳 중국 (People's Republic of China)")
    st.write(
        "세계에서 가장 긴 역사를 자랑하는 문명 발상지 중 하나입니다. "
        "만리장성, 자금성 등 유서 깊은 세계문화유산과 상하이, 선전 등 첨단 현대 도시가 어우러져 있습니다."
    )
    st.link_button(
        "중국 공식 관광 안내 사이트 방문하기", "https://www.travelchina.gov.cn"
    )

# 4. 일본
elif menu == "일본":
    st.title("🇯🇵 일본 (Japan)")
    st.write(
        "동아시아 열도에 위치한 섬나라로, 전통적인 신사와 정원부터 현대적인 쇼핑과 애니메이션 문화까지 고루 갖추고 있습니다. "
        "도쿄, 오사카, 후쿠오카, 교토 등 도시마다 개성 있는 미식과 온천 문화를 즐길 수 있습니다."
    )
    st.link_button(
        "일본 정부 관광국(JNTO) 방문하기", "https://www.japan.travel/ko/kr/"
    )