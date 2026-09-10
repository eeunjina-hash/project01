import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="무역 직무 MBTI 진단 테스트",
    page_icon="🚢",
    layout="centered"
)

# 2. 직무 정의 및 상세 설명
JOBS = {
    "sales": "해외영업 (Overseas Sales)",
    "admin": "무역영업관리 (Sales Administration)",
    "sourcing": "해외소싱 및 구매 (Global Sourcing)",
    "logistics": "수출입 물류 및 통관 (Logistics & Customs)",
    "marketing": "글로벌 마케팅 (Global Marketing)",
    "compliance": "무역 계약 및 법무·정산 (Trade Compliance & Finance)"
}

JOB_DETAILS = {
    "sales": {
        "tagline": "새로운 시장을 개척하는 글로벌 비즈니스 프론티어",
        "desc": "목표 지향적이고 도전적인 성향으로, 신규 바이어 발굴과 가격 및 계약 조건 협상에 탁월합니다. 적극적인 커뮤니케이션과 네트워킹을 즐기는 인재에게 적합합니다.",
        "skills": ["글로벌 비즈니스 협상력", "바이어 콜드메일/미팅 리딩", "실적 및 매출 관리"]
    },
    "admin": {
        "tagline": "정확성과 신뢰로 오더를 완성하는 무역 실무의 엔진",
        "desc": "꼼꼼하고 체계적인 관리 성향으로, 수주부터 선적, 대금 정산에 이르는 전 과정을 조율합니다. 내부 부서 및 해외 거래선 간의 원활한 소통을 이끄는 인재에게 적합합니다.",
        "skills": ["ERP/오더 트래킹 관리", "바이어 사후 CS 및 일정 조율", "서류 정밀 대조"]
    },
    "sourcing": {
        "tagline": "최적의 공급망과 원가 경쟁력을 설계하는 전략가",
        "desc": "분석적이고 실리적인 성향으로, 경쟁력 있는 글로벌 서플라이어를 발굴하고 유리한 단가를 이끌어냅니다. 원가 구조 분석과 시장 조사에 능한 인재에게 적합합니다.",
        "skills": ["해외 공급처 발굴 및 네고", "원가 구조 및 마진 분석", "품질 및 납기 리스크 관리"]
    },
    "logistics": {
        "tagline": "물류 리스크를 최소화하고 납기를 책임지는 해결사",
        "desc": "신속한 문제 해결력과 현장 감각을 갖춘 성향으로, 포워더 조율, 선적 스케줄링, 통관 리스크 관리를 도맡습니다. 물류 프로세스를 막힘없이 운영하는 인재에게 적합합니다.",
        "skills": ["선적/운송 스케줄 관리", "B/L, C/I, P/L 등 운송서류 검토", "적하보험 및 통관 규정 대응"]
    },
    "marketing": {
        "tagline": "현지 시장 트렌드를 꿰뚫고 브랜드를 전파하는 기획자",
        "desc": "창의적이고 분석적인 성향으로, 국가별 시장 트렌드 파악, STP 전략 수립, 해외 전시회 기획 및 디지털 캠페인을 주도합니다. 시장 확장 전략을 기획하는 인재에게 적합합니다.",
        "skills": ["해외 시장 조사 및 STP 분석", "글로벌 전시회 기획/운영", "디지털 마케팅 및 리드 분석"]
    },
    "compliance": {
        "tagline": "외환 및 계약 리스크로부터 회사의 이익을 지키는 수호자",
        "desc": "원칙을 중시하고 신중한 성향으로, 인코텀즈, 신용장(L/C), 무역 계약서 검토, 환율 변동 리스크 관리를 철저히 수행합니다. 무역 법무와 금융 규정에 강한 인재에게 적합합니다.",
        "skills": ["무역 계약서 조항 검토", "신용장(L/C) 심사 및 하자 관리", "환리스크 관리 및 무역금융 실무"]
    }
}

# 3. 20개 문항 데이터셋
QUESTIONS = [
    {"q": "Q01. 해외 시장 진출 시 가장 먼저 집중하고 싶은 업무는?", "a": ("현지 유력 바이어를 직접 찾아가 대면 미팅을 연다.", "sales"), "b": ("현지 소비자 트렌드와 경쟁사 가격 데이터를 분석한다.", "marketing")},
    {"q": "Q02. 해외 파트너와 협상 테이블에 앉았을 때 나의 핵심 강점은?", "a": ("설득력 있는 화술과 유리한 조건을 이끄는 기세", "sales"), "b": ("철저한 사전 서류 준비와 꼼꼼한 세부사항 체크", "admin")},
    {"q": "Q03. 업무 과정에서 가장 큰 성취감을 느끼는 순간은?", "a": ("수억 원 대의 대형 수출 계약을 성사시켰을 때", "sales"), "b": ("기존 대비 원가를 15% 이상 절감한 공급처를 찾았을 때", "sourcing")},
    {"q": "Q04. 선적 일정이 임박했는데 운송 차질이 발생했다면?", "a": ("포워더와 운송사에 즉시 연락해 대체 선편이나 항공편을 긴급 수배한다.", "logistics"), "b": ("바이어에게 상황을 선제 공유하고 납기 연장 양해를 구한다.", "admin")},
    {"q": "Q05. 직무 역량 강화를 위해 더 깊이 파고들고 싶은 분야는?", "a": ("인코텀즈 2020 세부 조건과 L/C 결제 리스크", "compliance"), "b": ("글로벌 원자재 공급망 분석과 제조 단가 네고 스킬", "sourcing")},
    {"q": "Q06. 팀 프로젝트를 진행할 때 자연스럽게 맡게 되는 포지션은?", "a": ("전체 일정 로드맵 관리 및 구성원 간 업무 조율", "admin"), "b": ("시장 조사 기반 아이디어 도출 및 전략 기획", "marketing")},
    {"q": "Q07. 신규 거래처를 발굴해야 할 때 더 선호하는 방식은?", "a": ("글로벌 박람회 현장을 누비거나 직접 콜드콜/메일을 보낸다.", "sales"), "b": ("B2B 플랫폼과 공공 무역 데이터베이스를 교차 검증해 추린다.", "sourcing")},
    {"q": "Q08. 복잡한 무역 서류(C/I, P/L, B/L 등)를 검토할 때 나의 스타일은?", "a": ("오탈자, 불일치(Discrepancy)를 매의 눈으로 잡아낸다.", "compliance"), "b": ("규격 맞춤보다는 화물이 예정대로 부두에 입고되었는지가 우선이다.", "logistics")},
    {"q": "Q09. 특정 국가의 관세 장벽 강화 뉴스를 접했을 때 먼저 드는 생각은?", "a": ("계약서의 가격 수정 조항이나 결제 조건 변경 가능성을 따져본다.", "compliance"), "b": ("해당 국가 시장에서 우리 제품의 최종 가격 경쟁력 변화를 시뮬레이션한다.", "marketing")},
    {"q": "Q10. 해외 박람회 부스 운영자로 참여한다면 더 맡고 싶은 파트는?", "a": ("부스에 들어오는 바이어 응대 및 명함/상담 리드 확보", "sales"), "b": ("부스 비주얼 연출, 홍보 리플렛 및 브랜딩 영상 기획", "marketing")},
    {"q": "Q11. 바이어로부터 납기 지연에 대한 거센 클레임이 들어왔다면?", "a": ("생산 및 물류 현황을 파악해 정확한 입항 예상 일정을 재공지한다.", "admin"), "b": ("운송 구간별 과실 여부를 확인하고 선적 약관상 면책 여부를 검토한다.", "logistics")},
    {"q": "Q12. 수출용 신제품을 기획할 때 더 신경 쓰이는 항목은?", "a": ("안정적인 수급이 가능한 양질의 원부자재 서플라이어 확보", "sourcing"), "b": ("도착국 통관 시 문제될 수 있는 성분 규제 및 인증 요건", "logistics")},
    {"q": "Q13. 매일 시스템에 주문을 입력하고 선적 일정을 트래킹하는 업무에 대해?", "a": ("체계가 잡혀 있고 프로세스가 매끄럽게 돌아갈 때 안정감을 느낀다.", "admin"), "b": ("루틴한 반복보다는 새로운 비즈니스 기회를 발굴하는 것이 더 흥미롭다.", "sales")},
    {"q": "Q14. 신규 국가 런칭을 앞두고 예산 1순위로 배정하고 싶은 곳은?", "a": ("현지 타깃 소비자 확보를 위한 인플루언서 및 SNS 광고 캠페인", "marketing"), "b": ("현지 물류 창고 확보 및 가장 저렴한 로컬 운송 파트너 계약", "sourcing")},
    {"q": "Q15. 계약 체결 직전 최종 검토 시 가장 꼼꼼히 확인하는 조항은?", "a": ("준거법, 중재 조항, 지연배상금(LD) 및 환차손 보전 조건", "compliance"), "b": ("인도 장소, 위험 이전 시점, 터미널 조작료(THC) 부담 주체", "logistics")},
    {"q": "Q16. 업무상 상대방과 대화할 때 나의 기본적인 태도는?", "a": ("원가 내역과 조건을 파악해 우리 측 실리를 확실히 챙긴다.", "sourcing"), "b": ("부드러운 커뮤니케이션으로 장기적인 신뢰 관계를 유지한다.", "admin")},
    {"q": "Q17. 박람회 종료 후 수집한 200장의 바이어 명함을 처리하는 방식은?", "a": ("바이어 성향/규모별 세그먼트를 분류해 맞춤형 뉴스레터를 보낸다.", "marketing"), "b": ("구매 결정권자 순서로 분류해 즉시 견적서와 미팅 제안서를 보낸다.", "sales")},
    {"q": "Q18. 예상치 못한 리스크가 발생했을 때 나의 직관적인 판단 기준은?", "a": ("사내 규정 및 무역 법규 매뉴얼에 명시된 원칙대로 처리한다.", "compliance"), "b": ("현장 대리인과 협의해 당장의 물리적 문제를 가장 빠르게 우회 해결한다.", "logistics")},
    {"q": "Q19. 동료들이 평가하는 나의 가장 큰 업무적 강점은?", "a": ("일정 약속 준수, 꼼꼼한 피드백, 안정적인 지원력", "admin"), "b": ("트렌드 캐치 능력, 창의적인 전략 제안, 시장 분석력", "marketing")},
    {"q": "Q20. 무역 전문가로서 장기적으로 도달하고 싶은 최종 목표는?", "a": ("글로벌 공급망 전체를 핸들링하는 글로벌 소싱 디렉터", "sourcing"), "b": ("국제 분쟁과 무역 금융 리스크를 완벽히 통제하는 컴플라이언스 총괄", "compliance")}
]

# 4. 헤더 렌더링
st.title("🚢 무역 직무 MBTI 진단 테스트")
st.caption("20개의 선택형 질문을 통해 나의 업무 성향과 가장 잘 어울리는 무역 직무를 분석합니다.")
st.markdown("---")

# 5. 질문 폼
with st.form("trade_mbti_form"):
    user_choices = []
    
    for i, item in enumerate(QUESTIONS):
        choice = st.radio(
            item["q"],
            options=[item["a"][0], item["b"][0]],
            index=0,
            key=f"q_{i}"
        )
        user_choices.append((i, choice))
        st.write("")  # 간격 추가
        
    submitted = st.form_submit_button("🎯 결과 확인하기", use_container_width=True)

# 6. 결과 계산 및 출력
if submitted:
    # 점수 집계 초기화
    scores = {key: 0 for key in JOBS.keys()}
    
    for q_idx, selected_text in user_choices:
        question_data = QUESTIONS[q_idx]
        if selected_text == question_data["a"][0]:
            target_job = question_data["a"][1]
        else:
            target_job = question_data["b"][1]
        scores[target_job] += 1

    # 최고 득점 직무 선정 (동점 시 상위 키 기준)
    best_job_key = max(scores, key=scores.get)
    result_job = JOBS[best_job_key]
    result_info = JOB_DETAILS[best_job_key]

    st.markdown("---")
    st.header("📊 진단 결과")
    st.subheader(f"당신의 무역 직무 유형은 **[{result_job}]** 입니다!")
    st.info(f"💡 **\"{result_info['tagline']}\"**")
    
    st.markdown(f"**직무 성향 분석:**\n{result_info['desc']}")
    
    st.markdown("**핵심 추천 역량:**")
    for skill in result_info["skills"]:
        st.markdown(f"- {skill}")

    st.markdown("---")
    st.subheader("📈 직무별 적합도 랭킹")
    
    # 점수 내림차순 정렬
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # 20문항 중 직무당 최대 질문 수(대략 6~8점)를 감안해 8점을 100% 기준으로 게이지 표시
    max_possible = 8
    for job_key, score in sorted_scores:
        progress_val = min(score / max_possible, 1.0)
        st.write(f"**{JOBS[job_key]}** : {score}점")
        st.progress(progress_val)