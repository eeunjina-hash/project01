import streamlit as st

# 1. page_icon에 이모지 문자열 추가
st.set_page_config(page_title="세계여행 포털", page_icon="🌍")

# 2. st.page -> st.Page (대문자 P)
home_page = st.Page("view/home.py", title="홈", icon="🏠", default=True)

# 3. icon에 국가 코드 대신 실제 국기 이모지 적용
usa = st.Page("view/usa.py", title="미국", icon="🇺🇸")
china = st.Page("view/china.py", title="중국", icon="🇨🇳")

# 4. japan== -> japan = (등호 1개로 변수 할당)
japan = st.Page("view/japan.py", title="일본", icon="🇯🇵")

# 네비게이션 메뉴 가동 (사이드바 메뉴 자동 생성)
pg = st.navigation([home_page, usa, china, japan])
pg.run()