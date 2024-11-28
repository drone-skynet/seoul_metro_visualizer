import streamlit as st
import pandas as pd
import pydeck as pdk

# File path for the merged data
file_path = "data/Merged_Subway_Data.csv"
data = pd.read_csv(file_path)

# Define line-specific colors
line_colors = {
    "1호선": "#0052A4",
    "2호선": "#009D3E",
    "3호선": "#EF7C1C",
    "4호선": "#00A5DE",
    "5호선": "#996CAC",
    "6호선": "#CD7C2F",
    "7호선": "#747F00",
    "8호선": "#EA545D",
    "9호선": "#A17E46",
    "신림선": "#6789CA",
    "우이신설선": "#B0CE18"
}

# Ensure '사용월' is treated as a string
data['Date'] = data['사용월'].astype(str)
data['Month'] = data['Date'].str[4:6]  # Extract month

# Map line colors to a new column and fill NaN values with a default color
data['LineColor'] = data['Line'].map(line_colors).fillna("#808080")  # Default color: gray

# Convert hex colors to RGB and handle potential NaN values
def hex_to_rgb(hex_color):
    """Convert HEX color to RGB tuple. Default to gray if invalid."""
    try:
        return [int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16), 160]
    except (TypeError, ValueError):
        return [128, 128, 128, 160]  # Gray color with transparency

data['RGBColor'] = data['LineColor'].apply(hex_to_rgb)

# Extract unique time slots from column names
time_slots = list(
    {col.split(" ")[0] for col in data.columns if "승차인원" in col or "하차인원" in col}
)

# Streamlit app configuration
st.title("2024년 서울 지하철 시간대별 이용 현황")
st.sidebar.header("옵션 선택")

# Month selection
month_options = sorted(data['Month'].unique())
selected_month = st.sidebar.selectbox("월 선택 (1월 ~ 10월)", month_options)

# Time slot selection
selected_time_slot = st.sidebar.selectbox("시간대 선택", sorted(time_slots))

# Circle size scaling factor selection
scale_factor = st.sidebar.slider("동그라미 크기 배율", min_value=100, max_value=1000, step=50, value=500)

# Filter data for the selected month
filtered_data = data[data['Month'] == selected_month]

# Filter data for the selected time slot
entry_column = f"{selected_time_slot} 승차인원"
exit_column = f"{selected_time_slot} 하차인원"

if entry_column not in filtered_data.columns or exit_column not in filtered_data.columns:
    st.error(f"선택한 시간대 데이터가 없습니다: {selected_time_slot}")
    st.stop()

filtered_data['Users'] = filtered_data[entry_column] + filtered_data[exit_column]
filtered_data['Size'] = filtered_data['Users'] / filtered_data['Users'].max() * scale_factor  # Dynamic scaling

# Pydeck visualization
st.subheader(f"{selected_month}월 [{selected_time_slot}] 평균")
view_state = pdk.ViewState(
    latitude=filtered_data['Latitude'].mean(),
    longitude=filtered_data['Longitude'].mean(),
    zoom=10,
    pitch=50
)

circle_layer = pdk.Layer(
    "ScatterplotLayer",
    data=filtered_data,
    get_position="[Longitude, Latitude]",
    get_fill_color="RGBColor",
    get_radius="Size",
    pickable=True,
    auto_highlight=True
)

deck = pdk.Deck(
    layers=[circle_layer],
    initial_view_state=view_state,
    tooltip={
        "html": "<b>역명:</b> {Station} <br><b>시간대 이용자:</b> {Users}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }
)

# Display map
st.pydeck_chart(deck)

# Additional information
st.sidebar.markdown("지도에서 동그라미 크기는 시간대별 상대적인 이용자 수를 나타냅니다.")
st.sidebar.markdown("동그라미 색상은 실제 노선별 색상으로 표시됩니다.")
st.markdown("데이터 출처: 서울 열린데이터 광장(https://data.seoul.go.kr)")
st.markdown("지도 제공: Mapbox, OpenStreetMap")

# Footer
st.markdown("---")  # 구분선
st.markdown("Powered by 캡스톤디자인 Skynet팀")
