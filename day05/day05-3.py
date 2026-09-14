# 파일 업로드 문서 요약 앱
# 텍스트 파일(.txt)을 업로드하면 내용을 읽고 요약해주는 앱
# 실행 방법: streamlit run day05-4.py

import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="문서 요약 앱", page_icon="📄")

# 1. 메인 제목 및 2. 소제목
st.title("예제3: 파일 업로드 문서 요약 앱")
st.caption("텍스트 파일을 업로드하면 OpenAI API가 원하는 스타일로 요약해줍니다.")

# ----------------------- 사이드바 설정 -----------------------
with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input(
        "OpenAI API key",
        type="password",
        help="sk-로 시작하는 OpenAI API key를 입력하세요.",
    )
    model = st.selectbox(
        "모델 선택", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"], index=0
    )

    # 요약 스타일 선택 옵션
    summary_style = st.selectbox(
        "요약 스타일",
        ["핵심 요약 (3줄 불릿포인트)", "상세 요약 (개념 및 결론 포함)", "한 줄 요약"],
        index=0,
    )

    st.markdown("[API 키 발급 받기](https://platform.openai.com/api-keys)")

# ----------------------- 3. 파일 업로드 -----------------------
st.subheader("요약할 텍스트파일을 업로드하세요")
uploaded_file = st.file_uploader(
    "파일을 선택하세요", type=["txt"], label_visibility="collapsed"
)

# 파일이 업로드되었을 때 처리
if uploaded_file is not None:
    # 텍스트 파일 내용 디코딩 (utf-8 기본, 오류 발생 시 euc-kr 시도)
    try:
        raw_text = uploaded_file.read().decode("utf-8")
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        raw_text = uploaded_file.read().decode("euc-kr")

    # 4. 업로드한 문서 미리보기
    st.subheader("업로드한 문서 미리보기")
    with st.expander("📄 원본 문서 내용 펼치기 / 접기", expanded=True):
        st.text_area("문서 내용", raw_text, height=200, disabled=True)

    # 요약 시작 버튼
    if st.button("문서 요약하기", type="primary"):
        if not api_key:
            st.error("사이드바에서 OpenAI API key를 먼저 입력해주세요.")
        elif not raw_text.strip():
            st.warning("업로드된 문서가 비어 있습니다.")
        else:
            try:
                client = OpenAI(api_key=api_key)

                st.subheader("📝 요약 결과")

                with st.chat_message("assistant"):
                    stream_response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {
                                "role": "system",
                                "content": f"당신은 문서 요약 전문가입니다. 사용자가 제공한 문서를 바탕으로 다음 요청 스타일에 맞춰 명확하고 정중하게 요약해주세요: {summary_style}",
                            },
                            {
                                "role": "user",
                                "content": f"다음 문서를 요약해주세요:\n\n{raw_text}",
                            },
                        ],
                        stream=True,
                    )
                    st.write_stream(stream_response)

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")