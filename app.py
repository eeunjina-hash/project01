import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(
    page_title="무역 분석 대시보드",
    page_icon="🌐",
    layout="wide"
)

# 2. 샘플 데이터 생성 함수
@st.cache_data
def load_data():
    countries = ["미국", "중국", "일본", "독일", "베트남", "호주", "인도"]
    grades = ["A", "B", "C", "D"]
    categories = ["전자제품", "자동차", "반도체", "석유화학", "철강", "식품"]
    
    np.random.seed(42)
    n_records = 300
    
    data = {
        "거래ID": [f"TR-{1000 + i}" for i in range(n_records)],
        "국가": np.random.choice(countries, n_records),
        "등급": np.random.choice(grades, n_records),
        "품목": np.random.choice(categories, n_records),
        "수출액(백만 달러)": np.random.randint(10, 500, n_records),
        "수입액(백만 달러)": np.random.randint(5, 450, n_records),
    }
    df = pd.DataFrame(data)
    df["총무역액(백만 달러)"] = df["수출액(백만 달러)"] + df["수입액(백만 달러)"]
    
    # 무역액 등급 (대/중/소) 구분 기준 설정
    def categorize_trade(val):
        if val >= 600:
            return "대"
        elif val >= 300:
            return "중"
        else:
            return "소"
            
    df["무역액등급"] = df["총무역액(백만 달러)"].apply(categorize_trade)
    return df

df = load_data()

# 3. 사이드바 필터 구성
st.sidebar.title("🔍 필터 설정")

# 등급 다중 선택
selected_grades = st.sidebar.multiselect(
    "등급 선택",
    options=sorted(df["등급"].unique()),
    default=sorted(df["등급"].unique())
)

# 국가 다중 선택
selected_countries = st.sidebar.multiselect(
    "국가 선택",
    options=sorted(df["국가"].unique()),
    default=sorted(df["국가"].unique())
)

# 무역액 등급 선택 (대, 중, 소)
selected_trade_levels = st.sidebar.multiselect(
    "무역액 등급 선택",
    options=["대", "중", "소"],
    default=["대", "중", "소"]
)

# 4. 데이터 필터링 적용
filtered_df = df[
    (df["등급"].isin(selected_grades)) &
    (df["국가"].isin(selected_countries)) &
    (df["무역액등급"].isin(selected_trade_levels))
]

# 5. 메인 대시보드
st.title("🌐 무역 분석 대시보드")
st.markdown("사이드바의 필터를 활용하여 등급, 국가 및 무역 규모별 데이터를 실시간으로 분석합니다.")

# 주요 지표 (KPI)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("총 거래 건수", f"{len(filtered_df):,} 건")
with kpi2:
    st.metric("총 무역액", f"{filtered_df['총무역액(백만 달러)'].sum():,} 백만$")
with kpi3:
    st.metric("총 수출액", f"{filtered_df['수출액(백만 달러)'].sum():,} 백만$")
with kpi4:
    st.metric("총 수입액", f"{filtered_df['수입액(백만 달러)'].sum():,} 백만$")

st.divider()

# 시각화 영역 (히트맵 & 파이차트)
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 국가별 무역 규모 (히트맵)")
    if not filtered_df.empty:
        country_group = (
            filtered_df.groupby("국가")[["수출액(백만 달러)", "수입액(백만 달러)"]]
            .sum()
            .T
        )
        fig_heat = px.imshow(
            country_group,
            labels=dict(x="국가", y="구분", color="무역액 (백만 달러)"),
            x=country_group.columns,
            y=["수출액", "수입액"],
            text_auto=True,
            aspect="auto",
            color_continuous_scale="Blues",
            title="국가별 수출/수입 비교 히트맵"
        )
        fig_heat.update_layout(
            xaxis_title="국가",
            yaxis_title="구분",
            height=400
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("선택된 조건에 해당하는 데이터가 없습니다.")

with col2:
    st.subheader("🍩 무역액 등급별 비중")
    if not filtered_df.empty:
        fig_pie = px.pie(
            filtered_df,
            names="무역액등급",
            values="총무역액(백만 달러)",
            title="무역액 등급(대/중/소) 점유율",
            category_orders={"무역액등급": ["대", "중", "소"]},
            hole=0.4
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("선택된 조건에 해당하는 데이터가 없습니다.")

st.divider()

# 상위 5개국 x 무역액 등급 교차표
st.subheader("📌 상위 5개국 × 무역액 등급 교차표")
if not filtered_df.empty:
    top5_countries = (
        filtered_df.groupby("국가")["총무역액(백만 달러)"]
        .sum()
        .nlargest(5)
        .index
        .tolist()
    )
    top5_df = filtered_df[filtered_df["국가"].isin(top5_countries)]
    
    ctab = pd.crosstab(
        index=top5_df["국가"],
        columns=top5_df["무역액등급"],
        margins=True,
        margins_name="합계"
    )
    level_order = [col for col in ["대", "중", "소", "합계"] if col in ctab.columns]
    ctab = ctab[level_order]
    row_order = [c for c in top5_countries if c in ctab.index] + ["합계"]
    ctab = ctab.reindex(row_order)
    
    st.caption("※ 총 무역액 기준 상위 5개국의 거래 건수(빈도) 교차 분석표입니다.")
    st.dataframe(ctab, use_container_width=True)
else:
    st.info("선택된 조건에 해당하는 데이터가 없습니다.")

st.divider()

# 결측치 현황 확인 영역
st.subheader("🔍 결측치(Missing Values) 현황")
if not filtered_df.empty:
    missing_count = filtered_df.isnull().sum()
    missing_ratio = (missing_count / len(filtered_df)) * 100
    dtypes = filtered_df.dtypes.astype(str)

    missing_df = pd.DataFrame({
        "컬럼명": filtered_df.columns,
        "데이터 타입": dtypes.values,
        "결측치 개수": missing_count.values,
        "결측치 비율(%)": missing_ratio.round(2).values
    })

    total_missing = missing_count.sum()
    if total_missing == 0:
        st.success("✅ 현재 필터링된 데이터에 결측치가 존재하지 않습니다.")
    else:
        st.warning(f"⚠️ 총 {total_missing:,}개의 결측치가 발견되었습니다.")

    st.dataframe(missing_df, use_container_width=True)
else:
    st.info("데이터가 비어 있어 결측치를 계산할 수 없습니다.")

st.divider()

# 상세 데이터 테이블
st.subheader("📋 필터링된 데이터 상세")
st.dataframe(filtered_df, use_container_width=True)