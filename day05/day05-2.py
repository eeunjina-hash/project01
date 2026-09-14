# openAI + streamlit 앱
# 질문 하나 입력하면 OpenAI chat Completions API 한번 호출
# 답변을 받아오는 가장 단순한 방법
# 대화 기록을 기억하지 않는 단발성 질문-답변
# 실행 방법: streamlit run day05-2.py

import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="나의 첫번째 챗봇", page_icon="💕")
st.title("예제1) 나의 첫번째 챗봇")
st.caption(
    "질문 하나 입력하면 openai chat completion api 한번 호출, 답변을 받아오는 가장 단순한 방법"
)

# ----------------------- 사이드바 설정 -----------------------
with st.sidebar:
    st.header("설정")
    api_key = st.text_input(
        "OpenAI API key",
        type="password",
        help="sk-로 시작하는 OpenAI API key를 입력하세요.",
    )
    model = st.selectbox(
        "모델 선택", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"], index=0
    )
    st.markdown("[API 키 발급 받기](https://platform.openai.com/api-keys)")

# ----------------------- 메인 화면 -----------------------
question = st.text_input(
    "질문을 입력하세요", placeholder="예) 오늘 날씨가 어떤가요?"
)

if st.button("질문하기", type="primary"):
    if not api_key:
        st.error("OpenAI API key를 입력하세요.")
    elif not question:
        st.warning("질문을 입력하세요.")
    else:
        try:
            client = OpenAI(api_key=api_key)

            # 답변 생성 중 로딩 스피너 표시
            with st.spinner("답변을 생각하는 중..."):
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "당신은 사용자를 '주인님'이라고 부르는 공손하고 친절한 비서입니다. 항상 친절하고 정중하게 답변해주세요.",
                        },
                        {"role": "user", "content": question},
                    ],
                )

            # 1. 답변 출력
            answer = response.choices[0].message.content
            st.success("답변이 완료되었습니다!")
            st.markdown(f"### 💬 답변\n{answer}")

            # 2. 토큰 사용량 계산 및 표시
            usage = response.usage
            st.divider()
            st.subheader("📊 사용한 토큰 수")
            col1, col2, col3 = st.columns(3)
            col1.metric("입력 토큰", f"{usage.prompt_tokens}개")
            col2.metric("출력 토큰", f"{usage.completion_tokens}개")
            col3.metric("총 토큰 수", f"{usage.total_tokens}개")

        except Exception as e:
            # API 키 오류나 네트워크 문제 등 예외 처리
            st.error(f"오류가 발생했습니다: {e}")