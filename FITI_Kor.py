import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import plotly.express as px

# 1. 페이지 설정 (넓은 레이아웃)
st.set_page_config(page_title="FITI 열화 물성 예측", layout="wide")


#사전 정의 영역===============
# ---------------------------------------------------------
# 1. 팝업창(Dialog) 함수 정의 (상단에 작성)
# ---------------------------------------------------------
@st.dialog("예측 데이터 다운로드")
def show_export_dialog():
    st.write("다운로드 할 항목을 선택해주세요.")

    # 팝업 내 선택 옵션들
    시료_샘플 = st.checkbox("시료 샘플", value=True)
    열화_조건 = st.checkbox("열화 조건", value=True)
    열화_물성 = st.checkbox(label="열화 물성", value=True)


    st.write("")

    # 팝업 내부 확인/취소 버튼
    col1, col2 = st.columns(2)
    with col1:
        if st.button("확인 및 다운로드", type="primary", use_container_width=True):
            st.success("성공적으로 다운로드가 완료되었습니다")
            # 실제 데이터 추출 처리 로직 작성 위치
            st.rerun()  # 작업 완료 후 팝업창 닫기

    with col2:
        if st.button("취소", use_container_width=True):
            st.rerun()  # 팝업창 닫기
#===============

# ---------------------------------------------------------
# [사이드바 영역]
# ---------------------------------------------------------
with st.sidebar:

    st.markdown("### 프로젝트 선택")
    project= st.selectbox(
        label= "프로젝트를 선택해주세요",
        options=["PCB 소재 프로젝트"],
        label_visibility='collapsed',
    )

    st.markdown("### 물성 및 시료 정보 입력")
    prop = st.selectbox(
        "확인하고자 하는 물성을 선택해주세요",
        ["인장 강도", "신율"],
        label_visibility="visible",)

    밀도 = st.number_input("밀도를 입력하세요",min_value=0.0,max_value=5.0,value=0.0,label_visibility="visible")
    유리전이온도 = st.number_input("유리전이온도를 입력하세요",min_value=0.0,max_value=300.0,value=0.0,label_visibility="visible")

    st.markdown("### 예측 열화 시간")
    target_hour = st.number_input("열화 예측을 할 시간을 입력하세요",min_value=0.0,max_value=244.0,value=0.0,label_visibility="visible")

    # 체크박스 2개 가로 배치
    c1, c2 = st.columns(2)
    with c1:
        show_curve = st.checkbox("열화 곡선 ", value=True)
    with c2:
        show_band = st.checkbox("계산 범위 ", value=True)

    st.write("")

    if st.button("데이터 내려받기", type='primary',use_container_width=True):
        show_export_dialog()
    if st.button(label="기본값 초기화", use_container_width=True):
        st.write("기본값 초기화")

    st.caption("원작자 : Rishabh Gupta, 수정자 : 손용화")

# ---------------------------------------------------------
# [메인 영역]
# ---------------------------------------------------------

# 1. Title & Metadata
st.title("FITI 열화 물성 예측 프로그램")
st.markdown(
    """
**학습된 샘플:** 8 &nbsp;&nbsp; **학습된 물성:** 7 &nbsp;&nbsp; **마지막 학습 일자:** 26.10.17
""")

# 2. Tabs
tab1, tab2, tab3 ,tab4 = st.tabs(
    ["예측 모델", "상관 분석", "특징", "데이터 업로드"]
)

# 1. 엑셀 파일(test_ts.xlsx) 내 전체 8개 모델 데이터 구축
time_steps = np.array([0, 20, 40, 60, 80, 100, 120, 140, 160, 180])

model_data = {
    "Polymerize": np.array(
        [
            290.435,
            285.103,
            278.795,
            277.917,
            273.272,
            272.483,
            271.694,
            270.905,
            270.116,
            269.327,
        ]
    ),
    "Stacked": np.array(
        [
            291.156,
            286.495,
            277.327,
            278.061,
            272.318,
            273.160,
            274.002,
            274.844,
            275.685,
            276.527,
        ]
    ),
    "XGB": np.array(
        [
            290.386,
            290.386,
            279.842,
            279.842,
            273.775,
            273.775,
            273.775,
            273.775,
            273.775,
            273.775,
        ]
    ),
    "Bayesian Ridge": np.array(
        [
            282.952,
            279.503,
            276.054,
            272.606,
            269.157,
            265.708,
            262.259,
            258.811,
            255.362,
            251.913,
        ]
    ),
    "Gaussian Process": np.array(
        [
            286.680,
            284.481,
            284.481,
            284.481,
            284.481,
            284.481,
            284.481,
            284.481,
            284.481,
            284.481,
        ]
    ),
    "Lasso CV": np.array(
        [
            286.465,
            282.372,
            278.280,
            274.187,
            270.095,
            266.002,
            261.910,
            257.818,
            253.725,
            249.633,
        ]
    ),
    "Polynomial Ridge": np.array(
        [
            289.577,
            284.877,
            280.177,
            275.477,
            270.777,
            266.077,
            261.377,
            256.677,
            251.977,
            247.277,
        ]
    ),
    "Random Forest": np.array(
        [
            293.221,
            281.883,
            279.558,
            279.337,
            276.302,
            276.302,
            276.302,
            276.302,
            276.302,
            276.302,
        ]
    ),
}

# 각 모델별 선 색상 지정 (MATLAB 컬러 팔레트 기반)
colors = {
    "Polymerize": "#0072BD",  # Classic Blue
    "Stacked": "#7E2F8E",  # Purple
    "XGB": "#77AC30",  # Green
    "Bayesian Ridge": "#4DBEEE",  # Cyan
    "Gaussian Process": "#D95319",  # Red/Orange
    "Lasso CV": "#ED1C24",  # Red
    "Polynomial Ridge": "#E69F00",  # Yellow/Orange
    "Random Forest": "#A2142F",  # Maroon
}

with tab1:
    # 1. 소제목 및 열화 시간 정보 병합 표시
    st.subheader(f"{prop}  |  예측 열화 시간: {int(target_hour)} hr")

    # 레이아웃 분할 (그래프 영역 : 오른쪽 요약 및 모델선택 영역 = 5 : 3)
    col_chart, col_card = st.columns([5, 3])

    # ---------------------------------------------------------
    # 1. [우측 모델 선택 드롭다운 및 예측 결과 카드 패널]
    # ---------------------------------------------------------
    with col_card:
        # (1) [최상단] 머신 러닝 모델 선택 (다중 선택 드롭다운)
        st.markdown("#### 머신 러닝 모델 선택")

        model_options = [
            "Polymerize",
            "Stacked",
            "XGB ",
            "Bayesian Ridge",
            "Gaussian Process",
            "Lasso CV ",
            "Polynomial Ridge",
            "Random Forest",
        ]

        model_name_map = {
            "Polymerize": "Polymerize",
            "Stacked": "Stacked",
            "XGB": "XGB",
            "Bayesian Ridge": "Bayesian Ridge",
            "Gaussian Process": "Gaussian Process",
            "Lasso CV": "Lasso CV",
            "Polynomial Ridge": "Polynomial Ridge",
            "Random Forest": "Random Forest",
        }

        selected_dropdown = st.multiselect(
            "비교할 머신러닝 모델을 선택하세요",
            options=model_options,
            default=["Polymerize", "Stacked"],
            label_visibility="collapsed",
        )

        active_models = [model_name_map[item] for item in selected_dropdown]

        st.write("")

        # (2) 선택된 첫 번째 대표 모델의 예측 인장 강도 요약 카드
        if active_models:
            primary_model = active_models[0]
            primary_target_y = float(
                np.interp(target_hour, time_steps, model_data[primary_model])
            )

            st.markdown(
                f"""
                <div style="border: 1px solid #E5E7EB; border-radius: 12px; padding: 20px; background-color: #FFFFFF; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <p style="color: #6B7280; font-size: 13px; font-weight: bold; margin-bottom: 5px;">예측 {prop} ({primary_model})</p>
                    <h1 style="font-size: 32px; font-weight: 800; margin: 0; color: #111827;">{primary_target_y:.2f} MPa</h1>
                </div>
                <br>
                """,
                unsafe_allow_html=True,
            )

            # 선택된 모델이 2개 이상일 경우 다중 수치 비교 표기
            if len(active_models) > 1:
                st.markdown("**선택 모델별 수치 비교**")
                for m_name in active_models:
                    m_target_y = float(
                        np.interp(target_hour, time_steps, model_data[m_name])
                    )
                    st.markdown(f"• **{m_name}**: `{m_target_y:.2f} MPa`")
        else:
            st.warning("드롭다운에서 하나 이상의 머신러닝 모델을 선택해주세요.")

    # ---------------------------------------------------------
    # 2. [좌측 차트 영역]
    # ---------------------------------------------------------
    with col_chart:
        fig = go.Figure()

        # (1) 선택된 모델들의 열화 곡선 Plotting
        if show_curve:
            for m_name in active_models:
                fig.add_trace(
                    go.Scatter(
                        x=time_steps,
                        y=model_data[m_name],
                        mode="lines+markers",
                        name=f"{m_name} Model",
                        line=dict(color=colors[m_name], width=2.0),
                        marker=dict(size=5),
                    )
                )

        # (2) 선택된 모든 모델에 대해 각각 별표(Target Point) 및 수치 표기
        for m_name in active_models:
            m_target_y = float(
                np.interp(target_hour, time_steps, model_data[m_name])
            )
            fig.add_trace(
                go.Scatter(
                    x=[target_hour],
                    y=[m_target_y],
                    mode="markers+text",
                    name=f"{m_name} @ {int(target_hour)}h",
                    marker=dict(symbol="star", size=13, color=colors[m_name]),
                    text=[f"{m_target_y:.1f}"],
                    textposition="top right",
                    textfont=dict(family="Arial", size=10, color=colors[m_name]),
                )
            )

        # (3) MATLAB 스타일 축 및 레이아웃 설정
        fig.update_layout(
            template="plotly_white",
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            xaxis=dict(
                title=dict(
                    text="<b>Degradation time (h)</b>",
                    font=dict(family="Arial", size=12, color="#000000"),
                ),
                showgrid=True,
                gridcolor="#E5E5E5",
                gridwidth=0.8,
                showline=True,
                linecolor="#000000",
                linewidth=1.2,
                mirror=True,
                ticks="inside",
                tickfont=dict(family="Arial", size=10, color="#000000"),
            ),
            yaxis=dict(
                title=dict(
                    text=f"<b>{prop} Value (MPa)</b>",
                    font=dict(family="Arial", size=12, color="#000000"),
                ),
                showgrid=True,
                gridcolor="#E5E5E5",
                gridwidth=0.8,
                showline=True,
                linecolor="#000000",
                linewidth=1.2,
                mirror=True,
                ticks="inside",
                tickfont=dict(family="Arial", size=10, color="#000000"),
            ),
            legend=dict(
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor="#000000",
                borderwidth=1,
                font=dict(family="Arial", size=10, color="#000000"),
                x=0.98,
                y=0.98,
                xanchor="right",
                yanchor="top",
            ),
            margin=dict(l=30, r=30, t=20, b=30),
            height=480,
        )

        st.plotly_chart(fig, use_container_width=True)
#=======================상관 분석 파트==============================================================================
with tab2:
        st.subheader("변수 간 상관 분석")
        st.caption("원료의 성질과 공정, 물성 간의 상관 관계를 확인할 수 있습니다.")

        # 1. 상관분석용 샘플 데이터 생성 (실제 데이터프레임으로 교체 가능)
        data = {
            "밀도": [2.38, 2.40, 2.35, 2.39, 2.42, 2.37],
            "유리전이온도": [179, 182, 175, 180, 185, 178],
            "열화 시간": [0, 20, 50, 70, 100, 150],
            "인장 강도": [302, 285, 278, 264, 230, 210],
        }
        df = pd.DataFrame(data)

        # 2. 상관계수 계산
        corr = df.corr()

        fig_corr = px.imshow(
            corr,
            text_auto=".2f",  # 소수점 둘째 자리까지 표시
            aspect="auto",
            color_continuous_scale="RdBu_r",  # 학술 논문 스타일 (레드-블루 계열)
            zmin=-1,
            zmax=1,
            title="상관계수 히트맵"
            )

        fig_corr.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            height=400
            )

        st.plotly_chart(fig_corr, use_container_width=True)

        st.divider()

        st.markdown("#### 상관계수 표")
        # 수치 데이터프레임 깔끔하게 표시
        st.dataframe(
                corr.style.background_gradient(cmap="coolwarm", axis=None).format("{:.2f}"),
                use_container_width=True,
                height=180
            )
        st.download_button(
            label="상관계수 데이터 (CSV) 다운로드/ 현재는 지원하지 않는 기능입니다.",
            data=corr.to_csv().encode("utf-8-sig"),
            file_name="correlation_matrix.csv",
            mime="text/csv",
        )
with tab3:
    st.write("특징 정보 업로드 필요, Rishabh과 논의")

with tab4:
    st.write("차후 엑셀 파일 업로드 시, 학습에 자동반영될 수 있도록 플랫폼 수정 예정 / Rishabh과 논의 필요")