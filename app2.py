import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

# ── 페이지 설정 ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="서울시 전기차 충전소 분석 대시보드",
    page_icon="⚡",
    layout="wide",
)

# ── 글로벌 CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #f5f7fa; }
    [data-testid="stSidebar"]          { background-color: #0f2744; }
    [data-testid="stSidebar"] *        { color: #dce8f5 !important; }
    [data-testid="stSidebar"] .stRadio > label { font-size: 0.97rem; }

    .kpi-card {
        background: linear-gradient(135deg, #1a4580, #2d79c7);
        border-radius: 14px; padding: 22px 18px;
        color: white; text-align: center; height: 100%;
    }
    .kpi-card .val { font-size: 1.75rem; font-weight: 800; margin: 0; }
    .kpi-card .lbl { font-size: 0.8rem; opacity: 0.85; margin-top: 5px; }

    .sec-title {
        border-left: 5px solid #2d79c7; padding-left: 12px;
        font-size: 1.12rem; font-weight: 700; color: #0f2744;
        margin: 28px 0 14px;
    }
    .insight {
        background: #e8f0fb; border-radius: 10px;
        padding: 13px 17px; font-size: 0.9rem;
        color: #0f2744; margin-top: 10px; line-height: 1.65;
    }
    .strat-card {
        background: white; border-radius: 12px;
        border-left: 5px solid #2d79c7;
        padding: 18px 20px; margin-bottom: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    }
    .strat-card h4 { color: #0f2744; margin: 0 0 8px; font-size: 1rem; }
    .strat-card p  { margin: 4px 0; font-size: 0.87rem; color: #334; }

    .filter-bar {
        background: #ffffff; border-radius: 12px;
        padding: 14px 20px; margin-bottom: 18px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    }
</style>
""", unsafe_allow_html=True)

# ── 원본 데이터 ───────────────────────────────────────────────────────────────
MONTHS      = ["1월","2월","3월","4월","5월","6월",
               "7월","8월","9월","10월","11월","12월"]
MONTH_IDX   = list(range(12))

FAST_KWH = [82.72, 85.87, 72.80, 66.51, 64.22, 62.88,
            62.36, 63.12, 63.47, 65.31, 68.44, 74.21]
SLOW_KWH = [30.51, 31.51, 27.42, 26.91, 26.23, 25.73,
            25.62, 25.61, 25.76, 26.35, 27.81, 29.14]
RATIO    = [2.71, 2.73, 2.65, 2.47, 2.45, 2.44,
            2.43, 2.46, 2.46, 2.48, 2.46, 2.55]

YANGJAI  = [12073.12,12311.46,12482.51,11968.63,12276.84,11993.38,
            11857.96,11924.57,11982.13,12146.40,12488.55,13021.88]
CHILDREN = [11077.44,11697.57,11403.17,10965.35,11012.24,10883.26,
            10845.41,10969.38,11023.69,11161.56,11493.21,11884.06]
APGUJUNG = [10723.77,11083.09,10821.18,10384.91,10503.72,10274.49,
            10195.21,10236.05,10289.14,10401.87,10639.62,10981.44]

# 충전소 지리 정보 (실제 서울 좌표)
STATIONS_GEO = pd.DataFrame({
    "name":        ["양재솔라스테이션", "어린이대공원 구의문 주차장 복합충전소", "강남구 압구정 나들목 앞 가로등형 충전기"],
    "short":       ["양재솔라스테이션", "어린이대공원 구의문", "압구정 나들목 가로등형"],
    "lat":         [37.4753, 37.5497, 37.5267],
    "lon":         [127.0384, 127.0895, 127.0284],
    "type":        ["급속 메인", "목적지형 복합", "가로등형 급속"],
    "rank":        ["🥇 1위", "🥈 2위", "🥉 3위"],
    "color":       ["#2d79c7", "#1e8c6e", "#d4610c"],
    "annual_kwh":  [sum(YANGJAI), sum(CHILDREN), sum(APGUJUNG)],
    "monthly_avg": [sum(YANGJAI)/12, sum(CHILDREN)/12, sum(APGUJUNG)/12],
    "monthly_data":[YANGJAI, CHILDREN, APGUJUNG],
    "months_top3": [12, 5, 8],
    "feature":     [
        "교통 요충지 + 대형 주차 인프라",
        "목적지형 — 공원·여가 체류 충전",
        "비아파트 거주지 핵심 가로등형",
    ],
})

STRATEGIES = [
    {"color":"#2d79c7","icon":"⚡","title":"급속 이용자 즉시성 마케팅",
     "insight":"급속 이용자는 '짧은 체류·즉시성·경로 편의'에 민감",
     "target":"출퇴근 이동자, 택시/법인차, 장거리 EV 운전자",
     "action":"충전소 3~5km 내 디지털 광고, 길찾기 앱 연동 프로모션, 즉시 할인 쿠폰",
     "effect":"급속 이용 전환율 상승, 유휴 시간대 사용 증가"},
    {"color":"#1e8c6e","icon":"❄️","title":"동절기 안심 충전 캠페인",
     "insight":"겨울철 주행 효율 저하 → 보충 충전 수요 집중 (12~2월 피크)",
     "target":"주행거리 민감 고객, 장거리 운전자",
     "action":"12~2월 한정 '겨울 안심 충전 패키지', 충전량 기준 리워드, 배터리 관리 콘텐츠",
     "effect":"겨울철 충전량 방어 및 재방문률 증가"},
    {"color":"#d4610c","icon":"📍","title":"상위 거점 상권 연계 제휴 (B2B)",
     "insight":"상위 충전소는 입지 우위와 수요 집중이 동시에 발생",
     "target":"주변 상권 이용자, 인근 직장인, 방문객",
     "action":"카페·편의점·쇼핑몰과 제휴, 충전 대기 시간 혜택 (Charge & Drink 쿠폰)",
     "effect":"체류 시간 내 부가매출 확대, 충전소 이용 만족도 향상"},
    {"color":"#7b3fc4","icon":"🏅","title":"반복 방문 로열티 프로그램",
     "insight":"반복 상위 거점은 브랜드 노출 효과가 높고 충성 고객이 집중됨",
     "target":"정기 방문자, 상습 이용자",
     "action":"멤버십·스탬프형 로열티, 상위 거점 전용 혜택, 재방문 리마인드 메시지",
     "effect":"충성 고객 유지, 특정 거점 점유율 강화"},
    {"color":"#336b87","icon":"🏠","title":"완속 생활권 타겟 마케팅",
     "insight":"완속 충전은 주거·생활권 충전 습관과 연결된 안정 수요",
     "target":"아파트 거주자, 장시간 주차 고객, 야간 충전자",
     "action":"야간 요금 안내, 주거권 기반 푸시 알림, 예약형 완속 충전 추천",
     "effect":"완속 점유율 개선, 야간 비혼잡 시간대 분산"},
]

# ── 사이드바 ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚡ 서울시\n## 전기차 충전소 분석")
    st.caption("데이터 기간: 2025년 1월 ~ 12월")
    st.divider()
    view = st.radio("📌 섹션 선택", [
        "📊 개요 대시보드",
        "📈 월별 충전 패턴",
        "📍 핵심 거점 분석",
        "🗺️ 지도 시각화",
        "🎯 마케팅 전략",
    ])
    st.divider()

    # ── 전역 필터 (사이드바) ──
    st.markdown("### 🔧 전역 필터")
    sel_months = st.multiselect(
        "분석 월 선택",
        options=MONTHS,
        default=MONTHS,
        help="선택한 월의 데이터만 반영됩니다.",
    )
    sel_type = st.radio(
        "충전기 유형",
        ["전체", "급속만", "완속만"],
        horizontal=True,
    )
    st.divider()
    st.caption("작성: 시니어 데이터 분석가\n작성일: 2026-03-21")

# ── 필터 인덱스 계산 ──────────────────────────────────────────────────────────
if not sel_months:
    sel_months = MONTHS   # 아무것도 선택 안 하면 전체

sel_idx = [MONTHS.index(m) for m in sel_months]

f_fast = [FAST_KWH[i] for i in sel_idx]
f_slow = [SLOW_KWH[i] for i in sel_idx]
f_ratio= [RATIO[i]    for i in sel_idx]
f_mon  = [MONTHS[i]   for i in sel_idx]

f_yangjai  = [YANGJAI[i]  for i in sel_idx]
f_children = [CHILDREN[i] for i in sel_idx]
f_apgujung = [APGUJUNG[i] for i in sel_idx]

# 유형 필터에 따라 보여줄 계열
show_fast = sel_type in ["전체", "급속만"]
show_slow = sel_type in ["전체", "완속만"]

avg_fast = sum(f_fast)/len(f_fast) if f_fast else 0
avg_slow = sum(f_slow)/len(f_slow) if f_slow else 0

# ─────────────────────────────────────────────────────────────────────────────
# 섹션 1 : 개요 대시보드
# ─────────────────────────────────────────────────────────────────────────────
if view == "📊 개요 대시보드":
    st.title("⚡ 서울시 전기차 충전소 이용 패턴 분석")
    st.caption("2025년 1~12월 | 시니어 데이터 분석가 겸 마케팅 전략가")

    # 필터 상태 배지
    st.info(f"🔧 현재 필터: **{', '.join(sel_months)}** | 충전기 유형: **{sel_type}**")
    st.divider()

    # KPI 카드
    c1,c2,c3,c4,c5 = st.columns(5)
    kpis = [
        (f"{avg_fast:.1f} kWh", f"급속 평균 ({len(sel_months)}개월)"),
        (f"{avg_slow:.1f} kWh", f"완속 평균 ({len(sel_months)}개월)"),
        (f"{avg_fast/avg_slow:.2f}x" if avg_slow else "—", "급속/완속 배율"),
        (f"{max(f_fast):.2f} kWh", f"급속 최고 ({f_mon[f_fast.index(max(f_fast))]})"),
        ("13,022 kWh", "1위 거점 12월 최고"),
    ]
    for col,(val,lbl) in zip([c1,c2,c3,c4,c5], kpis):
        col.markdown(f"""<div class="kpi-card">
            <p class="val">{val}</p><p class="lbl">{lbl}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec-title">핵심 인사이트</div>', unsafe_allow_html=True)
    il,ir = st.columns(2)
    with il:
        st.markdown('<div class="insight">⚡ <b>급속 우위 구조</b><br>급속은 전 월에서 완속 대비 2.4~2.7배 높은 사용량을 일관되게 유지합니다.</div>', unsafe_allow_html=True)
        st.markdown('<div class="insight">❄️ <b>계절성: 겨울 피크, 여름 저점</b><br>1~2월 최고, 5~8월 최저. 동절기 배터리 효율 저하로 보충 충전 수요가 집중됩니다.</div>', unsafe_allow_html=True)
    with ir:
        st.markdown('<div class="insight">📍 <b>집중형 수요 구조</b><br>양재솔라스테이션이 12개월 내내 1위. 상위 3개 거점이 월간 랭킹을 독점합니다.</div>', unsafe_allow_html=True)
        st.markdown('<div class="insight">🏠 <b>완속의 안정성</b><br>25.6~31.5 kWh 좁은 밴드 유지. 주거지·장시간 체류 기반 습관형 수요입니다.</div>', unsafe_allow_html=True)

    st.markdown('<div class="sec-title">한눈에 보는 데이터 (필터 반영)</div>', unsafe_allow_html=True)
    ch1, ch2 = st.columns(2)

    with ch1:
        fig_ov1 = go.Figure()
        if show_fast:
            fig_ov1.add_trace(go.Scatter(x=f_mon, y=f_fast, name="급속",
                fill="tozeroy", line=dict(color="#2d79c7",width=2),
                fillcolor="rgba(45,121,199,0.15)"))
        if show_slow:
            fig_ov1.add_trace(go.Scatter(x=f_mon, y=f_slow, name="완속",
                fill="tozeroy", line=dict(color="#f4a261",width=2),
                fillcolor="rgba(244,162,97,0.15)"))
        fig_ov1.update_layout(title="월별 평균 충전량 추이", height=290,
            margin=dict(t=40,b=20,l=20,r=20),
            legend=dict(orientation="h",y=1.15), yaxis_title="kWh")
        st.plotly_chart(fig_ov1, use_container_width=True)

    with ch2:
        fig_ov2 = go.Figure()
        for sname, sdata, scolor in [
            ("양재솔라스테이션", f_yangjai, "#2d79c7"),
            ("어린이대공원 구의문", f_children, "#1e8c6e"),
            ("압구정 나들목", f_apgujung, "#d4610c"),
        ]:
            fig_ov2.add_trace(go.Scatter(x=f_mon, y=sdata, name=sname,
                mode="lines+markers", line=dict(color=scolor,width=2),
                marker=dict(size=5)))
        fig_ov2.update_layout(title="핵심 3개 거점 월별 사용량", height=290,
            margin=dict(t=40,b=20,l=20,r=20),
            legend=dict(orientation="h",y=1.15,font=dict(size=10)),
            yaxis_title="kWh")
        st.plotly_chart(fig_ov2, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# 섹션 2 : 월별 충전 패턴
# ─────────────────────────────────────────────────────────────────────────────
elif view == "📈 월별 충전 패턴":
    st.title("📈 충전기 유형별 월간 사용 패턴")
    st.info(f"🔧 필터 적용 중: **{', '.join(sel_months)}** | 유형: **{sel_type}**")
    st.divider()

    # ── 인라인 필터 바 ──
    with st.container():
        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
        fc1, fc2 = st.columns([2,1])
        with fc1:
            range_sel = st.select_slider(
                "📅 월 범위 선택 (추이 차트용)",
                options=MONTHS,
                value=(MONTHS[0], MONTHS[-1]),
            )
        with fc2:
            show_annotation = st.checkbox("최고·최저 어노테이션 표시", value=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 슬라이더 범위 적용
    r_start = MONTHS.index(range_sel[0])
    r_end   = MONTHS.index(range_sel[1]) + 1
    r_idx   = list(range(r_start, r_end))
    r_fast  = [FAST_KWH[i] for i in r_idx]
    r_slow  = [SLOW_KWH[i] for i in r_idx]
    r_ratio = [RATIO[i]    for i in r_idx]
    r_mon   = [MONTHS[i]   for i in r_idx]

    tab1, tab2, tab3 = st.tabs(["📉 추이 비교", "📊 비율 분석", "📋 원본 데이터"])

    with tab1:
        fig1 = go.Figure()
        if show_fast:
            fig1.add_trace(go.Scatter(x=r_mon, y=r_fast, name="급속 (kWh)",
                mode="lines+markers", line=dict(color="#2d79c7",width=3),
                marker=dict(size=9)))
        if show_slow:
            fig1.add_trace(go.Scatter(x=r_mon, y=r_slow, name="완속 (kWh)",
                mode="lines+markers", line=dict(color="#f4a261",width=3),
                marker=dict(size=9,symbol="diamond")))
        if show_annotation and r_fast:
            mx_i = r_fast.index(max(r_fast))
            mn_i = r_fast.index(min(r_fast))
            fig1.add_annotation(x=r_mon[mx_i], y=r_fast[mx_i],
                text=f"최고 {r_fast[mx_i]:.2f} kWh",
                showarrow=True, arrowhead=2,
                font=dict(color="#2d79c7",size=11), ax=40, ay=-35)
            fig1.add_annotation(x=r_mon[mn_i], y=r_fast[mn_i],
                text=f"최저 {r_fast[mn_i]:.2f} kWh",
                showarrow=True, arrowhead=2,
                font=dict(color="#c0392b",size=11), ax=40, ay=35)
        fig1.update_layout(
            title=f"월별 급속/완속 평균 충전량 ({range_sel[0]} ~ {range_sel[1]})",
            xaxis_title="월", yaxis_title="월평균 kWh",
            hovermode="x unified", height=430,
            legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown("""<div class="insight">
        💡 급속은 겨울(1~2월) 피크 → 여름(7월) 저점의 계절 곡선을 그립니다.
        완속은 좁은 밴드에서 연중 안정적으로 유지됩니다.
        </div>""", unsafe_allow_html=True)

    with tab2:
        col_a, col_b = st.columns(2)
        with col_a:
            fig2 = go.Figure(go.Bar(
                x=r_mon, y=r_ratio,
                marker_color=["#2d79c7" if v >= 2.6 else "#7fb3e0" for v in r_ratio],
                text=[f"{v:.2f}x" for v in r_ratio],
                textposition="outside",
            ))
            fig2.update_layout(title="월별 급속/완속 비율",
                xaxis_title="월", yaxis_title="배율",
                height=380, yaxis_range=[2.2, 2.9])
            st.plotly_chart(fig2, use_container_width=True)
        with col_b:
            a_f = sum(r_fast)/len(r_fast) if r_fast else 1
            a_s = sum(r_slow)/len(r_slow) if r_slow else 1
            vals, names = [], []
            if show_fast: vals.append(a_f); names.append("급속")
            if show_slow: vals.append(a_s); names.append("완속")
            fig3 = px.pie(values=vals, names=names,
                color_discrete_sequence=["#2d79c7","#f4a261"],
                title=f"선택 기간 평균 충전량 구성<br>({range_sel[0]}~{range_sel[1]})",
                hole=0.45)
            fig3.update_traces(textinfo="percent+label")
            fig3.update_layout(height=380)
            st.plotly_chart(fig3, use_container_width=True)
        st.markdown("""<div class="insight">
        💡 겨울(12~2월) 비율 2.55~2.73, 여름(6~8월) 비율 2.43~2.46.
        겨울철 급속 수요가 더 크게 증가하는 계절 비대칭이 나타납니다.
        </div>""", unsafe_allow_html=True)

    with tab3:
        df_view = pd.DataFrame({
            "월": r_mon,
            "급속(kWh)": r_fast,
            "완속(kWh)": r_slow,
            "급속/완속 비율": r_ratio,
        })
        cols_to_show = ["월"]
        if show_fast: cols_to_show += ["급속(kWh)"]
        if show_slow: cols_to_show += ["완속(kWh)"]
        cols_to_show += ["급속/완속 비율"]

        styled = df_view[cols_to_show].style.format({
            "급속(kWh)": "{:.2f}", "완속(kWh)": "{:.2f}",
            "급속/완속 비율": "{:.2f}"
        })
        if "급속(kWh)" in cols_to_show:
            styled = styled.background_gradient(subset=["급속(kWh)"], cmap="Blues")
        if "완속(kWh)" in cols_to_show:
            styled = styled.background_gradient(subset=["완속(kWh)"], cmap="Oranges")
        st.dataframe(styled, use_container_width=True, height=460)

        csv = df_view[cols_to_show].to_csv(index=False, encoding="utf-8-sig")
        st.download_button("⬇️ CSV 다운로드", data=csv,
            file_name="월별충전패턴.csv", mime="text/csv")

# ─────────────────────────────────────────────────────────────────────────────
# 섹션 3 : 핵심 거점 분석
# ─────────────────────────────────────────────────────────────────────────────
elif view == "📍 핵심 거점 분석":
    st.title("📍 월별 상위 3개 핵심 거점")
    st.info(f"🔧 필터 적용 중: **{', '.join(sel_months)}** | 유형: **{sel_type}**")
    st.divider()

    # ── 인라인 필터 ──
    with st.container():
        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
        gc1, gc2 = st.columns(2)
        with gc1:
            sel_stations = st.multiselect(
                "📍 거점 선택",
                options=["양재솔라스테이션","어린이대공원 구의문","압구정 나들목 가로등형"],
                default=["양재솔라스테이션","어린이대공원 구의문","압구정 나들목 가로등형"],
            )
        with gc2:
            chart_type = st.radio("차트 유형", ["라인", "바", "누적 영역"],
                horizontal=True)
        st.markdown('</div>', unsafe_allow_html=True)

    station_map = {
        "양재솔라스테이션":      (f_yangjai,  "#2d79c7", "circle"),
        "어린이대공원 구의문":   (f_children, "#1e8c6e", "diamond"),
        "압구정 나들목 가로등형": (f_apgujung, "#d4610c", "square"),
    }

    # 메트릭 카드
    mc = st.columns(len(sel_stations)) if sel_stations else st.columns(1)
    descs = {"양재솔라스테이션":"12개월 연속 1위",
             "어린이대공원 구의문":"목적지형 충전 대표",
             "압구정 나들목 가로등형":"비아파트 핵심 거점"}
    ranks = {"양재솔라스테이션":"🥇","어린이대공원 구의문":"🥈","압구정 나들목 가로등형":"🥉"}
    for col, sname in zip(mc, sel_stations):
        data, color, _ = station_map[sname]
        col.metric(f"{ranks[sname]} {sname}",
            f"{sum(data)/len(data):,.0f} kWh/월",
            descs[sname])

    tab_a, tab_b, tab_c = st.tabs(["📈 월별 추이", "📊 연간 비교", "📋 월별 원본"])

    with tab_a:
        fig_s1 = go.Figure()
        for sname in sel_stations:
            data, color, symbol = station_map[sname]
            if chart_type == "라인":
                fig_s1.add_trace(go.Scatter(x=f_mon, y=data, name=sname,
                    mode="lines+markers", line=dict(color=color, width=2.5),
                    marker=dict(size=8, symbol=symbol)))
            elif chart_type == "바":
                fig_s1.add_trace(go.Bar(x=f_mon, y=data, name=sname,
                    marker_color=color))
            else:  # 누적 영역
                fig_s1.add_trace(go.Scatter(x=f_mon, y=data, name=sname,
                    mode="lines", fill="tonexty",
                    line=dict(color=color, width=1.5),
                    fillcolor=color.replace("#","rgba(").replace(
                        "2d79c7","45,121,199,0.3").replace(
                        "1e8c6e","30,140,110,0.3").replace(
                        "d4610c","212,97,12,0.3") + ")"))
        if chart_type == "바":
            fig_s1.update_layout(barmode="group")
        fig_s1.update_layout(
            title="핵심 거점 월별 사용량 추이 (kWh)",
            xaxis_title="월", yaxis_title="kWh",
            hovermode="x unified", height=430,
            legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig_s1, use_container_width=True)

    with tab_b:
        annual_data = []
        for sname in sel_stations:
            data, color, _ = station_map[sname]
            annual_data.append({"충전소": sname,
                "연간합계(kWh)": sum(data),
                "월평균(kWh)": sum(data)/len(data)})
        df_ann = pd.DataFrame(annual_data)
        fig_s2 = px.bar(df_ann, x="충전소", y="연간합계(kWh)", color="충전소",
            color_discrete_sequence=["#2d79c7","#1e8c6e","#d4610c"],
            text="연간합계(kWh)",
            title=f"거점별 총 사용량 ({', '.join(sel_months)})",
            height=400)
        fig_s2.update_traces(texttemplate="%{text:,.0f} kWh",
            textposition="outside")
        st.plotly_chart(fig_s2, use_container_width=True)
        st.markdown("""<div class="insight">
        💡 상위 3개 거점이 순위를 고정적으로 유지하는 <b>집중형 수요 구조</b>는
        신규 거점 개발보다 <b>기존 상위 거점 강화가 더 효율적</b>임을 시사합니다.
        </div>""", unsafe_allow_html=True)

    with tab_c:
        rank_rows = []
        for i, m in enumerate(f_mon):
            row = {"월": m}
            for sname in sel_stations:
                data, _, _ = station_map[sname]
                row[sname] = f"{data[i]:,.2f} kWh"
            rank_rows.append(row)
        df_rank = pd.DataFrame(rank_rows)
        st.dataframe(df_rank, use_container_width=True, height=470)
        csv2 = df_rank.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("⬇️ CSV 다운로드", data=csv2,
            file_name="핵심거점월별.csv", mime="text/csv")

# ─────────────────────────────────────────────────────────────────────────────
# 섹션 4 : 지도 시각화
# ─────────────────────────────────────────────────────────────────────────────
elif view == "🗺️ 지도 시각화":
    st.title("🗺️ 핵심 충전소 지도 시각화")
    st.divider()

    # ── 지도 필터 컨트롤 ──
    with st.container():
        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            map_month = st.selectbox("📅 기준 월 선택", MONTHS, index=0)
        with mc2:
            map_metric = st.radio("📊 버블 크기 기준",
                ["월별 사용량", "연간 합계"], horizontal=True)
        with mc3:
            map_style = st.selectbox("🗺️ 지도 스타일", [
                "OpenStreetMap", "CartoDB positron", "CartoDB dark_matter",
            ])
        st.markdown('</div>', unsafe_allow_html=True)

    m_idx = MONTHS.index(map_month)

    # 월별 사용량 계산
    station_kwh_month = [YANGJAI[m_idx], CHILDREN[m_idx], APGUJUNG[m_idx]]
    station_kwh_annual= [sum(YANGJAI), sum(CHILDREN), sum(APGUJUNG)]

    kwh_for_bubble = (station_kwh_month if map_metric == "월별 사용량"
                      else station_kwh_annual)

    # folium 지도 생성
    m = folium.Map(
        location=[37.515, 127.045],
        zoom_start=12,
        tiles=map_style,
    )

    colors_hex = ["#2d79c7", "#1e8c6e", "#d4610c"]
    radius_scale = 25 if map_metric == "월별 사용량" else 0.002

    for _, row in STATIONS_GEO.iterrows():
        i = STATIONS_GEO.index.get_loc(_)
        kwh_val = kwh_for_bubble[i]
        radius  = (kwh_val / max(kwh_for_bubble)) * 60 + 15

        # 버블 원
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=radius,
            color=colors_hex[i],
            fill=True,
            fill_color=colors_hex[i],
            fill_opacity=0.55,
            weight=2,
            popup=folium.Popup(
                f"""
                <div style="font-family:sans-serif;min-width:200px">
                  <h4 style="color:{colors_hex[i]};margin:0 0 6px">{row['rank']} {row['short']}</h4>
                  <b>유형:</b> {row['type']}<br>
                  <b>특징:</b> {row['feature']}<br>
                  <hr style="margin:6px 0">
                  <b>{map_month} 사용량:</b> {station_kwh_month[i]:,.2f} kWh<br>
                  <b>연간 합계:</b> {station_kwh_annual[i]:,.0f} kWh<br>
                  <b>월평균:</b> {station_kwh_annual[i]/12:,.0f} kWh<br>
                  <b>상위 3위 등장:</b> {row['months_top3']}개월
                </div>
                """,
                max_width=260,
            ),
            tooltip=f"{row['rank']} {row['short']} | {kwh_val:,.0f} kWh",
        ).add_to(m)

        # 레이블 마커
        folium.Marker(
            location=[row["lat"] + 0.003, row["lon"]],
            icon=folium.DivIcon(
                html=f"""<div style="
                    font-size:11px;font-weight:700;
                    color:{colors_hex[i]};
                    background:white;
                    border:1.5px solid {colors_hex[i]};
                    border-radius:6px;
                    padding:3px 7px;
                    white-space:nowrap;
                    box-shadow:0 1px 4px rgba(0,0,0,0.2)">
                    {row['rank']} {row['short']}
                </div>""",
                icon_size=(200, 30),
                icon_anchor=(100, 30),
            ),
        ).add_to(m)

    # 지도 출력
    col_map, col_info = st.columns([3, 1])
    with col_map:
        map_result = st_folium(m, width=None, height=520)

    with col_info:
        st.markdown("#### 📋 거점 정보")
        for i, row in STATIONS_GEO.iterrows():
            kwh_val = kwh_for_bubble[i]
            st.markdown(f"""
            <div style="background:white;border-radius:10px;
                border-left:4px solid {colors_hex[i]};
                padding:12px 14px;margin-bottom:10px;
                box-shadow:0 1px 5px rgba(0,0,0,0.07)">
                <b style="color:{colors_hex[i]}">{row['rank']} {row['short']}</b><br>
                <span style="font-size:0.82rem;color:#555">{row['type']}</span><br>
                <span style="font-size:0.9rem">
                    {map_month}: <b>{station_kwh_month[i]:,.0f} kWh</b>
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### 💡 범례")
        st.markdown("""
        - 🔵 **버블 크기** = 선택 기준 사용량
        - 클릭 시 상세 팝업 표시
        - 호버 시 kWh 수치 확인
        """)

    # 월별 슬라이더 비교 차트
    st.divider()
    st.markdown('<div class="sec-title">월별 거점별 사용량 변화 (슬라이더 연동)</div>',
        unsafe_allow_html=True)

    fig_map_bar = go.Figure()
    for sname, sdata, scolor in [
        ("양재솔라스테이션", YANGJAI, "#2d79c7"),
        ("어린이대공원 구의문", CHILDREN, "#1e8c6e"),
        ("압구정 나들목 가로등형", APGUJUNG, "#d4610c"),
    ]:
        fig_map_bar.add_trace(go.Bar(
            x=MONTHS, y=sdata, name=sname,
            marker_color=scolor,
            opacity=[1.0 if m == map_month else 0.35 for m in MONTHS],
        ))
    # 선택된 월 강조선
    fig_map_bar.add_vline(
        x=map_month, line_width=2,
        line_dash="dash", line_color="#e74c3c",
        annotation_text=f"선택: {map_month}",
        annotation_position="top",
    )
    fig_map_bar.update_layout(
        barmode="group",
        title=f"거점별 월별 사용량 — 현재 선택: {map_month}",
        xaxis_title="월", yaxis_title="kWh",
        hovermode="x unified", height=370,
        legend=dict(orientation="h", y=1.12),
    )
    st.plotly_chart(fig_map_bar, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# 섹션 5 : 마케팅 전략
# ─────────────────────────────────────────────────────────────────────────────
elif view == "🎯 마케팅 전략":
    st.title("🎯 마케팅 실행 전략 (Action Plan)")
    st.divider()

    # ── 필터: 전략 카테고리 ──
    with st.container():
        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
        strat_filter = st.multiselect(
            "🎯 표시할 전략 선택",
            options=[s["title"] for s in STRATEGIES],
            default=[s["title"] for s in STRATEGIES],
        )
        st.markdown('</div>', unsafe_allow_html=True)

    for s in STRATEGIES:
        if s["title"] not in strat_filter:
            continue
        st.markdown(f"""
        <div class="strat-card" style="border-left-color:{s['color']}">
            <h4>{s['icon']} {s['title']}</h4>
            <p>📌 <b>인사이트:</b> {s['insight']}</p>
            <p>👤 <b>타겟:</b> {s['target']}</p>
            <p>🚀 <b>실행:</b> {s['action']}</p>
            <p>✅ <b>기대 효과:</b> {s['effect']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### 📌 종합 제언")
    col1, col2 = st.columns(2)
    with col1:
        st.info("💡 **핵심 원칙**\n\n'급속 충전소의 입지 = 매출'\n\n'가로등형 충전기 = 비아파트 핵심 대안'")
        st.error("❌ **피해야 할 것**\n\n신규 고객 유입에만 집중하는 분산 투자")
    with col2:
        st.success("✅ **권고 방향**\n\n상위 10% 거점의 편의 시설 확충에 마케팅 예산 집중 투자")
        st.warning("⚠️ **우선 순위**\n\n1. 양재솔라스테이션 로열티 강화\n2. 동절기 캠페인 선제 준비\n3. B2B 상권 제휴 협약 체결")
