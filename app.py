import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="서울시 전기차 충전소 분석",
    page_icon="⚡",
    layout="wide",
)

# ── 커스텀 CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f, #2d6a9f);
        border-radius: 12px;
        padding: 20px;
        color: white;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-card h2 { margin: 0; font-size: 2rem; }
    .metric-card p  { margin: 4px 0 0; opacity: 0.85; font-size: 0.9rem; }
    .section-title {
        border-left: 4px solid #2d6a9f;
        padding-left: 12px;
        margin: 30px 0 16px;
        font-size: 1.2rem;
        font-weight: 700;
        color: #1e3a5f;
    }
    .insight-box {
        background: #eef4fb;
        border-radius: 8px;
        padding: 14px 18px;
        margin-top: 8px;
        font-size: 0.92rem;
        color: #1e3a5f;
    }
</style>
""", unsafe_allow_html=True)

# ── 데이터 정의 ──────────────────────────────────────────────
months = ["1월","2월","3월","4월","5월","6월","7월","8월","9월","10월","11월","12월"]

# 월별 사용량 (단위: kWh, 보고서 수치 기반 추정)
fast_kwh  = [82, 80, 78, 75, 74, 70, 65, 64, 65, 66, 70, 74]
slow_kwh  = [29, 28, 28, 27, 27, 27, 26, 26, 26, 27, 27, 28]

df_monthly = pd.DataFrame({
    "월": months,
    "급속 (kWh)": fast_kwh,
    "완속 (kWh)": slow_kwh,
})

# 상위 거점 데이터
stations = pd.DataFrame({
    "충전소":   ["양재솔라스테이션", "어린이대공원\n구의문 복합충전소", "강남구 압구정\n나들목 앞"],
    "월평균(kWh)": [12000, 8400, 7200],
    "유형":     ["급속 메인", "목적지형", "가로등형"],
    "순위":     ["🥇 1위", "🥈 2위", "🥉 3위"],
})

# ── 사이드바 ─────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/electric-vehicle.png", width=80)
    st.title("서울시 전기차\n충전소 분석")
    st.caption("데이터 기준: 2025년 1월 ~ 12월")
    st.divider()
    view = st.radio("📌 섹션 이동", [
        "📊 개요",
        "📈 월별 충전 패턴",
        "📍 핵심 거점 현황",
        "🎯 마케팅 전략",
    ])

# ── 메인 콘텐츠 ─────────────────────────────────────────────

# ── 1. 개요 ─────────────────────────────────────────────────
if view == "📊 개요":
    st.title("⚡ 서울시 전기차 충전소 이용 패턴 분석")
    st.caption("작성일: 2026-03-21 | 시니어 데이터 분석가 겸 마케팅 전략가")
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""<div class="metric-card">
            <h2>71.8 kWh</h2><p>급속 충전 연간 평균</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="metric-card">
            <h2>27.4 kWh</h2><p>완속 충전 연간 평균</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="metric-card">
            <h2>2.6x</h2><p>급속 / 완속 사용량 배율</p></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown("""<div class="metric-card">
            <h2>12,000 kWh</h2><p>1위 거점 월평균 사용량</p></div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">분석 요약</div>', unsafe_allow_html=True)
    st.markdown("""
    본 보고서는 2025년 한 해 서울시 전기차 충전소 이용 데이터를 분석하여
    **충전기 유형별 패턴**, **핵심 거점 현황**, **마케팅 전략**을 도출하였습니다.

    - 급속 충전은 **계절(온도)에 민감**하게 반응하며 동절기에 수요 급증
    - 완속 충전은 **주거지 기반 고정 수요**로 변동폭이 매우 낮음
    - **양재솔라스테이션**이 연중 부동의 1위 기록 (월평균 ~12,000 kWh)
    - 급속-상권 연계 및 계절 캠페인 전략으로 마케팅 효율 극대화 가능
    """)

    st.markdown('<div class="section-title">핵심 인사이트</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.info("🔥 **입지 = 매출**: 교통 요충지 및 체류 명분이 있는 거점이 압도적 성과를 기록합니다.")
        st.info("❄️ **동절기 수요 +15%**: 12~2월 급속 수요가 평소보다 15% 이상 증가합니다.")
    with c2:
        st.info("🏠 **가로등형 충전기**: 비아파트 거주지의 핵심 충전 인프라 대안으로 부상합니다.")
        st.info("☕ **틈새 시간 30~40분**: 급속 이용자의 대기 시간을 상권 연계로 전환할 기회입니다.")

# ── 2. 월별 충전 패턴 ────────────────────────────────────────
elif view == "📈 월별 충전 패턴":
    st.title("📈 월별 충전 패턴 분석")
    st.caption("2025년 1월 ~ 12월 | 단위: kWh")
    st.divider()

    tab1, tab2 = st.tabs(["📉 월별 추이", "📊 상반기 vs 하반기"])

    with tab1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=months, y=fast_kwh, mode="lines+markers",
            name="급속", line=dict(color="#2d6a9f", width=3),
            marker=dict(size=8)
        ))
        fig.add_trace(go.Scatter(
            x=months, y=slow_kwh, mode="lines+markers",
            name="완속", line=dict(color="#f4a261", width=3),
            marker=dict(size=8)
        ))
        fig.update_layout(
            title="월별 평균 충전량 추이 (급속 vs 완속)",
            xaxis_title="월", yaxis_title="평균 사용량 (kWh)",
            hovermode="x unified", height=420,
            legend=dict(orientation="h", y=1.12),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="insight-box">💡 <b>인사이트:</b> 급속 충전은 동절기(1~2월) 피크 이후 완만하게 하락하다 12월에 반등(74.2kWh)합니다. 완속은 연중 26~29kWh로 매우 안정적입니다.</div>', unsafe_allow_html=True)

    with tab2:
        compare_data = pd.DataFrame({
            "구분":   ["상반기 (1~6월)", "하반기 (7~12월)"],
            "급속 (kWh)": [77.4, 66.2],
            "완속 (kWh)": [28.1, 26.7],
        })
        fig2 = px.bar(
            compare_data.melt(id_vars="구분", var_name="충전 유형", value_name="kWh"),
            x="구분", y="kWh", color="충전 유형",
            barmode="group",
            color_discrete_map={"급속 (kWh)": "#2d6a9f", "완속 (kWh)": "#f4a261"},
            title="상반기 vs 하반기 평균 충전량 비교",
            height=400,
        )
        st.plotly_chart(fig2, use_container_width=True)

        col1, col2 = st.columns(2)
        col1.metric("상반기 급속 평균", "77.4 kWh", "+11.2 vs 하반기")
        col2.metric("하반기 급속 평균", "66.2 kWh", "-14.4% vs 상반기")

# ── 3. 핵심 거점 현황 ────────────────────────────────────────
elif view == "📍 핵심 거점 현황":
    st.title("📍 상위 3개 핵심 거점")
    st.caption("월평균 사용량 기준 Top-Tier Stations")
    st.divider()

    for _, row in stations.iterrows():
        with st.expander(f"{row['순위']}  {row['충전소'].replace(chr(10), ' ')}  |  {row['유형']}"):
            c1, c2 = st.columns([1, 2])
            c1.metric("월평균 사용량", f"{row['월평균(kWh)']:,} kWh")
            c2.markdown(f"""
            **입지 유형:** {row['유형']}
            
            **성과 요인 가설**
            - 🚗 교통 요충지: 나들목 및 주요 대로변 위치
            - 🛍️ 체류 명분: 공원·쇼핑·업무 인프라 인접
            """)

    st.divider()
    fig3 = px.bar(
        stations,
        x="충전소", y="월평균(kWh)", color="유형",
        text="월평균(kWh)",
        title="핵심 거점 월평균 사용량 비교",
        color_discrete_sequence=["#2d6a9f", "#3ab0a0", "#f4a261"],
        height=380,
    )
    fig3.update_traces(texttemplate="%{text:,} kWh", textposition="outside")
    fig3.update_xaxes(tickfont_size=11)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<div class="insight-box">💡 <b>핵심:</b> "급속 충전소의 입지가 곧 매출"입니다. 상위 10% 거점의 편의 시설 확충에 마케팅 예산을 집중 투자하는 것을 권고합니다.</div>', unsafe_allow_html=True)

# ── 4. 마케팅 전략 ───────────────────────────────────────────
elif view == "🎯 마케팅 전략":
    st.title("🎯 마케팅 실행 전략 (Action Plan)")
    st.divider()

    st.markdown('<div class="section-title">전략 1: 거점 중심 로열티 프로그램</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("대상 거점", "상위 3개소")
        st.metric("반복 방문율", "매우 높음 📈")
    with col2:
        st.markdown("""
        **실행 방안**
        - 🎫 상위 3개 거점 전용 **'스탬프 투어'** 도입
        - 💳 **'단골 할인제'** (충전 횟수 누적 → 포인트 적립)
        
        **기대 효과**
        - 핵심 거점 점유율 고착화 및 사용자 충성도 제고
        """)

    st.divider()
    st.markdown('<div class="section-title">전략 2: 동절기 에너지 방어 캠페인</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("동절기 수요 증가", "+15% 이상")
        st.metric("대상 기간", "12월 ~ 2월")
    with col2:
        st.markdown("""
        **실행 방안**
        - 🧤 **'겨울 안심 충전 패키지'**: 급속 충전 시 핫팩 증정
        - ☕ 인근 카페 할인권 제공 연계
        
        **기대 효과**
        - 겨울철 충전 대기 불만 → 긍정적 브랜드 경험으로 전환
        """)

    st.divider()
    st.markdown('<div class="section-title">전략 3: 급속-상권 연계 제휴 (B2B)</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("이용자 틈새 시간", "30~40분")
        st.metric("제휴 유형", "편의점·커피숍")
    with col2:
        st.markdown("""
        **실행 방안**
        - ☕ 압구정·어린이대공원 인근 상권과 **'Charge & Drink'** 쿠폰 발행
        - 🤝 B2B 파트너십 체결로 양방향 마케팅 효과 창출
        
        **기대 효과**
        - 지역 상권 활성화 + 충전 편의성 만족도 증대
        """)

    st.divider()
    st.markdown("### 📌 종합 제언")
    st.success("""
    **향후 마케팅 예산 배분 원칙**
    
    신규 고객 유입보다 **상위 10% 거점의 편의 시설 확충**에 집중 투자를 권고합니다.  
    가로등형 충전기는 비아파트 거주지의 핵심 대안으로, 거점 확장 시 우선 검토 대상입니다.
    """)
