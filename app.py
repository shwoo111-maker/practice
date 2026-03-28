import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import warnings, os

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="서울시 교통 접근성 분석 강의",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=JetBrains+Mono:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1b2a 0%, #1b2d3e 100%); border-right: 1px solid #2a4a6b; }
[data-testid="stSidebar"] * { color: #c8dff0 !important; }
[data-testid="stAppViewContainer"] { background-color: #f0f4f8; }
.lecture-header { background: linear-gradient(135deg, #0d1b2a 0%, #1e3a5f 50%, #0d4f8c 100%); border-radius: 16px; padding: 36px 40px; color: white; margin-bottom: 24px; position: relative; overflow: hidden; }
.lecture-header h1 { font-size: 1.9rem; font-weight: 900; margin: 0 0 8px; letter-spacing: -0.5px; }
.lecture-header p { font-size: 0.95rem; opacity: 0.75; margin: 0; }
.lecture-badge { display: inline-block; background: rgba(100,180,255,0.25); border: 1px solid rgba(100,180,255,0.4); border-radius: 20px; padding: 4px 14px; font-size: 0.78rem; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 12px; color: #7ec8f5 !important; }
.section-box { background: white; border-radius: 14px; padding: 28px 30px; margin-bottom: 20px; border: 1px solid #dde8f5; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
.section-title { font-size: 1.05rem; font-weight: 700; color: #0d1b2a; border-left: 4px solid #1e6fbf; padding-left: 12px; margin: 0 0 16px; }
.concept-card { background: linear-gradient(135deg, #f0f7ff, #e8f4ff); border: 1px solid #c0d8f5; border-radius: 12px; padding: 18px 20px; margin-bottom: 12px; }
.concept-card .tag { display: inline-block; background: #1e6fbf; color: white !important; border-radius: 6px; padding: 2px 10px; font-size: 0.75rem; font-weight: 700; margin-bottom: 8px; }
.concept-card h4 { color: #0d1b2a; font-size: 0.97rem; font-weight: 700; margin: 0 0 6px; }
.concept-card p { color: #3a5068; font-size: 0.87rem; margin: 0; line-height: 1.6; }
.code-block { background: #0d1b2a; border-radius: 10px; padding: 18px 20px; font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; line-height: 1.7; color: #c8dff0; overflow-x: auto; border: 1px solid #1e3a5f; margin: 12px 0; white-space: pre; }
.code-kw { color: #7ec8f5; } .code-fn { color: #ffd580; } .code-str { color: #98c379; } .code-cmt { color: #5c7a9a; font-style: italic; } .code-num { color: #d19a66; }
.flow-step { background: white; border-radius: 10px; border: 1.5px solid #c0d8f5; padding: 14px 18px; margin-bottom: 8px; display: flex; align-items: center; gap: 14px; }
.flow-num { background: #1e6fbf; color: white !important; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.85rem; flex-shrink: 0; }
.flow-text { color: #0d1b2a; font-size: 0.88rem; font-weight: 500; }
.flow-arrow { text-align: center; color: #7aa8d4; font-size: 1.2rem; margin: 2px 0; }
.insight-box { background: #e8f4ff; border-left: 4px solid #1e6fbf; border-radius: 0 10px 10px 0; padding: 14px 18px; margin: 12px 0; font-size: 0.9rem; color: #1a3a5c; line-height: 1.7; }
.warn-box { background: #fff8e8; border-left: 4px solid #f0a500; border-radius: 0 10px 10px 0; padding: 14px 18px; margin: 12px 0; font-size: 0.9rem; color: #5c3e00; line-height: 1.7; }
.crs-table { width: 100%; border-collapse: collapse; font-size: 0.87rem; }
.crs-table th { background: #1e3a5f; color: white; padding: 10px 14px; text-align: left; font-weight: 600; }
.crs-table td { padding: 9px 14px; border-bottom: 1px solid #dde8f5; color: #2a3a4a; vertical-align: top; }
.crs-table tr:nth-child(even) td { background: #f5f9ff; }
.rank-item { background: white; border-radius: 10px; padding: 14px 18px; margin-bottom: 8px; border: 1px solid #dde8f5; display: flex; justify-content: space-between; align-items: center; gap: 14px; }
.rank-num { font-size: 1.4rem; font-weight: 900; color: #c0ccd8; width: 34px; }
.rank-num.top { color: #c0392b; }
.rank-info { flex: 1; }
.rank-info h5 { margin: 0 0 3px; font-size: 0.95rem; color: #0d1b2a; }
.rank-info p { margin: 0; font-size: 0.8rem; color: #5a7a9a; }
.rank-score { font-size: 0.85rem; color: #1e6fbf; font-weight: 700; text-align: right; min-width: 80px; }
</style>
""", unsafe_allow_html=True)

# ── 데이터 경로 ────────────────────────────────
DATA_DIR = "data"

@st.cache_data
def load_data():
    try:
        pop  = pd.read_csv(os.path.join(DATA_DIR,"pop_by_admin.csv"),         encoding="utf-8-sig")
        bus  = pd.read_csv(os.path.join(DATA_DIR,"bus_stop_cnt_by_admin.csv"),encoding="utf-8-sig")
        sub  = pd.read_csv(os.path.join(DATA_DIR,"subway_cnt_by_admin.csv"),  encoding="utf-8-sig")
        area = pd.read_csv(os.path.join(DATA_DIR,"area_by_admin.csv"),         encoding="utf-8-sig")
        return pop, bus, sub, area
    except FileNotFoundError:
        return None, None, None, None

@st.cache_data
def load_raw():
    try:
        for enc in ["utf-8","cp949","euc-kr"]:
            try:
                bus_raw = pd.read_csv(os.path.join(DATA_DIR,"서울시버스정류소위치정보_20260108_.csv"), encoding=enc)
                break
            except: pass
        for enc in ["cp949","euc-kr","utf-8"]:
            try:
                sub_raw = pd.read_csv(os.path.join(DATA_DIR,"서울교통공사_1_8호선_역사_좌표_위경도__정보_20250814.csv"), encoding=enc)
                break
            except: pass
        return bus_raw, sub_raw
    except:
        return None, None

@st.cache_data
def load_shp():
    try:
        gdf = gpd.read_file(os.path.join(DATA_DIR,"BND_ADM_DONG_PG.shp"))
        gdf = gdf[["ADM_CD","ADM_NM","geometry"]].copy()
        gdf.rename(columns={"ADM_CD":"region_id","ADM_NM":"region_nm"}, inplace=True)
        gdf["region_id"] = gdf["region_id"].astype(str)
        gdf = gdf[gdf["region_id"].str.startswith("11")].copy()
        return gdf
    except:
        return None

@st.cache_data
def build_merged():
    pop, bus, sub, area = load_data()
    if pop is None:
        return None
    pop["region_id"] = pd.to_numeric(pop["region_id"], errors="coerce").astype("Int64").astype(str).str.strip()
    bus["region_id"] = bus["region_id"].astype(str).str.strip()
    sub["region_id"] = sub["region_id"].astype(str).str.strip()
    df = (pop[["region_id","region_nm","population","area_km2","pop_density"]]
          .merge(bus[["region_id","bus_stop_cnt"]], on="region_id", how="left")
          .merge(sub[["region_id","subway_cnt"]],   on="region_id", how="left"))
    df["bus_stop_cnt"] = df["bus_stop_cnt"].fillna(0)
    df["subway_cnt"]   = df["subway_cnt"].fillna(0)
    df["bus_per_10k"]    = (df["bus_stop_cnt"] / (df["population"] / 10000)).replace([np.inf,-np.inf],np.nan).fillna(0)
    df["subway_per_10k"] = (df["subway_cnt"]   / (df["population"] / 10000)).replace([np.inf,-np.inf],np.nan).fillna(0)
    def _mm(s):
        s = s.astype(float)
        return (s-s.min())/(s.max()-s.min()) if s.max()!=s.min() else pd.Series(np.zeros(len(s)),index=s.index)
    df["pop_norm"]         = _mm(df["pop_density"])
    df["bus_inv_norm"]     = 1 - _mm(df["bus_stop_cnt"] + df["subway_cnt"])
    df["vulnerability_score"] = df["pop_norm"]*0.5 + df["bus_inv_norm"]*0.5
    return df

# ── 사이드바 ───────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 0 10px">
        <div style="font-size:1.3rem;font-weight:900;color:#7ec8f5;letter-spacing:-0.5px">🗺️ 공간데이터 분석</div>
        <div style="font-size:0.78rem;color:#4a7a9a;margin-top:4px">Python · GeoPandas · Folium</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    page = st.radio("📚 강의 목차", [
        "🏠  강의 소개",
        "📦  1강 | 라이브러리 & 환경 설정",
        "🗂️  2강 | Shapefile 전처리 & 면적",
        "👥  3강 | 인구 데이터 전처리",
        "🚌  4강 | 버스·지하철 공간 집계",
        "🔗  5강 | 데이터 병합 & 파생지표",
        "📊  6강 | EDA — 교통 취약지역 탐색",
        "🗺️  7강 | Folium 인터랙티브 지도",
    ])
    st.divider()
    pop, bus, sub, area = load_data()
    if pop is not None:
        st.success(f"✅ 행정동 {len(pop):,}개 로드됨")
    else:
        st.error("⚠️ data/ 폴더에 CSV 배치 필요")
    st.caption("출처: 서울열린데이터광장\n서울교통공사 · 브이월드")


# ══════════════════════════════════════════════
# 🏠 강의 소개
# ══════════════════════════════════════════════
if page == "🏠  강의 소개":
    st.markdown("""
    <div class="lecture-header">
        <div class="lecture-badge">공간 데이터 분석 강의</div>
        <h1>닿지 않는 공간을 처음으로 인식하다</h1>
        <p>Python과 GeoPandas를 활용한 서울시 버스·지하철 접근성 분석</p>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    for col,(icon,val,lbl) in zip([c1,c2,c3,c4],[
        ("🗺️","7강","강의 구성"),("📁","6종","사용 데이터"),
        ("🐍","GeoPandas","핵심 라이브러리"),("🔍","427개","분석 행정동"),
    ]):
        col.markdown(f"""
        <div style="background:white;border-radius:12px;padding:20px 16px;text-align:center;
            border:1px solid #dde8f5;box-shadow:0 2px 8px rgba(0,0,0,0.05)">
            <div style="font-size:1.6rem;margin-bottom:6px">{icon}</div>
            <div style="font-size:1.3rem;font-weight:900;color:#1e3a5f">{val}</div>
            <div style="font-size:0.8rem;color:#5a7a9a;margin-top:3px">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔄 전체 분석 흐름</div>', unsafe_allow_html=True)
        steps = [
            ("원시 데이터 불러오기","CSV · Shapefile · Excel"),
            ("좌표 기반 포인트 생성","gpd.points_from_xy()"),
            ("행정동 경계와 공간조인","sjoin(predicate='within')"),
            ("행정동별 시설 수 집계","groupby().size()"),
            ("파생지표 생성","bus_per_10k, pop_density"),
            ("단계구분도 시각화","choropleth map"),
        ]
        for i,(t,s) in enumerate(steps,1):
            st.markdown(f"""
            <div class="flow-step">
                <div class="flow-num">{i}</div>
                <div>
                    <div class="flow-text">{t}</div>
                    <div style="font-size:0.78rem;color:#7a9ab8;font-family:'JetBrains Mono',monospace">{s}</div>
                </div>
            </div>""", unsafe_allow_html=True)
            if i < len(steps):
                st.markdown('<div class="flow-arrow">↓</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📁 사용 데이터</div>', unsafe_allow_html=True)
        for icon,title,fname,source in [
            ("🏙️","행정동 경계 (Shapefile)","BND_ADM_DONG_PG.shp","VWorld 국가공간정보포털"),
            ("👥","등록인구 데이터","등록인구_20260126.csv","서울 열린데이터광장"),
            ("🚌","버스정류소 위치정보","서울시버스정류소위치정보.xlsx","서울 열린데이터광장"),
            ("🚇","지하철역 위경도 정보","서울교통공사_1_8호선.csv","공공데이터포털"),
        ]:
            st.markdown(f"""
            <div style="background:#f5f9ff;border-radius:10px;padding:14px 16px;margin-bottom:10px;border:1px solid #dde8f5">
                <div style="font-size:0.92rem;font-weight:700;color:#0d1b2a;margin-bottom:3px">{icon} {title}</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.77rem;color:#1e6fbf;margin-bottom:3px">{fname}</div>
                <div style="font-size:0.78rem;color:#5a7a9a">출처: {source}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# 1강
# ══════════════════════════════════════════════
elif page == "📦  1강 | 라이브러리 & 환경 설정":
    st.markdown("""
    <div class="lecture-header">
        <div class="lecture-badge">1강</div>
        <h1>라이브러리 소개 & 환경 설정</h1>
        <p>Pandas vs GeoPandas — 공간 데이터를 다루는 도구 이해하기</p>
    </div>
    """, unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="concept-card">
            <div class="tag">PANDAS</div>
            <h4>📊 표 형태 데이터 처리</h4>
            <p>결측치 처리, 정렬, 그룹 집계, 병합 등 기본 EDA에 최적화.
            CSV·엑셀·DB 등 다양한 포맷 지원. 수치·범주형 분석의 표준.</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="concept-card" style="background:linear-gradient(135deg,#f0fff5,#e5f8ec);border-color:#b0dfc0">
            <div class="tag" style="background:#1e7f4f">GEOPANDAS</div>
            <h4>🗺️ 공간 정보를 결합한 확장판</h4>
            <p>Pandas에 geometry를 더한 공간 데이터 전용 라이브러리.
            shp·geojson 읽기, 좌표계 변환·공간조인·버퍼·면적 계산 제공.</p>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔧 환경 설정 코드</div>', unsafe_allow_html=True)
    st.markdown("""<div class="code-block"><span class="code-kw">import</span> os, warnings
warnings.filterwarnings(<span class="code-str">"ignore"</span>)

<span class="code-kw">import</span> pandas <span class="code-kw">as</span> pd
<span class="code-kw">import</span> numpy <span class="code-kw">as</span> np
<span class="code-kw">import</span> geopandas <span class="code-kw">as</span> gpd
<span class="code-kw">import</span> matplotlib.pyplot <span class="code-kw">as</span> plt
<span class="code-kw">import</span> matplotlib <span class="code-kw">as</span> mpl

<span class="code-cmt"># 한글 폰트</span>
<span class="code-kw">try</span>:
    mpl.rcParams[<span class="code-str">"font.family"</span>] = <span class="code-str">"Malgun Gothic"</span>
<span class="code-kw">except</span>:
    mpl.rcParams[<span class="code-str">"font.family"</span>] = <span class="code-str">"AppleGothic"</span>
mpl.rcParams[<span class="code-str">"axes.unicode_minus"</span>] = <span class="code-kw">False</span>

<span class="code-cmt"># 폴더 구조</span>
BASE_DIR = os.getcwd()
DATA_DIR = os.path.join(BASE_DIR, <span class="code-str">"data"</span>)
OUT_DIR  = os.path.join(BASE_DIR, <span class="code-str">"outputs"</span>)
os.makedirs(DATA_DIR, exist_ok=<span class="code-kw">True</span>)
os.makedirs(OUT_DIR,  exist_ok=<span class="code-kw">True</span>)</div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🛠️ 유틸 함수</div>', unsafe_allow_html=True)
    st.markdown("""<div class="code-block"><span class="code-kw">def</span> <span class="code-fn">read_csv_safely</span>(path):
    <span class="code-cmt"># UTF-8 → CP949 자동 감지</span>
    <span class="code-kw">try</span>:   <span class="code-kw">return</span> pd.read_csv(path, encoding=<span class="code-str">"utf-8"</span>)
    <span class="code-kw">except</span>: <span class="code-kw">return</span> pd.read_csv(path, encoding=<span class="code-str">"cp949"</span>)

<span class="code-kw">def</span> <span class="code-fn">to_num</span>(s):
    <span class="code-cmt"># 문자/혼합 값 → 숫자형 (변환 불가 → NaN)</span>
    <span class="code-kw">return</span> pd.to_numeric(s, errors=<span class="code-str">"coerce"</span>)

<span class="code-kw">def</span> <span class="code-fn">norm_nm</span>(x):
    <span class="code-cmt"># 행정동 이름 표준화 (공백·특수문자·점 통일)</span>
    <span class="code-kw">if</span> pd.isna(x): <span class="code-kw">return None</span>
    s = str(x).strip().replace(<span class="code-str">"\u00A0"</span>, <span class="code-str">" "</span>)
    s = <span class="code-str">" "</span>.join(s.split()).replace(<span class="code-str">"."</span>, <span class="code-str">"·"</span>)
    <span class="code-kw">return</span> s

<span class="code-kw">def</span> <span class="code-fn">ensure_crs</span>(gdf, epsg):
    <span class="code-cmt"># CRS 확인 후 지정 EPSG로 변환</span>
    <span class="code-kw">if</span> gdf.crs <span class="code-kw">is None</span>: <span class="code-kw">raise</span> ValueError(<span class="code-str">"CRS 없음"</span>)
    <span class="code-kw">return</span> gdf.to_crs(epsg=epsg)</div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# 2강
# ══════════════════════════════════════════════
elif page == "🗂️  2강 | Shapefile 전처리 & 면적":
    st.markdown("""
    <div class="lecture-header">
        <div class="lecture-badge">2강</div>
        <h1>Shapefile 전처리 & 면적 계산</h1>
        <p>행정동 경계 벡터 데이터 로딩 · CRS 변환 · 면적 계산</p>
    </div>
    """, unsafe_allow_html=True)

    c1,c2 = st.columns([3,2])
    with c1:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📄 Shapefile 로딩 & 전처리</div>', unsafe_allow_html=True)
        st.markdown("""<div class="code-block"><span class="code-cmt"># Shapefile 읽기</span>
gdf_admin = gpd.read_file(<span class="code-str">"data/BND_ADM_DONG_PG.shp"</span>)

<span class="code-cmt"># 필요 컬럼 선택 & 이름 변경</span>
gdf_admin = gdf_admin[[<span class="code-str">"ADM_CD"</span>,<span class="code-str">"ADM_NM"</span>,<span class="code-str">"geometry"</span>]].copy()
gdf_admin.rename(columns={<span class="code-str">"ADM_CD"</span>:<span class="code-str">"region_id"</span>,<span class="code-str">"ADM_NM"</span>:<span class="code-str">"region_nm"</span>}, inplace=<span class="code-kw">True</span>)

<span class="code-cmt"># 서울(코드 11로 시작)만 필터링</span>
gdf_admin[<span class="code-str">"region_id"</span>] = gdf_admin[<span class="code-str">"region_id"</span>].astype(str)
gdf_admin = gdf_admin[gdf_admin[<span class="code-str">"region_id"</span>].str.startswith(<span class="code-str">"11"</span>)].copy()

<span class="code-cmt"># 행정동 이름 표준화</span>
gdf_admin[<span class="code-str">"region_nm"</span>] = gdf_admin[<span class="code-str">"region_nm"</span>].map(norm_nm)

<span class="code-cmt"># CRS 변환: EPSG:5179 (미터 단위 — 면적 계산용)</span>
gdf_admin = ensure_crs(gdf_admin, <span class="code-num">5179</span>)

<span class="code-cmt"># 면적 계산 (m² → km²)</span>
area_df = gdf_admin[[<span class="code-str">"region_id"</span>,<span class="code-str">"region_nm"</span>]].copy()
area_df[<span class="code-str">"area_km2"</span>] = gdf_admin.geometry.area / <span class="code-num">1e6</span></div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🌐 좌표계(CRS) 비교</div>', unsafe_allow_html=True)
        st.markdown("""
        <table class="crs-table">
            <tr><th>구분</th><th>EPSG:4326</th><th>EPSG:5179</th></tr>
            <tr><td><b>명칭</b></td><td>WGS84</td><td>Korea 2000</td></tr>
            <tr><td><b>단위</b></td><td>도(°)</td><td>미터(m)</td></tr>
            <tr><td><b>용도</b></td><td>GPS·표시</td><td>분석·계산</td></tr>
            <tr><td><b>면적</b></td><td>❌ 부정확</td><td>✅ 정확</td></tr>
            <tr><td><b>한국 특화</b></td><td>-</td><td>✅ 표준</td></tr>
        </table>
        <div class="insight-box" style="margin-top:14px">
        💡 <b>실무 권장 원칙</b><br>
        · 불러오기: EPSG:4326 그대로<br>
        · 분석 전: EPSG:5179로 통일<br>
        · 면적·거리·버퍼는 투영 좌표계에서!
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    _, _, _, area_loaded = load_data()
    if area_loaded is not None:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 행정동 면적 분포 (실제 데이터)</div>', unsafe_allow_html=True)
        area_loaded["area_km2"] = area_loaded["area_km2"].astype(float)
        fig = px.histogram(area_loaded, x="area_km2", nbins=40,
                           color_discrete_sequence=["#1e6fbf"],
                           labels={"area_km2":"면적 (km²)","count":"행정동 수"},
                           title="서울시 행정동 면적 분포")
        fig.update_layout(height=280, margin=dict(t=40,b=20,l=20,r=20),
                          plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
        c1,c2,c3 = st.columns(3)
        c1.metric("전체 행정동 수", f"{len(area_loaded):,}개")
        c2.metric("평균 면적", f"{area_loaded['area_km2'].mean():.2f} km²")
        c3.metric("최대 면적", f"{area_loaded['area_km2'].max():.2f} km²")
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# 3강
# ══════════════════════════════════════════════
elif page == "👥  3강 | 인구 데이터 전처리":
    st.markdown("""
    <div class="lecture-header">
        <div class="lecture-badge">3강</div>
        <h1>인구 데이터 전처리</h1>
        <p>다단 헤더 CSV 처리 · 총인구 계산 · 인구밀도 생성</p>
    </div>
    """, unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📄 다단 헤더 CSV 처리 코드</div>', unsafe_allow_html=True)
        st.markdown("""<div class="code-block"><span class="code-cmt"># 3단 헤더 파일 읽기</span>
pop_raw = pd.read_csv(POP_CSV, header=[<span class="code-num">0</span>, <span class="code-num">1</span>, <span class="code-num">2</span>])

<span class="code-cmt"># MultiIndex에서 필요 컬럼 추출</span>
cols = pop_raw.columns
dong_col   = [c <span class="code-kw">for</span> c <span class="code-kw">in</span> cols <span class="code-kw">if</span> <span class="code-str">"동별(3)"</span> <span class="code-kw">in</span> str(c)][<span class="code-num">0</span>]
male_col   = [c <span class="code-kw">for</span> c <span class="code-kw">in</span> cols <span class="code-kw">if</span> <span class="code-str">"계"</span> <span class="code-kw">in</span> str(c)
              <span class="code-kw">and</span> <span class="code-str">"남자"</span> <span class="code-kw">in</span> str(c)][<span class="code-num">0</span>]
female_col = [c <span class="code-kw">for</span> c <span class="code-kw">in</span> cols <span class="code-kw">if</span> <span class="code-str">"계"</span> <span class="code-kw">in</span> str(c)
              <span class="code-kw">and</span> <span class="code-str">"여자"</span> <span class="code-kw">in</span> str(c)][<span class="code-num">0</span>]

<span class="code-cmt"># 컬럼 선택 & 이름 변경</span>
pop_df = pop_raw[[dong_col, male_col, female_col]].copy()
pop_df.columns = [<span class="code-str">"region_nm"</span>, <span class="code-str">"male"</span>, <span class="code-str">"female"</span>]

<span class="code-cmt"># 합계/소계 제거 & 표준화</span>
pop_df = pop_df[~pop_df[<span class="code-str">"region_nm"</span>].isin([<span class="code-str">"합계"</span>,<span class="code-str">"소계"</span>])].copy()
pop_df[<span class="code-str">"region_nm"</span>] = pop_df[<span class="code-str">"region_nm"</span>].map(norm_nm)

<span class="code-cmt"># 숫자 변환 & 총인구 계산</span>
pop_df[<span class="code-str">"male"</span>]       = to_num(pop_df[<span class="code-str">"male"</span>])
pop_df[<span class="code-str">"female"</span>]     = to_num(pop_df[<span class="code-str">"female"</span>])
pop_df[<span class="code-str">"population"</span>] = pop_df[<span class="code-str">"male"</span>] + pop_df[<span class="code-str">"female"</span>]

<span class="code-cmt"># 인구밀도 (1km²당 인구)</span>
pop_df[<span class="code-str">"pop_density"</span>] = pop_df[<span class="code-str">"population"</span>] / pop_df[<span class="code-str">"area_km2"</span>]</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        pop_loaded, _, _, _ = load_data()
        if pop_loaded is not None:
            st.markdown('<div class="section-box">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📊 인구밀도 분포 (실제 데이터)</div>', unsafe_allow_html=True)
            df_c = pop_loaded.copy()
            df_c["pop_density"] = pd.to_numeric(df_c["pop_density"], errors="coerce")
            fig = px.histogram(df_c.dropna(subset=["pop_density"]), x="pop_density", nbins=40,
                               color_discrete_sequence=["#e07b00"],
                               labels={"pop_density":"인구밀도 (명/km²)","count":"행정동 수"},
                               title="서울시 행정동 인구밀도 분포")
            fig.update_layout(height=240, margin=dict(t=40,b=20,l=20,r=20),
                              plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
            disp = df_c[["region_nm","population","area_km2","pop_density"]].dropna().head(8).copy()
            disp.columns = ["행정동","총인구","면적(km²)","인구밀도"]
            disp["총인구"] = disp["총인구"].astype(int)
            disp["인구밀도"] = disp["인구밀도"].round(0).astype(int)
            st.dataframe(disp, use_container_width=True, height=220)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""<div class="insight-box">
    💡 <b>핵심 포인트</b> — 행정동 이름으로 데이터를 결합할 때 반드시 <code>norm_nm()</code>으로
    공백·특수문자·표기 방식을 통일해야 합니다. "종로1.2.3.4가동" ↔ "종로1·2·3·4가동" 같은
    불일치가 병합 오류의 주요 원인입니다.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# 4강
# ══════════════════════════════════════════════
elif page == "🚌  4강 | 버스·지하철 공간 집계":
    st.markdown("""
    <div class="lecture-header">
        <div class="lecture-badge">4강</div>
        <h1>버스 & 지하철 공간 집계</h1>
        <p>좌표 → GeoDataFrame → 공간조인(sjoin) → 행정동별 시설 수 집계</p>
    </div>
    """, unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🚌 버스정류장 공간 집계</div>', unsafe_allow_html=True)
        st.markdown("""<div class="code-block"><span class="code-cmt"># 엑셀 읽기 & 숫자 변환</span>
bus_raw = pd.read_excel(<span class="code-str">"서울시버스정류소위치정보.xlsx"</span>)
bus_raw[<span class="code-str">"X좌표"</span>] = to_num(bus_raw[<span class="code-str">"X좌표"</span>])
bus_raw[<span class="code-str">"Y좌표"</span>] = to_num(bus_raw[<span class="code-str">"Y좌표"</span>])

<span class="code-cmt"># ① 좌표 → GeoDataFrame</span>
gdf_bus = gpd.GeoDataFrame(
    bus_raw,
    geometry=gpd.points_from_xy(
        bus_raw[<span class="code-str">"X좌표"</span>], bus_raw[<span class="code-str">"Y좌표"</span>]
    ),
    crs=<span class="code-str">"EPSG:4326"</span>
)
<span class="code-cmt"># ② 분석 좌표계로 변환</span>
gdf_bus = gdf_bus.to_crs(epsg=<span class="code-num">5179</span>)

<span class="code-cmt"># ③ 공간조인 & 집계</span>
bus_cnt = (
    gpd.sjoin(gdf_bus, gdf_admin,
              how=<span class="code-str">"left"</span>, predicate=<span class="code-str">"within"</span>)
    .groupby([<span class="code-str">"region_id"</span>,<span class="code-str">"region_nm"</span>])
    .size()
    .reset_index(name=<span class="code-str">"bus_stop_cnt"</span>)
)</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🚇 지하철역 공간 집계</div>', unsafe_allow_html=True)
        st.markdown("""<div class="code-block"><span class="code-cmt"># CSV 읽기 (CP949)</span>
sub_raw = read_csv_safely(SUBWAY_CSV)
sub_raw[<span class="code-str">"경도"</span>] = to_num(sub_raw[<span class="code-str">"경도"</span>])
sub_raw[<span class="code-str">"위도"</span>] = to_num(sub_raw[<span class="code-str">"위도"</span>])

<span class="code-cmt"># ① GeoDataFrame 변환</span>
gdf_sub = gpd.GeoDataFrame(
    sub_raw,
    geometry=gpd.points_from_xy(
        sub_raw[<span class="code-str">"경도"</span>], sub_raw[<span class="code-str">"위도"</span>]
    ),
    crs=<span class="code-str">"EPSG:4326"</span>
)
<span class="code-cmt"># ② 좌표계 변환</span>
gdf_sub = gdf_sub.to_crs(epsg=<span class="code-num">5179</span>)

<span class="code-cmt"># ③ 공간조인 & 집계</span>
sub_cnt = (
    gpd.sjoin(gdf_sub, gdf_admin,
              how=<span class="code-str">"left"</span>, predicate=<span class="code-str">"within"</span>)
    .groupby([<span class="code-str">"region_id"</span>,<span class="code-str">"region_nm"</span>])
    .size()
    .reset_index(name=<span class="code-str">"subway_cnt"</span>)
)</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    _, bus_loaded, sub_loaded, _ = load_data()
    if bus_loaded is not None:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 집계 결과 (실제 데이터)</div>', unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("버스 집계 행정동", f"{len(bus_loaded):,}개")
        c2.metric("버스 정류장 총계", f"{int(bus_loaded['bus_stop_cnt'].sum()):,}개")
        c3.metric("지하철 집계 행정동", f"{len(sub_loaded):,}개")
        c4.metric("지하철역 총계", f"{int(sub_loaded['subway_cnt'].sum()):,}개")
        ca,cb = st.columns(2)
        with ca:
            fig = px.histogram(bus_loaded, x="bus_stop_cnt", nbins=30,
                               color_discrete_sequence=["#1e6fbf"],
                               title="행정동별 버스 정류장 수 분포",
                               labels={"bus_stop_cnt":"정류장 수","count":"행정동 수"})
            fig.update_layout(height=260, margin=dict(t=40,b=20,l=20,r=20),
                              plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
        with cb:
            fig2 = px.histogram(sub_loaded, x="subway_cnt", nbins=15,
                                color_discrete_sequence=["#e07b00"],
                                title="행정동별 지하철역 수 분포",
                                labels={"subway_cnt":"역 수","count":"행정동 수"})
            fig2.update_layout(height=260, margin=dict(t=40,b=20,l=20,r=20),
                               plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""<div class="concept-card" style="background:linear-gradient(135deg,#fff5e8,#fff0d8);border-color:#f0c880">
        <div class="tag" style="background:#c06000">sjoin predicate</div>
        <h4>공간조인 술어(predicate) 이해</h4>
        <p><b>within</b> — 포인트가 폴리곤 안에 완전히 포함될 때 매칭 (정류장→행정동)<br>
        <b>intersects</b> — 두 geometry가 조금이라도 겹치면 매칭<br>
        <b>contains</b> — 폴리곤이 포인트를 포함할 때 (within의 반대 방향)</p>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# 5강
# ══════════════════════════════════════════════
elif page == "🔗  5강 | 데이터 병합 & 파생지표":
    st.markdown("""
    <div class="lecture-header">
        <div class="lecture-badge">5강</div>
        <h1>데이터 병합 & 파생지표 생성</h1>
        <p>인구 + 버스 + 지하철 + 면적 통합 → 표준화 접근성 지표 계산</p>
    </div>
    """, unsafe_allow_html=True)

    c1,c2 = st.columns([3,2])
    with c1:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔗 데이터 병합 & 파생지표 생성</div>', unsafe_allow_html=True)
        st.markdown("""<div class="code-block"><span class="code-cmt"># 순차 병합 (인구 기준 좌조인)</span>
df = (
    pop_df[[<span class="code-str">"region_id"</span>,<span class="code-str">"population"</span>,<span class="code-str">"pop_density"</span>]]
    .merge(bus_df[[<span class="code-str">"region_id"</span>,<span class="code-str">"bus_stop_cnt"</span>]],
           on=<span class="code-str">"region_id"</span>, how=<span class="code-str">"left"</span>)
    .merge(subway_df[[<span class="code-str">"region_id"</span>,<span class="code-str">"subway_cnt"</span>]],
           on=<span class="code-str">"region_id"</span>, how=<span class="code-str">"left"</span>)
)
<span class="code-cmt"># NaN → 0</span>
df[<span class="code-str">"bus_stop_cnt"</span>] = df[<span class="code-str">"bus_stop_cnt"</span>].fillna(<span class="code-num">0</span>)
df[<span class="code-str">"subway_cnt"</span>]   = df[<span class="code-str">"subway_cnt"</span>].fillna(<span class="code-num">0</span>)

<span class="code-cmt"># 파생지표: 인구 1만명당 시설 수</span>
df[<span class="code-str">"bus_per_10k"</span>]    = df[<span class="code-str">"bus_stop_cnt"</span>] / (df[<span class="code-str">"population"</span>] / <span class="code-num">10000</span>)
df[<span class="code-str">"subway_per_10k"</span>] = df[<span class="code-str">"subway_cnt"</span>]   / (df[<span class="code-str">"population"</span>] / <span class="code-num">10000</span>)

<span class="code-cmt"># 접근성 등급 (5분위)</span>
df[<span class="code-str">"bus_class"</span>] = pd.qcut(
    df[<span class="code-str">"bus_per_10k"</span>], q=<span class="code-num">5</span>,
    labels=[<span class="code-str">"매우 낮음"</span>,<span class="code-str">"낮음"</span>,<span class="code-str">"보통"</span>,<span class="code-str">"높음"</span>,<span class="code-str">"매우 높음"</span>]
)</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📐 파생지표 설명</div>', unsafe_allow_html=True)
        for icon,title,formula,desc in [
            ("🚌","bus_per_10k","bus_stop_cnt ÷ (population / 10,000)","인구 규모를 보정한 버스 접근성. 값이 클수록 접근성 양호"),
            ("🚇","subway_per_10k","subway_cnt ÷ (population / 10,000)","인구 대비 지하철역 수. 0이면 역이 없는 지역"),
            ("📏","pop_density","population ÷ area_km²","1km²당 인구. 교통 수요 크기를 나타내는 기초 지표"),
        ]:
            st.markdown(f"""
            <div style="background:#f5f9ff;border-radius:10px;padding:14px 16px;margin-bottom:10px;border:1px solid #dde8f5">
                <div style="font-size:0.9rem;font-weight:700;color:#0d1b2a;margin-bottom:3px">{icon} {title}</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.77rem;color:#1e6fbf;margin-bottom:4px">{formula}</div>
                <div style="font-size:0.82rem;color:#3a5a7a">{desc}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    df_m = build_merged()
    if df_m is not None:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 병합 결과 테이블 (상위 10개)</div>', unsafe_allow_html=True)
        disp = df_m[["region_nm","population","pop_density","bus_stop_cnt","subway_cnt","bus_per_10k","subway_per_10k"]].head(10).copy()
        disp.columns = ["행정동","총인구","인구밀도","버스 정류장","지하철역","버스/만명","지하철/만명"]
        disp["총인구"] = disp["총인구"].astype(int)
        disp["인구밀도"] = disp["인구밀도"].round(0).astype(int)
        disp["버스/만명"] = disp["버스/만명"].round(2)
        disp["지하철/만명"] = disp["지하철/만명"].round(3)
        st.dataframe(disp, use_container_width=True, height=300)
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# 6강 EDA
# ══════════════════════════════════════════════
elif page == "📊  6강 | EDA — 교통 취약지역 탐색":
    st.markdown("""
    <div class="lecture-header">
        <div class="lecture-badge">6강</div>
        <h1>EDA — 교통 취약지역 탐색</h1>
        <p>"버스 접근성이 낮은 동은 지하철도 좋지 않은가?" · "고밀 저버스 지역은 어디?"</p>
    </div>
    """, unsafe_allow_html=True)

    df = build_merged()
    if df is None:
        st.error("data/ 폴더 CSV를 확인해주세요."); st.stop()

    with st.container():
        st.markdown('<div style="background:white;border-radius:12px;padding:16px 20px;margin-bottom:16px;border:1px solid #dde8f5">', unsafe_allow_html=True)
        f1,f2,f3 = st.columns(3)
        pop_min     = f1.slider("최소 인구", 0, 60000, 5000, 1000)
        bus_max     = f2.slider("버스/만명 상한", 1.0, 50.0, 30.0, 0.5)
        highlight_n = f3.slider("취약지역 강조 수", 5, 20, 10, 1)
        st.markdown('</div>', unsafe_allow_html=True)

    df_f = df[(df["population"] >= pop_min) & (df["bus_per_10k"] <= bus_max)].copy()
    tab1, tab2, tab3 = st.tabs(["📈 교통 접근성 산점도", "🏙️ 고밀·저버스 분석", "🏆 취약지역 순위"])

    with tab1:
        target = df_f.sort_values(["bus_per_10k","subway_per_10k"]).head(highlight_n)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_f["bus_per_10k"], y=df_f["subway_per_10k"],
            mode="markers", name="전체 행정동",
            marker=dict(color="#a0c0e0",size=7,opacity=0.6),
            hovertext=df_f["region_nm"], hoverinfo="text+x+y"))
        fig.add_trace(go.Scatter(x=target["bus_per_10k"], y=target["subway_per_10k"],
            mode="markers+text", name=f"교통 취약 Top{highlight_n}",
            marker=dict(color="#c0392b",size=12),
            text=target["region_nm"], textposition="top right",
            textfont=dict(size=11,color="#c0392b")))
        fig.update_layout(title="교통 접근성 산점도 (버스 vs 지하철)", height=460,
            xaxis_title="버스 정류장 수 (인구 1만명당)",
            yaxis_title="지하철역 수 (인구 1만명당)",
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h",y=1.05), hovermode="closest")
        fig.update_xaxes(showgrid=True,gridcolor="#eee")
        fig.update_yaxes(showgrid=True,gridcolor="#eee")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""<div class="insight-box">💡 좌하단 빨간 점이 <b>버스·지하철 접근성이 동시에 낮은 교통 취약 행정동</b>입니다.
        이 지역은 자가용 의존도가 높아 교통 정책 개선 우선순위가 됩니다.</div>""", unsafe_allow_html=True)

    with tab2:
        hd  = df["pop_density"].quantile(0.8)
        lb  = df["bus_per_10k"].quantile(0.1)
        t2  = df[(df["pop_density"]>=hd)&(df["bus_per_10k"]<=lb)]
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df["pop_density"], y=df["bus_per_10k"],
            mode="markers", name="전체 행정동",
            marker=dict(color="#a0c0e0",size=7,opacity=0.5),
            hovertext=df["region_nm"], hoverinfo="text+x+y"))
        fig2.add_trace(go.Scatter(x=t2["pop_density"], y=t2["bus_per_10k"],
            mode="markers+text", name="고밀·저버스 취약지역",
            marker=dict(color="#e07b00",size=12),
            text=t2["region_nm"], textposition="top right",
            textfont=dict(size=11,color="#e07b00")))
        fig2.add_vline(x=hd, line_dash="dash", line_color="#c0392b",
            annotation_text=f"상위 20% 기준 ({hd:,.0f}명/km²)")
        fig2.update_layout(title="인구밀도 vs 버스 접근성 (고밀·저버스 취약지역)", height=460,
            xaxis_title="인구밀도 (명/km²)", yaxis_title="버스 정류장 수 (인구 1만명당)",
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h",y=1.05))
        fig2.update_xaxes(showgrid=True,gridcolor="#eee")
        fig2.update_yaxes(showgrid=True,gridcolor="#eee")
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown(f"""<div class="insight-box">💡 인구밀도 상위 20%(기준 {hd:,.0f}명/km²)이면서
        버스 접근성 하위 10%인 지역이 <b>"고밀·저버스 취약지역"</b>입니다. 수요 대비 공급이 가장 부족한 최우선 개선 대상입니다.
        </div>""", unsafe_allow_html=True)

    with tab3:
        ranking = df.sort_values("vulnerability_score", ascending=False).head(20)
        for i,(_,row) in enumerate(ranking.iterrows(),1):
            is_top = i <= 5
            st.markdown(f"""
            <div class="rank-item" style="{'border-color:#ffd0c0;' if is_top else ''}">
                <div class="rank-num {'top' if is_top else ''}">{i}</div>
                <div class="rank-info">
                    <h5>{row['region_nm']} {'🔴' if is_top else ''}</h5>
                    <p>인구: {int(row['population']):,}명 &nbsp;|&nbsp; 버스: {row['bus_stop_cnt']:.0f}개 &nbsp;|&nbsp;
                       지하철: {row['subway_cnt']:.0f}개 &nbsp;|&nbsp; 인구밀도: {row['pop_density']:,.0f}명/km²</p>
                </div>
                <div class="rank-score">취약점수<br>{row['vulnerability_score']:.3f}</div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# 7강 Folium
# ══════════════════════════════════════════════
elif page == "🗺️  7강 | Folium 인터랙티브 지도":
    st.markdown("""
    <div class="lecture-header">
        <div class="lecture-badge">7강</div>
        <h1>Folium 인터랙티브 지도</h1>
        <p>단계구분도 · 버스/지하철 마커 · 취약지역 3단계 비교 지도</p>
    </div>
    """, unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        st.markdown("""<div class="concept-card">
            <div class="tag">GEOPANDAS</div>
            <h4>📐 분석 & 정적 지도</h4>
            <p>공간 연산(버퍼·교차·차집합·공간조인) 수행 가능. Matplotlib 기반 정적 지도 → 논문·보고서용.</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="concept-card" style="background:linear-gradient(135deg,#f5fff5,#eafaf0);border-color:#b0dfb8">
            <div class="tag" style="background:#1e7f4f">FOLIUM</div>
            <h4>🌐 인터랙티브 웹 지도</h4>
            <p>확대·축소·이동·레이어 켜고끄기 지원. 공간 연산 없음 → 분석 결과 시각화·공유용.</p>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🗺️ 인터랙티브 지도</div>', unsafe_allow_html=True)

    mc1,mc2,mc3 = st.columns(3)
    map_type   = mc1.selectbox("지도 유형", ["버스 정류장 밀도","지하철 접근성","취약지역 3단계 비교"])
    tile_style = mc2.selectbox("스타일", ["CartoDB positron","OpenStreetMap","CartoDB dark_matter"])
    show_sub   = mc3.checkbox("🚇 지하철역 마커", value=True)
    show_bus   = mc3.checkbox("🚌 버스 정류장 샘플(300개)", value=False)

    df_map      = build_merged()
    _, _, _, _  = load_data()
    bus_raw, sub_raw = load_raw()

    m = folium.Map(location=[37.55,126.98], zoom_start=11, tiles=tile_style)

    if df_map is not None:
        gdf_shp = load_shp()
        if gdf_shp is not None:
            gdf_shp["region_id"] = gdf_shp["region_id"].astype(str).str.strip()
            df_map["region_id"]  = df_map["region_id"].astype(str).str.strip()
            gdf_base = gdf_shp.merge(df_map, on="region_id", how="left").to_crs(4326)

            if map_type == "버스 정류장 밀도":
                gj = gdf_base.dropna(subset=["bus_per_10k"]).to_json()
                folium.Choropleth(geo_data=gj,
                    data=gdf_base.dropna(subset=["bus_per_10k"]),
                    columns=["region_id","bus_per_10k"],
                    key_on="feature.properties.region_id",
                    fill_color="Blues", fill_opacity=0.7, line_opacity=0.3,
                    legend_name="인구 1만명당 버스 정류장 수", nan_fill_color="lightgray",
                ).add_to(m)
                folium.GeoJson(gj,
                    style_function=lambda x:{"fillOpacity":0,"color":"#555","weight":0.4},
                    tooltip=folium.GeoJsonTooltip(
                        fields=["region_nm","bus_stop_cnt","bus_per_10k"],
                        aliases=["행정동","버스 정류장","만명당"])
                ).add_to(m)

            elif map_type == "지하철 접근성":
                gj = gdf_base.dropna(subset=["subway_per_10k"]).to_json()
                folium.Choropleth(geo_data=gj,
                    data=gdf_base.dropna(subset=["subway_per_10k"]),
                    columns=["region_id","subway_per_10k"],
                    key_on="feature.properties.region_id",
                    fill_color="YlOrRd", fill_opacity=0.7, line_opacity=0.3,
                    legend_name="인구 1만명당 지하철역 수", nan_fill_color="lightgray",
                ).add_to(m)
                folium.GeoJson(gj,
                    style_function=lambda x:{"fillOpacity":0,"color":"#555","weight":0.4},
                    tooltip=folium.GeoJsonTooltip(
                        fields=["region_nm","subway_cnt","subway_per_10k"],
                        aliases=["행정동","지하철역 수","만명당"])
                ).add_to(m)

            else:  # 3단계 비교
                t1 = df_map.sort_values(["bus_per_10k","subway_per_10k"]).head(10)
                hd = df_map["pop_density"].quantile(0.8)
                lb = df_map["bus_per_10k"].quantile(0.1)
                t2 = df_map[(df_map["pop_density"]>=hd)&(df_map["bus_per_10k"]<=lb)]
                t3 = df_map.sort_values("vulnerability_score", ascending=False).head(10)
                folium.GeoJson(gdf_base.to_json(), name="전체 행정동",
                    style_function=lambda x:{"fillOpacity":0,"color":"#888","weight":0.5}).add_to(m)
                g1 = gdf_base[gdf_base["region_id"].isin(t1["region_id"].tolist())]
                g2 = gdf_base[gdf_base["region_id"].isin(t2["region_id"].tolist())]
                g3 = gdf_base[gdf_base["region_id"].isin(t3["region_id"].tolist())]
                folium.GeoJson(g1.to_json(), name="Step1: 교통만 (파란색)",
                    style_function=lambda x:{"fillOpacity":0.25,"color":"blue","weight":2,"fillColor":"blue"}).add_to(m)
                folium.GeoJson(g2.to_json(), name="Step2: 교통+인구 (주황)",
                    style_function=lambda x:{"fillOpacity":0.3,"color":"orange","weight":2,"fillColor":"orange"}).add_to(m)
                folium.GeoJson(g3.to_json(), name="Step3: 취약점수 Top10 (빨강)",
                    style_function=lambda x:{"fillOpacity":0.35,"color":"red","weight":3,"fillColor":"red"}).add_to(m)

        if show_sub and sub_raw is not None:
            for _,row in sub_raw.dropna(subset=["위도","경도"]).iterrows():
                folium.CircleMarker(
                    location=[row["위도"],row["경도"]], radius=5,
                    color="#e07b00", fill=True, fill_color="#e07b00",
                    fill_opacity=0.9, weight=1,
                    popup=f"{row['호선']}호선 {row['역명']}역",
                    tooltip=f"{row['역명']}역"
                ).add_to(m)

        if show_bus and bus_raw is not None:
            sample = bus_raw.dropna(subset=["X좌표","Y좌표"]).sample(min(300,len(bus_raw)), random_state=42)
            for _,row in sample.iterrows():
                folium.CircleMarker(
                    location=[row["Y좌표"],row["X좌표"]], radius=3,
                    color="#1e6fbf", fill=True, fill_color="#1e6fbf",
                    fill_opacity=0.6, weight=0.5,
                    tooltip=row.get("정류소명","버스 정류장")
                ).add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    st_folium(m, width=None, height=560)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📄 Folium 핵심 코드</div>', unsafe_allow_html=True)
    st.markdown("""<div class="code-block"><span class="code-kw">import</span> folium
<span class="code-kw">from</span> folium.plugins <span class="code-kw">import</span> MarkerCluster

<span class="code-cmt"># 지도 생성</span>
m = folium.Map(location=[<span class="code-num">37.55</span>, <span class="code-num">126.98</span>], zoom_start=<span class="code-num">11</span>)

<span class="code-cmt"># 단계구분도 (Choropleth)</span>
folium.Choropleth(
    geo_data=gdf_json,
    data=df, columns=[<span class="code-str">"region_id"</span>,<span class="code-str">"bus_per_10k"</span>],
    key_on=<span class="code-str">"feature.properties.region_id"</span>,
    fill_color=<span class="code-str">"Blues"</span>,
    legend_name=<span class="code-str">"인구 1만명당 버스 정류장 수"</span>,
).add_to(m)

<span class="code-cmt"># 취약지역 강조 폴리곤</span>
folium.GeoJson(gdf_top5.to_json(), name=<span class="code-str">"교통 취약 Top5"</span>,
    style_function=<span class="code-kw">lambda</span> x: {
        <span class="code-str">"fillOpacity"</span>:<span class="code-num">0.3</span>, <span class="code-str">"color"</span>:<span class="code-str">"red"</span>, <span class="code-str">"weight"</span>:<span class="code-num">2</span>
    }
).add_to(m)

<span class="code-cmt"># 레이어 컨트롤 & 저장</span>
folium.LayerControl(collapsed=<span class="code-kw">False</span>).add_to(m)
m.save(<span class="code-str">"seoul_accessibility.html"</span>)</div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""<div class="warn-box">
    ⚠️ <b>[과업의 한계] 공간적 다중공선성 (Spatial Multicollinearity)</b><br><br>
    정류장 수가 많은 지역은 커버리지도 넓고, 적은 지역은 좁습니다.
    두 지표가 <b>동일한 공간 구조를 반복</b>하면 지표를 추가해도 설명력이 증가하지 않습니다.<br><br>
    또한 직선거리 기반 접근성은 <b>실제 도로 구조·단절 구간·우회 경로를 반영하지 못합니다.</b><br>
    → 다음 단계: 실제 보행 경로(네트워크 분석)를 고려한 접근성 평가로 확장합니다.
    </div>""", unsafe_allow_html=True)
