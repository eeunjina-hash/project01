import os
import base64
import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="무역 실무 MBTI 진단",
    page_icon="🔮",
    layout="centered"
)

# 2. 배경 이미지 로드 함수
def get_image_base64(filename="background.jpg"):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        current_dir = os.getcwd()
        
    file_path = os.path.join(current_dir, filename)
    
    if not os.path.exists(file_path):
        alt_path = os.path.join(current_dir, "background.png")
        if os.path.exists(alt_path):
            file_path = alt_path
        else:
            return None

    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_base64 = get_image_base64("background.jpg")

# 3. 몽환적인 보랏빛 안개 숲 맞춤형 CSS
if bg_base64:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;700&display=swap');

        html, body, .stApp, 
        header[data-testid="stHeader"],
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewBlockContainer"],
        .main, .stMain, section.main {{
            background-color: transparent !important;
            background: transparent !important;
        }}

        html, [data-testid="stAppViewContainer"] {{
            background-image: linear-gradient(rgba(32, 16, 48, 0.45), rgba(20, 10, 35, 0.6)), url("data:image/jpeg;base64,{bg_base64}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
            font-family: 'Pretendard', sans-serif;
            color: #ffffff !important;
        }}

        h1 {{
            color: #ffffff !important;
            text-shadow: 0 0 18px rgba(254, 240, 138, 0.8), 0 0 32px rgba(192, 132, 252, 0.7);
            font-weight: 700 !important;
        }}

        div[data-testid="stRadio"] > div {{
            background: rgba(255, 255, 255, 0.18) !important;
            border: 1px solid rgba(233, 213, 255, 0.35) !important;
            border-radius: 18px !important;
            padding: 16px 22px !important;
            backdrop-filter: blur(14px) !important;
            -webkit-backdrop-filter: blur(14px) !important;
            box-shadow: 0 8px 32px 0 rgba(19, 7, 30, 0.4) !important;
            transition: all 0.3s ease;
        }}

        div[data-testid="stRadio"] > div:hover {{
            background: rgba(255, 255, 255, 0.28) !important;
            border-color: rgba(245, 208, 254, 0.8) !important;
            box-shadow: 0 8px 30px rgba(168, 85, 247, 0.35) !important;
            transform: translateY(-2px);
        }}

        div[data-testid="stRadio"] label p {{
            font-size: 1.05rem !important;
            font-weight: 600 !important;
            color: #ffffff !important;
            text-shadow: 0 1px 4px rgba(0, 0, 0, 0.7) !important;
        }}

        .stButton > button {{
            background: linear-gradient(135deg, #fde047 0%, #d8b4fe 50%, #c084fc 100%) !important;
            color: #2e1065 !important;
            font-weight: 700 !important;
            font-size: 1.15rem !important;
            padding: 14px 28px !important;
            border-radius: 30px !important;
            border: none !important;
            box-shadow: 0 0 25px rgba(253, 224, 71, 0.5) !important;
            transition: all 0.3s ease !important;
        }}

        .stButton > button:hover {{
            box-shadow: 0 0 35px rgba(192, 132, 252, 0.9) !important;
            transform: scale(1.02);
        }}

        .result-box {{
            border-radius: 22px;
            padding: 24px;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            margin-bottom: 20px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# 4. 16가지 무역 MBTI 기본 프로필 데이터
TRADE_MBTI_PROFILES = {
    "ESTJ": {"title": "오퍼레이션을 완벽 통제하는 사령관", "job": "무역영업관리 & 출하 관리", "desc": "선적 지연과 서류 하자를 절대 용납하지 않는 무역 실무의 철통 방패입니다.", "strengths": ["철저한 납기 통제", "수주-출하 프로세스 최적화", "바이어 요구사항의 정밀한 이행"], "match_item": "반도체/전자부품, 원자재, 설비", "cert": "국제무역사, 무역영어 1급, 물류관리사"},
    "ENTJ": {"title": "글로벌 시장을 장악하는 톱티어 세일즈맨", "job": "해외영업 총괄", "desc": "과감한 피칭과 네고 실력으로 현지 유통망을 뚫고 대형 수주를 이끄는 프론티어입니다.", "strengths": ["대형 바이어 단판 협상", "글로벌 독점 총판 계약", "공격적인 시장 침투"], "match_item": "K-뷰티/화장품, 소비재 완제품", "cert": "OPIc AL, 국제무역사"},
    "ESFP": {"title": "전시회 부스를 뜨겁게 달구는 스타", "job": "해외영업 & 필드 마케팅", "desc": "글로벌 전시회에서 탁월한 친화력과 스몰토크로 바이어의 마음을 즉석에서 사로잡습니다.", "strengths": ["오프라인 전시회 리드 발굴", "바이어 대면 라포 형성", "순발력 있는 현장 상담"], "match_item": "식품/K-푸드, 뷰티, 패션", "cert": "TOEIC Speaking / OPIc, 무역영어"},
    "ENFP": {"title": "글로벌 트렌드를 포착하는 바이럴 기획자", "job": "글로벌 마케팅 & 해외 브랜딩", "desc": "국가별 SNS 트렌드와 감성을 정확히 짚어내어 해외 소비자의 팬덤을 만듭니다.", "strengths": ["인플루언서 섭외/협업", "현지화(Localization) 브랜딩", "해외 마케팅 기획"], "match_item": "선케어/선세럼, 인디 뷰티, 라이프스타일", "cert": "디지털마케팅 자격, GA4, 무역영어"},
    "ESTP": {"title": "물류 위기도 번개처럼 뚫는 해결사", "job": "수출입 물류 & 포워딩 오퍼레이터", "desc": "선복 부족이나 결항 사태에도 기지를 발휘해 가장 빠른 대체 루트를 찾아냅니다.", "strengths": ["선복 긴급 확보", "포워더/선사 네고", "물류 현장 트러블 즉시 해결"], "match_item": "콜드체인 신선식품, 긴급 IT 부품", "cert": "물류관리사, 유통관리사"},
    "ENTP": {"title": "거래 조건을 유리하게 뒤집는 네고의 승부사", "job": "해외소싱 & 글로벌 구매", "desc": "글로벌 서플라이어와의 줄다리기에서 마진을 확보하고 단가를 깎아내는 실리파입니다.", "strengths": ["서플라이어 원가 분해", "대체 생산 거점 발굴", "유리한 결제 조건 도출"], "match_item": "OEM/ODM 화장품 용기, 전자 부품", "cert": "국제무역사, CPIM, 무역영어"},
    "ESFJ": {"title": "바이어를 단골로 만드는 관계 관리의 신", "job": "무역영업관리 & 해외 고객 CS", "desc": "정확하고 따뜻한 피드백으로 해외 바이어와의 신뢰를 수년간 단단히 유지합니다.", "strengths": ["바이어 정기 팔로업", "클레임 완화 및 신뢰 회복", "공장 및 유통망 조율"], "match_item": "OEM 지속 납품 부품, 소비재", "cert": "무역영어 1급, 비즈니스 영어"},
    "ENFJ": {"title": "글로벌 파트너를 원팀으로 묶는 리더", "job": "해외 사업개발 & 전략 제휴", "desc": "서로 다른 문화를 조율해 해외 바이어와 국내 생산팀을 묶는 프로젝트 사령탑입니다.", "strengths": ["글로벌 조인트벤처 기획", "신뢰 기반 파트너십", "복합 프로젝트 리딩"], "match_item": "헬스케어 솔루션, 친환경 소재", "cert": "국제무역사, PMP, OPIc"},
    "ISTJ": {"title": "인코텀즈와 L/C 하자를 잡아내는 서류의 신", "job": "무역 계약 & 컴플라이언스", "desc": "신용장 하자(Discrepancy)와 계약 독소 조항을 한 치의 오차도 없이 걸러냅니다.", "strengths": ["수출입 서류 정밀 심사", "외환 거래 규범 준수", "독소 조항 사전 차단"], "match_item": "L/C 기반 플랜트 설비, 철강, 대형 기계", "cert": "국제무역사 1급, CDCS, 보세사"},
    "INTJ": {"title": "공급망 전체를 설계하는 체스 마스터", "job": "글로벌 물류 기획 & 통상 전략", "desc": "환율 변동, 국제 유가, FTA 관세를 입체적으로 계산해 물류비와 원가를 최소화합니다.", "strengths": ["FTA 원산지 증명 최적화", "물류 거점 설계", "중장기 리스크 헷징"], "match_item": "고부가가치 반도체, 정밀 기기", "cert": "관세사 1차, 물류관리사, 국제무역사"},
    "ISTP": {"title": "공정 원가를 현미경으로 보는 테크니컬 바이어", "job": "테크니컬 소싱 & 무역 기술영업", "desc": "제품 도면과 공정을 꿰뚫어 해외 엔지니어와 대등하게 소통하고 단가를 검증합니다.", "strengths": ["기술 스펙 정밀 매칭", "품질 불량 원인 규명", "제조 공정 단가 절감"], "match_item": "정밀 계측기, 디스플레이 부품", "cert": "품질경영기사, 국제무역사, 무역영어"},
    "INTP": {"title": "통상 규제와 FTA 틈새를 파고드는 분석가", "job": "통상 분석 & 무역 정책 리서치", "desc": "복잡한 관세율표와 HS코드의 틈새를 분석해 절세 방안을 찾아내는 브레인입니다.", "strengths": ["HS Code 품목분류 분석", "해외 통상 규제 분석", "FTA 특혜관세 실무"], "match_item": "화학물질, 바이오 의약품, 가공식품", "cert": "원산지관리사, 관세사 1차"},
    "ISFJ": {"title": "선적 서류 완벽 패키징! 무역계의 든든한 백오피스", "job": "무역서류 작성 & 통관 지원", "desc": "B/L, C/I, P/L을 한 치의 오차도 없이 완성해 통관 지연을 사전에 방어합니다.", "strengths": ["통관 서류 완벽 구비", "대금 결제 일정 추적", "거래처 히스토리 관리"], "match_item": "화장품 패키징 부자재, 리빙/잡화", "cert": "무역영어 1급, 국제무역사"},
    "INFJ": {"title": "문화를 잇는 글로벌 브릿지 메이커", "job": "글로벌 파트너십 & 지속가능 무역(ESG)", "desc": "상대국의 문화적 맥락을 깊이 헤아려 지속 가능하고 윤리적인 무역을 이끕니다.", "strengths": ["글로벌 비즈니스 매너 조율", "장기 공급 계약 신뢰 구축", "ESG/공정무역 인증 실무"], "match_item": "비건 코스메틱, 친환경 유기농 식품", "cert": "국제무역사, ESG 무역 실무"},
    "ISFP": {"title": "현지 반응을 감각적으로 읽는 크로스보더 MD", "job": "해외 온라인 MD & 이커머스", "desc": "쇼피, 아마존 등 해외 플랫폼에서 현지 리뷰를 분석하고 상품을 매력적으로 연출합니다.", "strengths": ["글로벌 플랫폼 운영", "소비자 리뷰 분석 및 개선", "감각적인 상품 상세 기획"], "match_item": "K-인디 뷰티, 디자인 잡화", "cert": "유통관리사, 전자상거래운용사"},
    "INFP": {"title": "브랜드의 영혼을 번역하는 스토리텔러", "job": "글로벌 콘텐츠 마케팅 & 해외 PR", "desc": "브랜드의 철학을 감성적인 영문 스토리로 엮어 글로벌 바이어의 마음을 움직입니다.", "strengths": ["감성적 영문 카피라이팅", "해외 브랜드 스토리텔링", "진정성 있는 제휴 제안"], "match_item": "자연주의 스킨케어, 프리미엄 티", "cert": "TOEIC Writing, 무역영어"}
}

# 5. 16가지 무역 MBTI 상세 실무 스토리라인
EXTRA_PROFILE_DATA = {
    "ESTJ": {
        "daily": "08:50 ERP 수주 현황 점검 ➔ 10:30 포워더 선적 서류(B/L, C/I) 크로스체크 ➔ 14:00 공장 출하 지연 긴급 독촉 ➔ 17:30 바이어 선적 완료 통보 및 트래킹 넘버 회신",
        "rage_button": "출항 당일 아침에 포워더가 '선복(스페이스)이 꽉 차서 롤오버(이월)됐다'고 일방 통보할 때",
        "best_chemistry": "INFP (창의적인 해외 틈새 시장 아이디어를 물어와서 실행 플랜을 짜주기 딱 좋음)",
        "worst_chemistry": "ENTP (계약서 디테일 확인도 안 하고 구두로 번개 계약부터 맺고 올 때)"
    },
    "ENTJ": {
        "daily": "09:00 환율 및 글로벌 원자재가 체크 ➔ 11:00 신규 바이어 화상 영어 피칭 ➔ 15:00 권역별 수출 마진율 시뮬레이션 ➔ 19:00 해외 바이어 만찬 네트워킹",
        "rage_button": "단가를 30%나 후려치면서 MOQ(최소주문수량)는 샘플 수준으로 10개만 발주하겠다고 떼쓸 때",
        "best_chemistry": "ISFP (현장 감각과 꼼꼼함으로 계약서의 빈틈과 세부 실행을 완벽히 백업해 줌)",
        "worst_chemistry": "ISFJ (큰 그림 보고 과감하게 드라이브 걸어야 하는데 사소한 서류 걱정으로 브레이크 걸 때)"
    },
    "ESFP": {
        "daily": "09:30 글로벌 박람회 부스 세팅 점검 ➔ 11:00 지나가는 바이어 샘플 시연 및 명함 100장 확보 ➔ 15:00 통역원들과 현장 상담 리드 정리 ➔ 18:30 현지 리셉션 파티 참석",
        "rage_button": "신나게 바이어랑 친해져서 상담 다 끝내놨더니 회사에서 예산 없다고 출장비 삭감할 때",
        "best_chemistry": "INTJ (내가 현장에서 명함 쓸어오면 뒤에서 계약 조항과 마진을 칼같이 계산해 줌)",
        "worst_chemistry": "ISTJ (전시회 현장에서 분위기 띄우는데 옆에서 서류 규정 읊으며 찬물 끼얹을 때)"
    },
    "ENFP": {
        "daily": "10:00 틱톡/인스타 글로벌 뷰티 트렌드 서칭 ➔ 13:30 현지 인플루언서 PR 시딩 패키지 기획 ➔ 16:00 해외 전시회 부스 컨셉 회의 ➔ 18:00 글로벌 바이어용 감성 뉴스레터 발송",
        "rage_button": "야심차게 준비한 해외 바이럴 마케팅 기획서에 '과거 사례랑 규정대로만 해'라고 반려당할 때",
        "best_chemistry": "ISTJ (내가 던진 기발한 해외 마케팅 아이디어를 법적 문제와 선적 규정에 맞게 다듬어 줌)",
        "worst_chemistry": "ESTJ (창의적인 기획 설명하는데 '그래서 이번 달 당장 수출 얼마 찍히냐'고 윽박지를 때)"
    },
    "ESTP": {
        "daily": "08:30 야드 컨테이너 반입 현황 체크 ➔ 11:00 선박 결항 소식에 즉시 대체 항공편 확보 ➔ 14:30 세관 보세창고 현장 점검 ➔ 17:00 포워더와 체선료(Demurrage) 감면 담판",
        "rage_button": "현장에서 컨테이너 묶여서 난리 났는데 사무실에서 절차대로 품의서부터 올리라고 할 때",
        "best_chemistry": "INFJ (중장기적 글로벌 공급망 그림을 그려주면 현장에서 온몸으로 길을 뚫어줌)",
        "worst_chemistry": "INTP (지금 당장 화물 출발해야 하는데 관세율 규정 책 펴놓고 원론적인 토론하고 있을 때)"
    },
    "ENTP": {
        "daily": "10:00 글로벌 B2B 플랫폼 공급처 단가 비교 ➔ 13:00 해외 공장 매니저와 화상 네고 배틀 ➔ 16:00 독점 공급권 계약 조항 역제안 ➔ 18:30 새로운 소싱 루트 발굴",
        "rage_button": "서플라이어가 '원래 회사 방침이라 가격 조정 절대 안 된다'며 융통성 없이 벽칠 때",
        "best_chemistry": "ISFJ (내가 거칠게 깎아온 공급처의 사후 품질 검수와 납기 일정을 완벽히 챙겨줌)",
        "worst_chemistry": "ESTJ (새롭고 마진 높은 소싱 공장 찾아왔더니 기존 거래처 아니라고 쳐다도 안 볼 때)"
    },
    "ESFJ": {
        "daily": "09:00 시차 맞춰 해외 바이어 안부 및 오더 체크 ➔ 11:30 영업-생산-물류팀 납기 조율 회의 ➔ 14:30 지연 클레임 건 바이어 달래기 ➔ 17:00 명절/시즌 바이어 선물 패키징",
        "rage_button": "공장 팀에서 사전 상의도 없이 출하 일정 일주일 미뤄서 바이어한테 거짓말쟁이 만들 때",
        "best_chemistry": "INTP (논리적으로 빈틈없는 법적·통상 근거를 줘서 바이어 설득할 무기를 쥐여줌)",
        "worst_chemistry": "ENTP (바이어랑 조율해서 일정 다 맞춰놨는데 중간에 갑자기 납품 조건 다 뒤엎을 때)"
    },
    "ENFJ": {
        "daily": "09:30 다국적 합작 파트너사 주간 화상 회의 ➔ 13:00 해외 지사 로컬 직원 멘토링 ➔ 15:30 수출 바이어 초청 세미나 총괄 ➔ 18:00 프로젝트 마일스톤 회고 및 격려",
        "rage_button": "파트너십의 장기적 신뢰보다 당장 눈앞의 푼돈 마진 챙기겠다고 바이어 등치려 할 때",
        "best_chemistry": "ISTP (인간관계 신경 쓰느라 놓치기 쉬운 기술적 하자와 비용 낭비를 날카롭게 짚어줌)",
        "worst_chemistry": "ISTJ (바이어와의 전략적 관계를 위해 유연성이 필요한데 규정집 들이밀며 거부할 때)"
    },
    "ISTJ": {
        "daily": "09:00 신용장(L/C) 조건과 C/I 불일치(Discrepancy) 현미경 검토 ➔ 11:30 인코텀즈 2020 위험 이전 시점 체크 ➔ 14:00 원산지 증명서 발급 ➔ 17:00 외환 정산 마감",
        "rage_button": "인보이스 숫자나 품명 스펠링 하나 틀려놓고 '세관에서 대충 넘어가 주겠죠' 할 때",
        "best_chemistry": "ENFP (사고뭉치 같지만 기상천외한 해외 수출 건을 따오면 뒤에서 법적으로 안전하게 처리해 줌)",
        "worst_chemistry": "ENFJ (원칙과 계약서가 먼저인데 '좋은 게 좋은 거다'라며 예외 승인 남발하려 할 때)"
    },
    "INTJ": {
        "daily": "09:30 글로벌 운임 지수 및 유가 빅데이터 분석 ➔ 11:00 FTA 최적 특혜관세 루트 시뮬레이션 ➔ 14:30 전사 SCM 공급망 거점 재배치안 기획 ➔ 17:00 환율 리스크 헷징 전략 보고",
        "rage_button": "데이터와 논리적 근거도 없이 '영업은 원래 감과 깡으로 하는 거다'라며 우길 때",
        "best_chemistry": "ESFP (치밀하게 설계해 둔 해외 유통망 위에서 온몸으로 뛰며 매출을 쓸어 담아옴)",
        "worst_chemistry": "ESFJ (시스템 개선하자고 통계 가져왔더니 관계자들 눈치 보느라 적용 못 하겠다고 할 때)"
    },
    "ISTP": {
        "daily": "09:00 수출 장비 도면 및 부품 스펙 정밀 검토 ➔ 11:00 해외 테크니컬 엔지니어와 기술 질의 메일 회신 ➔ 14:00 불량 샘플 분해 및 공정 원인 분석 ➔ 16:30 실용적 단가 네고안 작성",
        "rage_button": "제품 구조나 공정도 전혀 모르는 영업사원이 바이어한테 불가능한 제작 스펙 약속해 올 때",
        "best_chemistry": "ENFJ (기술적인 검증만 끝내놓으면 바이어 앞에 나가 화려한 프레젠테이션으로 팔아줌)",
        "worst_chemistry": "ENFP (현실적으로 공장에서 구현 불가능한 뜬구름 잡는 아이디어 계속 가져올 때)"
    },
    "INTP": {
        "daily": "10:00 해외 통상 규제 보고서 정독 ➔ 13:30 신규 화장품 전성분 HS Code 품목분류 연구 ➔ 15:30 비관세 장벽 우회 통관 솔루션 도출 ➔ 18:00 무역 협정 개정안 사내 가이드 작성",
        "rage_button": "이론상 분명히 관세 감면받을 수 있는 루트인데 '늘 하던 대로 해'라며 관세 그냥 낼 때",
        "best_chemistry": "ESFJ (내가 골방에서 찾아낸 완벽한 통상 솔루션을 기관과 바이어에게 싹싹하게 전달해 줌)",
        "worst_chemistry": "ESTP (통상 규정 검토 끝나지도 않았는데 성질 급하게 화물부터 선적해 버렸을 때)"
    },
    "ISFJ": {
        "daily": "09:00 관세청 유니패스 수출입 신고 필증 확인 ➔ 11:00 바이어별 서류 아카이빙 및 파일철 정리 ➔ 14:00 L/C 대금 입금 확인 및 영수증 발행 ➔ 16:30 내일 출하 화물 패킹리스트 사전 검수",
        "rage_button": "선적 마감 10분 전에 서류 내용 갑자기 바꾸면서 '미안한데 빨리 좀 해줘'라고 던질 때",
        "best_chemistry": "ENTP (저돌적으로 신규 거래처를 뚫어오면 보이지 않는 곳에서 서류와 정산을 완벽히 서포트함)",
        "worst_chemistry": "ENTJ (내 노고는 당연하게 여기고 결과만 보면서 더 빠르게 서류 안 뽑냐고 쪼아댈 때)"
    },
    "INFJ": {
        "daily": "09:30 해외 바이어 국가의 최근 정치/문화 이슈 모니터링 ➔ 11:00 현지화 패키징 문구의 문화적 오역 검토 ➔ 14:00 공정무역 및 ESG 인증 심사 준비 ➔ 17:00 진정성 담긴 파트너십 레터 작성",
        "rage_button": "수출 상대국의 문화와 종교적 금기를 무시하고 무례하게 비즈니스 매너 말아먹을 때",
        "best_chemistry": "ESTP (진심 어린 파트너십을 내가 맺어두면 거친 물류 현장의 문제들을 시원하게 격파해 줌)",
        "worst_chemistry": "ESTJ (바이어의 문화적 맥락을 고려해야 한다는데 숫자와 기한만 들이밀며 밀어붙일 때)"
    },
    "ISFP": {
        "daily": "10:30 크로스보더 플랫폼 현지 리뷰 및 평점 체크 ➔ 13:00 상세페이지 현지어 폰트 및 톤앤매너 수정 ➔ 15:30 경쟁사 제품 언박싱 및 패키징 벤치마킹 ➔ 18:00 해외 리뷰어 샘플 발송",
        "rage_button": "디자인 1도 모르는 윗선이 현지화 상세페이지에 촌스러운 빨간 폰트로 문구 넣으라고 할 때",
        "best_chemistry": "ENTJ (내가 감각적으로 살려놓은 상품을 바탕으로 대형 총판 계약과 물류망을 뚫어줌)",
        "worst_chemistry": "INTJ (소비자의 미묘한 감성 반응을 설명하는데 차가운 통계 데이터만 요구할 때)"
    },
    "INFP": {
        "daily": "10:00 브랜드 고유의 철학을 녹여낸 영문 브랜드북 집필 ➔ 13:30 감성적인 해외 바이어용 뉴스레터 디자인 ➔ 15:30 글로벌 취향 저격 패키징 스토리텔링 회의 ➔ 17:30 바이어 감사 카드 작성",
        "rage_button": "브랜드가 가진 진정성과 가치를 '그냥 단가 싼 제품 카피해서 팔면 안 되냐'고 폄하할 때",
        "best_chemistry": "ESTJ (내가 동화 같은 브랜드 스토리를 만들어내면 칼 같은 납기와 선적으로 현실화해 줌)",
        "worst_chemistry": "ESTP (브랜드 이미지 관리해야 하는데 덤핑으로 재고 싸게 털어버리자고 할 때)"
    }
}

# 6. 20개 실무 질문 데이터셋
QUESTIONS = [
    # E vs I
    {"dim": "EI", "q": "Q01. 해외 바이어와 첫 비즈니스 미팅을 잡을 때 선호하는 방식은?", "a": ("직접 얼굴을 맞대고 감정을 읽을 수 있는 화상 미팅이나 출장 미팅", "E"), "b": ("배경 자료와 질문지를 꼼꼼히 정리해 보내는 영문 이메일", "I")},
    {"dim": "EI", "q": "Q02. 대규모 해외 무역 전시회장에 파견되었을 때 나는?", "a": ("지나가는 바이어에게 먼저 샘플을 건네며 적극적으로 대화를 튼다.", "E"), "b": ("부스에 들어와 제품을 유심히 관찰하는 진성 바이어에게 집중한다.", "I")},
    {"dim": "EI", "q": "Q03. 바이어와의 납기 일정에 긴급한 이견이 생겼을 때 더 편한 방식은?", "a": ("즉시 다이렉트 콜(전화)을 걸어 목소리로 뉘앙스를 풀고 해결한다.", "E"), "b": ("논리적인 타임라인과 근거 문서를 메일과 메신저로 정확히 보낸다.", "I")},
    {"dim": "EI", "q": "Q04. 하루 중 나에게 더 긍정적인 에너지를 주는 시간은?", "a": ("해외 거래처, 포워더, 공장 사람들과 쉼 없이 의견을 주고받을 때", "E"), "b": ("방해받지 않는 조용한 공간에서 무역 데이터와 서류를 정리할 때", "I")},
    {"dim": "EI", "q": "Q05. 해외 출장지에서 모든 공식 일정이 끝난 저녁 시간이라면?", "a": ("현지 바이어와의 디너 미팅이나 업계 네트워킹 모임에 참석한다.", "E"), "b": ("호텔 방에서 차분히 휴식을 취하며 오늘 나눈 상담 일지를 정리한다.", "I")},

    # S vs N
    {"dim": "SN", "q": "Q06. 수출할 신제품의 시장성을 파악할 때 먼저 눈길이 가는 곳은?", "a": ("현지 통관 관세율, 경쟁사 유통 단가, 기존 수입 통계 수치", "S"), "b": ("현지 소비자의 라이프스타일 변화와 향후 파생될 새로운 트렌드", "N")},
    {"dim": "SN", "q": "Q07. 새로운 해외 거래처를 검증할 때 더 신뢰하는 지표는?", "a": ("재무제표의 자본금, 기존 거래 실적 증명서, 신용평가 보고서", "S"), "b": ("해당 기업의 사업 비전, 창업자의 경영 철학, 미래 잠재력", "N")},
    {"dim": "SN", "q": "Q08. 바이어에게 보낼 수출 제안서(Proposal)의 핵심 구성은?", "a": ("제품 규격 스펙, 국제 인증, MOQ, 인코텀즈 단가표", "S"), "b": ("이 제품이 현지 시장에서 어떤 새로운 라이프스타일을 만들지 담은 비전", "N")},
    {"dim": "SN", "q": "Q09. 글로벌 경제 뉴스를 읽을 때 더 흥미롭게 다가오는 주제는?", "a": ("해상 운임 지수(SCFI) 변동폭, 원달러 환율 추이, 품목별 관세 개정안", "S"), "b": ("글로벌 친환경 규범(ESG)과 탄소국경세가 바꿀 미래 무역 지도", "N")},
    {"dim": "SN", "q": "Q10. 기존 매뉴얼에 없는 새로운 형태의 거래가 들어왔다면?", "a": ("기존 표준 계약서 양식과 검증된 절차를 최대한 준용해 안전하게 처리한다.", "S"), "b": ("기존 틀에 얽매이지 않고 새로운 계약 구조나 파트너십을 구상해본다.", "N")},

    # T vs F
    {"dim": "TF", "q": "Q11. 선적된 화물 일부에 불량이 발생해 바이어가 클레임을 걸어왔다면?", "a": ("계약서상 허용 오차 규정과 선적 약관의 법적 귀책사유를 냉철하게 따진다.", "T"), "b": ("바이어의 불편에 깊이 공감하며 신뢰 유지를 위해 선제적 보상을 제시한다.", "F")},
    {"dim": "TF", "q": "Q12. 오랜 파트너 공장이 원자재값 폭등으로 단가 인상을 요구한다면?", "a": ("국제 원자재 가격 지수 데이터를 근거로 객관적인 인상 폭만 인정한다.", "T"), "b": ("수년간 다져온 파트너십을 고려해 공장의 고충을 나누는 방안을 찾는다.", "F")},
    {"dim": "TF", "q": "Q13. 까다로운 결제 조건 네고 중 바이어가 강한 불만을 터뜨릴 때?", "a": ("감정적 언어에 휘둘리지 않고 사전에 정한 마진 마지노선을 지킨다.", "T"), "b": ("상대가 불안해하는 근본적인 심리 요인을 파악해 안심시키는 제안을 건넨다.", "F")},
    {"dim": "TF", "q": "Q14. 팀원이 인보이스 오탈자로 인해 세관 검사를 받게 되었다면?", "a": ("어떤 확인 절차가 누락되었는지 원인을 분석하고 재발 방지책을 세운다.", "T"), "b": ("크게 자책하고 있을 팀원의 마음을 먼저 다독이고 함께 수습한다.", "F")},
    {"dim": "TF", "q": "Q15. 글로벌 비즈니스를 지속 가능하게 만드는 가장 단단한 힘은?", "a": ("빈틈없는 원가 분석, 유리한 인코텀즈 계약, 객관적 리스크 헷징", "T"), "b": ("서로 다른 문화를 존중하는 온화한 태도와 사람 대 사람의 진심 어린 신뢰", "F")},

    # J vs P
    {"dim": "JP", "q": "Q16. 수출 선적 일정을 수립할 때 나의 계획 스타일은?", "a": ("선적일(ETD)을 기점으로 역산하여 주 단위 세부 마일스톤을 확정해둔다.", "J"), "b": ("큰 틀의 납기만 설정해두고 공장 상황이나 선사 사정에 맞춰 유연하게 조율한다.", "P")},
    {"dim": "JP", "q": "Q17. 업무용 노트북 속 무역 서류 폴더의 정리 상태는?", "a": ("연도별/국가별/인보이스 번호별로 칼같이 분류되어 있어 즉시 찾아낸다.", "J"), "b": ("자유롭게 저장되어 있지만 검색 기능이나 기억을 활용해 찾아낸다.", "P")},
    {"dim": "JP", "q": "Q18. 포워더로부터 '선박 결항으로 출항이 취소되었다'는 급보가 왔다면?", "a": ("미리 마련해둔 플랜 B(항공 운송/대체 선사 리스트)를 즉시 가동한다.", "J"), "b": ("당황하지 않고 현재 가용한 모든 인맥과 채널을 총동원해 현장에서 뚫어낸다.", "P")},
    {"dim": "JP", "q": "Q19. 하루 업무를 시작할 때 나의 집중 방식은?", "a": ("오늘 완결해야 할 일의 우선순위를 번호 매겨 하나씩 지워나간다.", "J"), "b": ("메일함을 열고 해외에서 밤사이 들어온 돌발 이슈부터 유연하게 해결한다.", "P")},
    {"dim": "JP", "q": "Q20. 해외 출장을 앞둔 나의 준비 방식은?", "a": ("미팅 시간, 동선, 이동 교통편, 비상 연락망까지 시간대별로 완벽히 계획한다.", "J"), "b": ("핵심 미팅만 잡아두고 현지 상황이나 바이어 분위기에 맞춰 탄력적으로 움직인다.", "P")}
]

# 7. 헤더 및 설문 UI 렌더링
st.markdown("<h1 style='text-align: center;'>✨ Trade Dream MBTI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #ffebf0; font-size: 1.1rem; text-shadow: 0 1px 3px rgba(0,0,0,0.5);'>파스텔 노을과 별빛 속에서 찾는 나의 무역 페르소나</p>", unsafe_allow_html=True)
st.write("")

with st.form("dreamy_trade_form"):
    user_choices = []
    
    for i, item in enumerate(QUESTIONS):
        st.markdown(f"<p style='color: #ffffff; font-weight: 700; font-size: 1.05rem; margin-bottom: 8px; text-shadow: 0 1px 4px rgba(0,0,0,0.6);'>{item['q']}</p>", unsafe_allow_html=True)
        choice = st.radio(
            label=f"q_{i}_label",
            options=[item["a"][0], item["b"][0]],
            index=0,
            key=f"unique_trade_q_{i}",
            label_visibility="collapsed"
        )
        user_choices.append((i, choice))
        st.write("")
        
    submitted = st.form_submit_button("🌟 나의 무역 성향 분석하기", use_container_width=True)

# 8. 결과 판정 및 최종 화면 출력
if submitted:
    scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
    
    for q_idx, selected_text in user_choices:
        q_item = QUESTIONS[q_idx]
        chosen_type = q_item["a"][1] if selected_text == q_item["a"][0] else q_item["b"][1]
        scores[chosen_type] += 1

    mbti_result = (
        ("E" if scores["E"] >= scores["I"] else "I") +
        ("S" if scores["S"] >= scores["N"] else "N") +
        ("T" if scores["T"] >= scores["F"] else "F") +
        ("J" if scores["J"] >= scores["P"] else "P")
    )

    p = TRADE_MBTI_PROFILES[mbti_result]
    extra = EXTRA_PROFILE_DATA[mbti_result]

    st.balloons()
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    
    # 1) 메인 결과 카드 (검은색 텍스트 & 선명한 박스)
    strengths_html = "".join([f"<li style='color: #111827; margin-bottom: 4px; font-weight: 600;'>{item}</li>" for item in p['strengths']])
    main_card_html = f"""<div class="result-box" style="background: rgba(255, 255, 255, 0.92); border: 1px solid rgba(255, 255, 255, 0.95); box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
<span style="background: #e9d5ff; color: #581c87; border: 1px solid #c084fc; padding: 4px 14px; border-radius: 20px; font-weight: 800; font-size: 0.9rem;">MBTI : {mbti_result}</span>
<h2 style="color: #111827; margin-top: 12px; font-size: 1.8rem; font-weight: 800; text-shadow: none;">💫 {p['title']}</h2>
<p style="color: #6b21a8; font-size: 1.15rem; font-weight: 800; margin-bottom: 12px;">💼 추천 직무 : {p['job']}</p>
<p style="color: #1f2937; line-height: 1.7; font-size: 1rem; margin-bottom: 18px; font-weight: 600;">{p['desc']}</p>
<div style="border-top: 1px solid rgba(0, 0, 0, 0.12); padding-top: 14px;">
<p style="color: #111827; font-weight: 800; font-size: 1.05rem; margin-bottom: 8px;">🎯 핵심 업무 강점</p>
<ul style="padding-left: 20px; line-height: 1.7;">
{strengths_html}
</ul>
</div>
</div>"""
    st.markdown(main_card_html, unsafe_allow_html=True)

    # 2) 품목 및 추천 스킬 카드
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""<div class="result-box" style="background: rgba(255, 255, 255, 0.92); padding: 18px; height: 100%; border: 1px solid rgba(255, 255, 255, 0.95);">
<p style="color: #6b21a8; font-weight: 800; margin-bottom: 6px; font-size: 1rem;">📦 어울리는 품목</p>
<p style="color: #111827; font-size: 0.95rem; margin: 0; line-height: 1.6; font-weight: 700;">{p['match_item']}</p>
</div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="result-box" style="background: rgba(255, 255, 255, 0.92); padding: 18px; height: 100%; border: 1px solid rgba(255, 255, 255, 0.95);">
<p style="color: #6b21a8; font-weight: 800; margin-bottom: 6px; font-size: 1rem;">📜 추천 스킬 & 자격증</p>
<p style="color: #111827; font-size: 0.95rem; margin: 0; line-height: 1.6; font-weight: 700;">{p['cert']}</p>
</div>""", unsafe_allow_html=True)

    # 3) 가상 일과 카드
    st.markdown(f"""<div class="result-box" style="background: rgba(255, 255, 255, 0.92); margin-top: 15px; border: 1px solid rgba(255, 255, 255, 0.95);">
<h4 style="color: #6b21a8; margin-bottom: 8px; font-weight: 800;">⏰ 이 유형의 하루 (A Day in Life)</h4>
<p style="color: #111827; font-size: 0.95rem; line-height: 1.7; margin-bottom: 0; font-weight: 600;">
{extra['daily']}
</p>
</div>""", unsafe_allow_html=True)

    # 4) 발작 버튼 카드
    st.markdown(f"""<div class="result-box" style="background: rgba(255, 255, 255, 0.94); border-left: 6px solid #dc2626; border-top: 1px solid rgba(255, 255, 255, 0.95); border-right: 1px solid rgba(255, 255, 255, 0.95); border-bottom: 1px solid rgba(255, 255, 255, 0.95);">
<h4 style="color: #b91c1c; margin-bottom: 8px; font-weight: 800;">🚨 절대 참을 수 없는 순간 (발작 버튼)</h4>
<p style="color: #111827; font-size: 0.95rem; line-height: 1.6; margin-bottom: 0; font-weight: 700;">
"{extra['rage_button']}"
</p>
</div>""", unsafe_allow_html=True)

    # 5) 찰떡 무역 케미 요약표 카드
    st.markdown(f"""<div class="result-box" style="background: rgba(255, 255, 255, 0.92); border: 1px solid rgba(255, 255, 255, 0.95);">
<h4 style="color: #581c87; margin-bottom: 14px; font-weight: 800;">🔮 유형별 찰떡 무역 케미 요약표</h4>
<div style="margin-bottom: 12px;">
<span style="background: #dcfce7; border: 1px solid #86efac; color: #166534; padding: 4px 10px; border-radius: 8px; font-size: 0.85rem; font-weight: 800;">최고의 파트너 찰떡궁합</span>
<p style="color: #111827; font-size: 0.95rem; margin-top: 6px; margin-bottom: 0; line-height: 1.6; font-weight: 600;">
{extra['best_chemistry']}
</p>
</div>
<div style="border-top: 1px dashed rgba(0, 0, 0, 0.15); padding-top: 12px; margin-top: 12px;">
<span style="background: #fee2e2; border: 1px solid #fca5a5; color: #991b1b; padding: 4px 10px; border-radius: 8px; font-size: 0.85rem; font-weight: 800;">주의! 상극 파트너</span>
<p style="color: #111827; font-size: 0.95rem; margin-top: 6px; margin-bottom: 0; line-height: 1.6; font-weight: 600;">
{extra['worst_chemistry']}
</p>
</div>
</div>""", unsafe_allow_html=True)