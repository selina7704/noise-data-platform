# Streamlit: 웹 앱을 만들기 위한 라이브러리
import streamlit as st
# Pandas: 데이터프레임으로 데이터를 다루기 위한 라이브러리
import pandas as pd
# Plotly Express: 간단한 인터랙티브 그래프 생성
import plotly.express as px
# Plotly Graph Objects: 복잡한 그래프를 위한 도구
import plotly.graph_objects as go
# NumPy: 수치 연산을 위한 라이브러리
import numpy as np
# Datetime: 날짜와 시간 처리
from datetime import datetime, timedelta
# MySQL Connector: MySQL 데이터베이스 연결
import mysql.connector
# config.py에서 DB 설정 가져오기 (예: 사용자 이름, 비밀번호, DB 이름 등)
from config import DB_CONFIG

# 통계 페이지를 위한 클래스 정의
class Statistics_page:
    # 특정 사용자의 데이터를 DB에서 가져오는 함수
    def fetch_data_from_db(self, user_id, days=30):
        # DB에 연결 (config.py의 설정 사용)
        conn = mysql.connector.connect(**DB_CONFIG)
        # 딕셔너리 형태로 결과를 받기 위한 커서 (컬럼명: 값 형태)
        cursor = conn.cursor(dictionary=True)
        # SQL 쿼리: 사용자 ID와 최근 며칠 데이터를 조회, 최신순 정렬
        query = """
            SELECT noise_type, spl_peak, spl_rms, estimated_distance, direction, 
                   latitude, longitude, alarm_triggered, audio_path, timestamp
            FROM classification_results
            WHERE user_id = %s AND timestamp > %s
            ORDER BY timestamp DESC
        """
        # 현재 날짜에서 days만큼 뺀 날짜 계산 (과거 데이터 필터링용)
        cutoff_date = datetime.now() - timedelta(days=days)
        # 쿼리 실행 (user_id와 cutoff_date를 매개변수로 전달)
        cursor.execute(query, (user_id, cutoff_date))
        # 모든 결과 가져오기
        data = cursor.fetchall()
        # DB 연결 종료
        conn.close()
        # 데이터가 없으면 빈 데이터프레임 반환
        if not data:
            return pd.DataFrame()
        # 데이터를 데이터프레임으로 변환
        df = pd.DataFrame(data)
        # 소음 강도를 실수형으로 변환 (DB에서 문자열일 수 있음)
        df['spl_peak'] = df['spl_peak'].astype(float)
        df['spl_rms'] = df['spl_rms'].astype(float)
        # 추정 거리를 숫자형으로 변환 (오류 시 NaN으로 처리)
        df['estimated_distance'] = pd.to_numeric(df['estimated_distance'], errors='coerce')
        # 소음 강도에 따라 경고 레이블 추가 (70dB 이상: 위험, 50dB 이상: 주의)
        df['warning'] = df['spl_peak'].apply(lambda x: '위험' if x >= 70 else '주의' if x >= 50 else None)
        # 알람 응답 여부를 True/False로 변환 (1: 응답, 0: 미응답, NaN: 알 수 없음)
        df['safety_check'] = df['alarm_triggered'].apply(lambda x: True if x == 1 else False if pd.notna(x) else None)
        return df

    # 모든 사용자의 데이터를 DB에서 가져오는 함수
    def fetch_all_users_data(self, days=30):
        # DB 연결
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        # SQL 쿼리: 최근 며칠 동안의 모든 사용자 데이터 조회
        query = """
            SELECT user_id, noise_type, spl_peak, latitude, longitude, timestamp
            FROM classification_results
            WHERE timestamp > %s
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        # 쿼리 실행 (cutoff_date만 매개변수로, 모든 사용자 대상)
        cursor.execute(query, (cutoff_date,))
        data = cursor.fetchall()
        conn.close()
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df['spl_peak'] = df['spl_peak'].astype(float)
        return df

    # 위도와 경도를 기반으로 지역명을 반환하는 함수
    def assign_region(self, lat, lon):
        """위도/경도를 기반으로 지역명 매핑, None 처리 추가"""
        # lat 또는 lon이 없거나 NaN이면 "기타" 반환
        if lat is None or lon is None or pd.isna(lat) or pd.isna(lon):
            return "기타"
        # 실수형으로 변환 (DB에서 문자열로 올 수 있음)
        lat, lon = float(lat), float(lon)
        # 지역 매핑: 위도/경도 범위에 따라 지역명 반환 (범위를 넓게 설정)
        if 37.0 <= lat <= 38.0 and 126.5 <= lon <= 127.5:
            return "서울"
        elif 34.5 <= lat <= 35.5 and 128.8 <= lon <= 129.5:
            return "부산"
        elif 35.5 <= lat <= 36.5 and 128.0 <= lon <= 129.0:
            return "대구"
        elif 37.0 <= lat <= 38.0 and 126.0 <= lon <= 126.8:
            return "인천"
        elif 34.8 <= lat <= 35.5 and 126.5 <= lon <= 127.0:
            return "광주"
        elif 33.0 <= lat <= 34.0 and 126.0 <= lon <= 127.0:
            return "제주"
        elif 36.0 <= lat <= 36.7 and 127.0 <= lon <= 127.8:
            return "대전"
        elif 36.5 <= lat <= 37.5 and 127.5 <= lon <= 128.5:
            return "충북"
        else:
            return "기타"

    # 안전지수를 계산하는 함수
    def calculate_safety_index(self, df):
        # 데이터가 없으면 0 반환
        if df.empty:
            return 0
        # 70dB 이상 소음 비율 계산 (%)
        danger_ratio = len(df[df["spl_peak"] >= 70]) / len(df) * 100
        # 위험 경고에 응답하지 않은 비율 계산 (위험 데이터가 있으면 계산, 없으면 0)
        no_response_ratio = (1 - df[df["warning"] == "위험"]["safety_check"].mean()) * 100 if len(df[df["warning"] == "위험"]) > 0 else 0
        # 안전지수: 위험 비율 * 2 + 미응답 비율 (최대 100으로 제한)
        safety_index = min(danger_ratio * 2 + no_response_ratio, 100)
        return safety_index

    # 안전지수를 신호등 UI로 표시하는 함수
    def display_traffic_light(self, safety_index):
        # 안전지수에 따라 색상과 상태 설정
        if safety_index <= 33:
            green, yellow, red = 1, 0.2, 0.2  # 초록 활성화
            status = "안전"
            color = "#6BCB77"  # 초록색
            tooltip = "위험 소음이 적고 응답률이 높아요!"
        elif safety_index <= 66:
            green, yellow, red = 0.2, 1, 0.2  # 노랑 활성화
            status = "주의"
            color = "#FFD93D"  # 노란색
            tooltip = "소음이 다소 높거나 응답이 느려요."
        else:
            green, yellow, red = 0.2, 0.2, 1  # 빨강 활성화
            status = "위험"
            color = "#FF6B6B"  # 빨간색
            tooltip = "위험 소음이 많고 응답이 부족해요!"
        # HTML/CSS로 신호등 UI 표시 (색상과 툴팁 포함)
        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 20px; display: flex; align-items: center; justify-content: center;">
                <h2 style="margin-right: 20px;">나의 안전지수: <span style="color: {color}">{int(safety_index)}</span> ({status})</h2>
                <div style="display: flex; justify-content: center; gap: 20px; align-items: center;">
                    <div style="width: 50px; height: 50px; border-radius: 50%; background-color: #6BCB77; opacity: {green};"></div>
                    <div style="width: 50px; height: 50px; border-radius: 50%; background-color: #FFD93D; opacity: {yellow};"></div>
                    <div class="tooltip" style="width: 50px; height: 50px; border-radius: 50%; background-color: #FF6B6B; opacity: {red};">
                        <span class="tooltiptext">{tooltip}</span>
                    </div>
                    <span style="font-size: 14px; cursor: pointer; color: #1E90FF;" class="tooltip">❓
                        <span class="tooltiptext">안전지수는 소음 강도와 경고 응답 여부를 기반으로 계산됩니다.<br>- 0-33: 안전 (초록)<br>- 34-66: 주의 (노랑)<br>- 67-100: 위험 (빨강)<br>계산: (70dB 이상 소음 비율 × 2) + (위험 경고 미응답 비율)</span>
                    </span>
                </div>
            </div>
            <style>
                .tooltip {{ position: relative; display: inline-block; }}
                .tooltip .tooltiptext {{ visibility: hidden; width: 250px; background-color: #555; color: #fff; text-align: left; border-radius: 6px; padding: 5px; position: absolute; z-index: 1; top: 125%; left: 50%; margin-left: -125px; opacity: 0; transition: opacity 0.3s; }}
                .tooltip:hover .tooltiptext {{ visibility: visible; opacity: 1; }}
            </style>
            """, unsafe_allow_html=True
        )

    # 통계 페이지의 메인 함수 (웹 UI 구성)
    def statistics_page(self):
        # 로그인 여부 확인
        if 'user_info' not in st.session_state or 'id' not in st.session_state['user_info']:
            st.warning("로그인이 필요합니다. 로그인 페이지로 이동해주세요.")
            return

        # 현재 사용자 ID 가져오기
        user_id = st.session_state['user_info']['id']

        # 데이터 필터 설정 UI (확장 가능한 섹션)
        with st.expander("🔍 데이터 필터 설정", expanded=True):
            col1, col2 = st.columns(2)  # 2열로 나눔
            with col1:
                # 슬라이더로 최근 며칠 데이터 선택 (기본값: 7일)
                time_range = st.slider("시간 범위 (최근 며칠)", 1, 30, 7, key="time_range")
            with col2:
                # 소음 유형 선택 (다중 선택 가능)
                noise_types = ["차량경적", "이륜차경적", "차량사이렌", "차량주행음", "이륜차주행음", "기타소음"]
                selected_types = st.multiselect("소음 유형", noise_types, default=noise_types, key="noise_types")

        # 사용자 데이터 가져오기
        df = self.fetch_data_from_db(user_id, days=time_range)
        if df.empty:
            st.warning("선택한 기간 내 데이터가 없습니다.")
            return
        # 선택된 소음 유형으로 필터링
        filtered_df = df[df["noise_type"].isin(selected_types)]

        # 요약 통계 UI
        with st.expander("📌 한눈에 보는 통계", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("총 소음 이벤트", len(filtered_df))  # 소음 발생 횟수
            with col2:
                st.metric("평균 소음 강도", f"{filtered_df['spl_peak'].mean():.1f} dB")  # 평균 소음 강도
            with col3:
                safety_index = self.calculate_safety_index(filtered_df)  # 안전지수 계산
                st.metric("안전지수", int(safety_index))  # 안전지수 표시
            self.display_traffic_light(safety_index)  # 신호등 UI 표시

        # 탭으로 통계 섹션 나누기
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "나의 소음 경험", "소음 위치와 방향", "소음 강도 분석", 
            "경고와 응답", "지역과 커뮤니티", "트렌드와 예측"
        ])

        # 탭 1: 나의 소음 경험
        with tab1:
            st.subheader("나의 소음 경험")
            col1, col2, col3 = st.columns(3)
            with col1:
                # 소음 유형별 분포를 원형 차트로 표시
                type_counts = filtered_df["noise_type"].value_counts()
                fig_pie = px.pie(names=type_counts.index, values=type_counts.values, title="소음 유형 분포", hole=0.3)
                st.plotly_chart(fig_pie, use_container_width=True)
                st.info("ℹ️ 소음 유형별 발생 비율을 원형 차트로 표시합니다.")
            with col2:
                # 시간대별 소음 발생 건수를 선 그래프로 표시 (0~23시 모두 포함)
                hourly_df = filtered_df.groupby(filtered_df["timestamp"].dt.strftime('%H:00')).size().reset_index(name='count')
                all_hours = pd.DataFrame({'timestamp': [f"{h:02d}:00" for h in range(24)]})
                hourly_df = all_hours.merge(hourly_df, on='timestamp', how='left').fillna({'count': 0})
                fig_line = px.line(hourly_df, x="timestamp", y="count", title="시간대별 소음 발생")
                st.plotly_chart(fig_line, use_container_width=True)
                st.info("ℹ️ 하루 중 소음 발생 건수를 시간별로 보여줍니다 (0-23시).")
            with col3:
                # 70dB 이상 위험 소음 횟수를 게이지로 표시
                danger_count = len(filtered_df[filtered_df["spl_peak"] >= 70])
                fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=danger_count, 
                                                   domain={'x': [0, 1], 'y': [0, 1]}, title={'text': "위험 소음 횟수"},
                                                   gauge={'axis': {'range': [0, max(10, danger_count+1)]}, 'bar': {'color': "#FF4D4D"}}))
                st.plotly_chart(fig_gauge, use_container_width=True)
                st.info("ℹ️ 70dB 이상 위험 소음 발생 횟수를 게이지로 표시합니다.")
            # 분석 리포트: 가장 빈번한 소음 유형과 일 평균 발생 횟수
            st.markdown(f"📝 *분석 리포트*: 가장 자주 감지된 소음은 '{type_counts.index[0]}' (일 평균 {type_counts[0]/time_range:.1f}회)입니다.")

        # 탭 2: 소음 위치와 방향
        with tab2:
            st.subheader("소음 위치와 방향")
            col1, col2 = st.columns(2)
            with col1:
                # 방향별 소음 빈도를 레이더 차트로 표시
                direction_counts = filtered_df["direction"].value_counts()
                if direction_counts.empty:
                    st.warning("방향 데이터가 부족합니다.")
                    fig_radar = px.line_polar(r=[0], theta=["없음"], line_close=True, title="방향별 소음 분포")
                else:
                    fig_radar = px.line_polar(r=direction_counts.values, theta=direction_counts.index, line_close=True, title="방향별 소음 분포")
                    fig_radar.update_traces(fill="toself")

                st.plotly_chart(fig_radar, use_container_width=True)
                st.info("ℹ️ 소음이 들리는 방향별 빈도를 레이더 차트로 보여줍니다.")
            with col2:
                # 추정 거리별 분포를 막대 차트로 표시
                distance_bins = pd.cut(filtered_df["estimated_distance"], bins=[0, 10, 50, 100], labels=["0-10m", "10-50m", "50m 이상"])
                distance_counts = distance_bins.value_counts()
                fig_bar = px.bar(x=distance_counts.index, y=distance_counts.values, title="추정 거리 분포")
                st.plotly_chart(fig_bar, use_container_width=True)
                st.info("ℹ️ 소음 발생 추정 거리 구간별 분포를 막대 차트로 표시합니다.")
            # 위치 데이터가 있으면 지도에 소음 분포 표시
            map_df = filtered_df.dropna(subset=["latitude", "longitude"])
            if not map_df.empty:
                fig_map = px.scatter_mapbox(
                    map_df, lat="latitude", lon="longitude", color="spl_peak",
                    size="spl_peak", color_continuous_scale=px.colors.sequential.Reds,
                    title="소음 발생 지도", zoom=10, height=400, mapbox_style="open-street-map"
                )
                st.plotly_chart(fig_map, use_container_width=True)
                st.info("ℹ️ 소음 발생 위치를 지도에 표시하며, 색상과 크기로 강도를 나타냅니다.")
            else:
                st.warning("위치 데이터가 없습니다.")
            st.markdown(f"📝 *분석 리포트*: 가장 많이 감지된 방향은 '{direction_counts.index[0] if not direction_counts.empty else '없음'}'입니다.")

        # 탭 3: 소음 강도 분석
        with tab3:
            st.subheader("소음 강도 분석")
            col1, col2 = st.columns(2)
            with col1:
                # 소음 강도 분포를 박스 플롯으로 표시
                avg_db, max_db = filtered_df["spl_peak"].mean(), filtered_df["spl_peak"].max()
                fig_box = px.box(filtered_df, y="spl_peak", title=f"평균 {avg_db:.1f}dB | 최대 {max_db:.1f}dB")
                st.plotly_chart(fig_box, use_container_width=True)
                st.info("ℹ️ 소음 강도의 분포와 평균/최대값을 박스 플롯으로 보여줍니다.")
            with col2:
                # 소음 강도를 안전/주의/위험으로 나눠 비율 표시
                level_bins = pd.cut(filtered_df["spl_peak"], bins=[0, 50, 70, 120], labels=["안전", "주의", "위험"])
                level_counts = level_bins.value_counts(normalize=True) * 100
                fig_stack = px.bar(x=level_counts.index, y=level_counts.values, title="위험 수준별 비율",
                                   color=level_counts.index, color_discrete_map={"안전": "#6BCB77", "주의": "#FFD93D", "위험": "#FF6B6B"})
                st.plotly_chart(fig_stack, use_container_width=True)
                st.info("ℹ️ 소음 강도를 안전/주의/위험으로 나눠 비율을 표시합니다.")
            # 최대 소음 이벤트 정보
            max_noise_row = filtered_df.loc[filtered_df["spl_peak"].idxmax()]
            st.markdown(f"📝 *분석 리포트*: 최대 소음은 {max_noise_row['timestamp'].strftime('%Y-%m-%d %H:%M')}에 {max_noise_row['spl_peak']:.1f}dB ({max_noise_row['noise_type']})로 기록됨.")

        # 탭 4: 경고와 응답
        with tab4:
            st.subheader("경고와 응답")
    
             # SOS 발송 계산
            sos_count = len(filtered_df[(filtered_df["warning"] == "위험") & (filtered_df["safety_check"] == False)])
    
            # 첫 번째 행: SOS 발송과 최근 발송 시간을 한 줄에 배치
            col1, col2 = st.columns([2, 1])  # 2:1 비율로 나눠서 SOS 발송이 더 강조되게
            with col1:
                st.markdown(
                    f"<h3 style='text-align: center;'>🚨 SOS 발송: <span style='color: #FF6B6B;'>{sos_count}회</span></h3>",
                    unsafe_allow_html=True
                )
            with col2:
                if sos_count > 0:
                    latest_sos = filtered_df[(filtered_df["warning"] == "위험") & (filtered_df["safety_check"] == False)].iloc[0]["timestamp"]
                    st.markdown(
                        f"<p style='text-align: center;'>최근 발송: {latest_sos.strftime('%Y-%m-%d %H:%M')}</p>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"<p style='text-align: center;'>최근 발송: 없음</p>",
                        unsafe_allow_html=True
                    )
            st.info("ℹ️ 응답 없는 위험 경고로 발송된 SOS 횟수와 가장 최근 발송 시점입니다.")
    
            # 두 번째 행: 타임라인과 응답률 차트를 나란히 배치
            col3, col4 = st.columns(2)
            with col3:
                # 경고 발생 시점을 타임라인으로 표시
                danger_alerts = len(filtered_df[filtered_df["warning"] == "위험"])
                caution_alerts = len(filtered_df[filtered_df["warning"] == "주의"])
                fig_timeline = px.scatter(
                    filtered_df[filtered_df["warning"].notnull()], 
                    x="timestamp", 
                    y="spl_peak", 
                    color="warning",
                    title=f"경고: 위험 {danger_alerts}회, 주의 {caution_alerts}회",
                    color_discrete_map={"위험": "#FF6B6B", "주의": "#FFD93D"}
                )
                st.plotly_chart(fig_timeline, use_container_width=True)
                st.info("ℹ️ 경고 발생 시점과 강도를 타임라인으로 표시합니다.")
    
            with col4:
                # 위험 경고 응답률을 원형 차트로 표시
                response_rate = filtered_df[filtered_df["warning"] == "위험"]["safety_check"].mean() * 100 if len(filtered_df[filtered_df["warning"] == "위험"]) > 0 else 0
                fig_pie_response = px.pie(
                    values=[response_rate, 100 - response_rate], 
                    names=["응답", "미응답"],
                    title=f"응답률: {response_rate:.1f}%", 
                    hole=0.4,
                    color_discrete_sequence=["#6BCB77", "#FF6B6B"]
                )
                st.plotly_chart(fig_pie_response, use_container_width=True)
                st.info("ℹ️ 위험 경고에 대한 응답 비율을 원형 차트로 보여줍니다.")
    
            # 분석 리포트: 최근 경고 정보
            if not filtered_df[filtered_df["warning"].notnull()].empty:
                latest_alert = filtered_df[filtered_df["warning"].notnull()].iloc[0]
                st.markdown(f"📝 *분석 리포트*: 최근 경고는 {latest_alert['timestamp'].strftime('%Y-%m-%d %H:%M')}에 발생 ({latest_alert['warning']}).")

        # 탭 5: 지역과 커뮤니티
        with tab5:
            st.subheader("지역과 커뮤니티")
            # 모든 사용자 데이터 가져오기
            all_users_df = self.fetch_all_users_data(days=time_range)
            if not all_users_df.empty:
                # 위도/경도로 지역 할당
                all_users_df['region'] = all_users_df.apply(lambda row: self.assign_region(row['latitude'], row['longitude']), axis=1)
        
                # 추가 통계 계산
                total_users = all_users_df['user_id'].nunique()  # 고유 사용자 수
                total_noises = len(all_users_df)  # 총 소음 이벤트 수
                noise_type_counts = all_users_df["noise_type"].value_counts()  # 소음 유형별 빈도
        
                # 첫 번째 행: 전체 유저 수와 소음 개수를 한 줄에 배치
                col1, col2 = st.columns(2)  # 2열로 나눔
                with col1:
                    st.metric(label="👤 전체 유저 수", value=total_users)  # 사람 아이콘 추가
                with col2:
                    st.metric(label="📢 현재까지 담긴 소음 개수", value=total_noises)  # 확성기 아이콘 추가
        
                # 두 번째 행: 소음 유형과 지역별 평균 소음을 한 줄에 배치
                col3, col4 = st.columns(2)  # 다시 2열로 나눔
                with col3:
                    # 전체 유저 소음 유형을 원형 차트로 표시
                    fig_noise_pie = px.pie(names=noise_type_counts.index, values=noise_type_counts.values, 
                                    title="전체 유저 소음 유형", hole=0.3)
                    st.plotly_chart(fig_noise_pie, use_container_width=True)
                with col4:
                    # 지역별 평균 소음을 막대 그래프로 표시
                    region_avg = all_users_df.groupby('region')['spl_peak'].mean().reset_index()
                    fig_region_bar = px.bar(region_avg, x="region", y="spl_peak", title="지역별 평균 소음", 
                                    color="spl_peak", color_continuous_scale="Reds")
                    st.plotly_chart(fig_region_bar, use_container_width=True)
        
                # 전국 소음 분포를 지도에 표시 (별도 섹션으로 유지)
                region_map = all_users_df.dropna(subset=["latitude", "longitude"])
                fig_region_map = px.scatter_mapbox(
                    region_map, lat="latitude", lon="longitude", color="spl_peak",
                    size="spl_peak", color_continuous_scale=px.colors.sequential.Reds,
                    title="전국 소음 분포", zoom=6, center={"lat": 36.5, "lon": 127.5}, height=400, mapbox_style="open-street-map"
                )
                st.plotly_chart(fig_region_map, use_container_width=True)
                st.info("ℹ️ 모든 사용자 데이터를 기반으로 전국 소음 발생 위치를 지도에 표시합니다.")
    
            # 개인과 전체 평균 소음 비교
            avg_spl = filtered_df["spl_peak"].mean()
            st.markdown(f"📝 *분석 리포트*: 당신의 평균 소음은 {avg_spl:.1f}dB로, 전체 사용자 평균 {all_users_df['spl_peak'].mean():.1f}dB와 비교됩니다.")

        # 탭 6: 트렌드와 예측
        with tab6:
            st.subheader("트렌드와 예측")
            # 타임스탬프에서 연도와 주 번호 추출
            filtered_df['year'] = filtered_df["timestamp"].dt.year
            filtered_df['week'] = filtered_df["timestamp"].dt.isocalendar().week
            # 주별 소음 강도 평균 계산
            weekly_df = filtered_df.groupby(['year', 'week'])["spl_peak"].mean().reset_index()
            if weekly_df.empty:
                # 데이터가 없으면 경고와 빈 그래프 표시
                st.warning("주간 데이터가 부족합니다.")
                fig_trend = px.line(x=["없음"], y=[0], title="주간 소음 트렌드")
            else:
                # 주 번호를 정수형으로 변환
                weekly_df['week'] = weekly_df['week'].astype(int)
                # 주 라벨 생성 (예: "2025-W01")
                weekly_df['week_label'] = weekly_df.apply(lambda row: f"{int(row['year'])}-W{int(row['week']):02d}", axis=1)
                # 주간 소음 트렌드를 선 그래프로 표시
                fig_trend = px.line(weekly_df, x="week_label", y="spl_peak", title="주간 소음 트렌드")
                # 소음 증가/감소율 계산
                increase = (weekly_df["spl_peak"].iloc[-1] - weekly_df["spl_peak"].iloc[0]) / weekly_df["spl_peak"].iloc[0] * 100 if len(weekly_df) > 1 else 0
                st.markdown(f"📝 *분석 리포트*: 소음 강도 {increase:.1f}% {'증가' if increase > 0 else '감소'}.")
            st.plotly_chart(fig_trend, use_container_width=True)
            st.info("ℹ️ 주 단위로 평균 소음 강도의 변화를 선 그래프로 보여줍니다.")
            # 예측 메시지 (현재는 하드코딩, 실제 AI 모델 미구현)
            st.warning("⚠️ 내일 18:00-20:00에 소음 증가 예상 (AI 예측, 개발 중)")

# 실행: Statistics_page 클래스의 인스턴스 생성 후 통계 페이지 표시
if __name__ == "__main__":
    m = Statistics_page()
    m.statistics_page()