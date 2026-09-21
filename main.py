import pandas as pd
import plotly.express as px
import streamlit as st

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
)

st.set_page_config(page_title="영화 데이터 그래프 도감 1 - 시간", layout="wide")


# ─────────────────────────────────────────────
# 데이터 불러오기
# ─────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_URL)
    # 20240101 같은 여덟 자리 숫자 → 진짜 날짜(datetime)
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")
    return df


def show_insight(text: str) -> None:
    """그래프 바로 아래에 '이 그래프로 알 수 있는 것' 한 문장을 보여 줍니다."""
    st.info(f"**이 그래프로 알 수 있는 것** · {text}")


df = load_data()

st.title("영화 데이터 그래프 도감 1 - 시간")
st.caption("일별 박스오피스 10위권 기록 (1년치)")


# ─────────────────────────────────────────────
# 구역 1: 영화별 일관객 변화
# ─────────────────────────────────────────────
def section_daily_audience() -> None:
    st.header("1. 영화별 일관객 변화")

    # 누적관객이 큰 영화가 위로 오도록 정렬
    movie_order = (
        df.groupby("영화명")["누적관객"].max().sort_values(ascending=False).index.tolist()
    )
    movie = st.selectbox("영화를 골라 보세요", movie_order, key="sec1_movie")

    movie_df = df[df["영화명"] == movie].sort_values("날짜")

    fig = px.line(
        movie_df,
        x="날짜",
        y="일관객",
        markers=True,
        title=f"{movie} · 날짜별 일관객",
    )
    fig.update_traces(
        hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>"
    )
    fig.update_layout(xaxis_title="날짜", yaxis_title="일관객(명)")
    st.plotly_chart(fig, use_container_width=True)

    # 아래 문구를 원하는 한 문장으로 바꿔 주세요.
    show_insight("여기에 이 그래프로 알 수 있는 내용을 한 문장으로 적어 주세요.")


# ─────────────────────────────────────────────
# 구역 2: 일관객 합계 상위 5편 비교
# ─────────────────────────────────────────────
def section_top5_compare() -> None:
    st.header("2. 일관객 합계 상위 5편 비교")

    # 이 기간 일관객 합계가 가장 큰 5편
    top5 = df.groupby("영화명")["일관객"].sum().nlargest(5).index.tolist()
    top5_df = df[df["영화명"].isin(top5)].sort_values(["영화명", "날짜"])

    fig = px.line(
        top5_df,
        x="날짜",
        y="일관객",
        color="영화명",
        category_orders={"영화명": top5},  # 범례를 합계 큰 순서로
        title="일관객 합계 상위 5편 · 날짜별 일관객",
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "날짜: %{x|%Y-%m-%d}<br>"
            "일관객: %{y:,}명<extra></extra>"
        )
    )
    fig.update_layout(xaxis_title="날짜", yaxis_title="일관객(명)", legend_title_text="영화 (클릭해서 켜고 끄기)")
    st.plotly_chart(fig, use_container_width=True)

    # 아래 문구를 원하는 한 문장으로 바꿔 주세요.
    show_insight("여기에 이 그래프로 알 수 있는 내용을 한 문장으로 적어 주세요.")


# ─────────────────────────────────────────────
# 구역 3: 날짜별 10위권 일관객 합계
# ─────────────────────────────────────────────
def section_daily_total() -> None:
    st.header("3. 날짜별 10위권 일관객 합계")

    # 날짜별로 그날 10위권 일관객을 모두 더함
    daily = df.groupby("날짜", as_index=False)["일관객"].sum().sort_values("날짜")
    # 합계가 가장 컸던 3일
    top3 = daily.nlargest(3, "일관객")

    fig = px.area(
        daily,
        x="날짜",
        y="일관객",
        title="날짜별 10위권 일관객 합계",
    )
    fig.update_traces(
        hovertemplate="날짜: %{x|%Y-%m-%d}<br>10위권 일관객 합계: %{y:,}명<extra></extra>"
    )

    # 합계 상위 3일: 점을 찍고 날짜를 적음
    fig.add_scatter(
        x=top3["날짜"],
        y=top3["일관객"],
        mode="markers+text",
        text=top3["날짜"].dt.strftime("%Y-%m-%d"),
        textposition="top center",
        cliponaxis=False,
        marker=dict(size=11, color="crimson", line=dict(width=2, color="white")),
        name="합계 상위 3일",
        hovertemplate="날짜: %{x|%Y-%m-%d}<br>10위권 일관객 합계: %{y:,}명<extra></extra>",
    )
    # 날짜 글씨가 위에서 잘리지 않도록 위쪽 여백 확보
    fig.update_yaxes(range=[0, daily["일관객"].max() * 1.15])
    fig.update_layout(xaxis_title="날짜", yaxis_title="10위권 일관객 합계(명)")
    st.plotly_chart(fig, use_container_width=True)

    # 아래 문구를 원하는 한 문장으로 바꿔 주세요.
    show_insight("여기에 이 그래프로 알 수 있는 내용을 한 문장으로 적어 주세요.")


# ─────────────────────────────────────────────
# 구역 4: 영화별 일관객 합계 TOP 10
# ─────────────────────────────────────────────
def section_top10_bar() -> None:
    st.header("4. 영화별 일관객 합계 TOP 10")

    # 영화별 일관객 합계와 10위권에 든 날수
    summary = (
        df.groupby("영화명")
        .agg(일관객합계=("일관객", "sum"), 십위권날수=("날짜", "nunique"))
        .reset_index()
        .nlargest(10, "일관객합계")
    )

    fig = px.bar(
        summary,
        x="일관객합계",
        y="영화명",
        orientation="h",
        custom_data=["십위권날수"],
        title="영화별 일관객 합계 TOP 10",
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "일관객 합계: %{x:,}명<br>"
            "10위권에 든 날수: %{customdata[0]}일<extra></extra>"
        )
    )
    # 관객이 많은 영화가 위로 오도록 정렬
    fig.update_yaxes(categoryorder="total ascending")
    fig.update_layout(xaxis_title="일관객 합계(명)", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    # 아래 문구를 원하는 한 문장으로 바꿔 주세요.
    show_insight("여기에 이 그래프로 알 수 있는 내용을 한 문장으로 적어 주세요.")


# ─────────────────────────────────────────────
# 구역 5: 월×요일별 일관객 합계 히트맵
# ─────────────────────────────────────────────
def section_month_weekday_heatmap() -> None:
    st.header("5. 월×요일별 일관객 합계")

    weekdays = ["월", "화", "수", "목", "금", "토", "일"]  # 월요일 → 일요일
    month_labels = [f"{m}월" for m in range(1, 13)]

    # 날짜에서 월과 요일 뽑기 (dayofweek: 월요일=0 … 일요일=6)
    temp = df.assign(
        월=df["날짜"].dt.month.astype(str) + "월",
        요일=df["날짜"].dt.dayofweek.map(dict(enumerate(weekdays))),
    )

    # 요일(행) × 월(열) 일관객 합계표
    pivot = temp.pivot_table(
        index="요일", columns="월", values="일관객", aggfunc="sum", fill_value=0
    ).reindex(index=weekdays, columns=month_labels, fill_value=0)

    fig = px.imshow(
        pivot,
        color_continuous_scale="Blues",  # 진할수록 관객이 많음
        aspect="auto",
        title="월×요일별 일관객 합계",
        labels=dict(x="월", y="요일", color="일관객 합계(명)"),
    )
    fig.update_traces(
        hovertemplate="%{x} %{y}요일<br>일관객 합계: %{z:,}명<extra></extra>"
    )
    st.plotly_chart(fig, use_container_width=True)

    # 아래 문구를 원하는 한 문장으로 바꿔 주세요.
    show_insight("여기에 이 그래프로 알 수 있는 내용을 한 문장으로 적어 주세요.")


# ─────────────────────────────────────────────
# 구역 6 이후: 그래프를 추가할 때는 아래처럼 함수를 만들고
# 맨 아래 '구역 실행' 부분에 호출을 한 줄 추가하면 됩니다.
# ─────────────────────────────────────────────
# def section_next_graph() -> None:
#     st.header("6. 새 그래프 제목")
#     ...
#     show_insight("한 문장")


# ─────────────────────────────────────────────
# 구역 실행 (구역 사이에는 구분선)
# ─────────────────────────────────────────────
section_daily_audience()
st.divider()
section_top5_compare()
st.divider()
section_daily_total()
st.divider()
section_top10_bar()
st.divider()
section_month_weekday_heatmap()
st.divider()
# section_next_graph()
# st.divider()
