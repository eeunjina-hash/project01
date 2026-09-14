import os
import json
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

# 1. 상위 폴더(.env) 키 로드
current_dir = Path(__file__).resolve().parent
parent_env_path = current_dir.parent / ".env"
load_dotenv(dotenv_path=parent_env_path)

KAKAO_API_KEY = os.getenv("KAKAO_MAP_API_KEY")

st.set_page_config(
    page_title="카카오 맵 서비스",
    page_icon="🗺️",
    layout="wide"
)

if not KAKAO_API_KEY:
    st.error(f"상위 폴더({parent_env_path})의 `.env` 파일에 KAKAO_MAP_API_KEY가 설정되지 않았습니다.")
    st.stop()

# 2. 장소 목록 데이터 (위도, 경도, 카테고리 등)
places = [
    {"name": "서울시청", "lat": 37.5665, "lon": 126.9780, "desc": "서울특별시 중구 세종대로 110"},
    {"name": "경복궁", "lat": 37.5796, "lon": 126.9770, "desc": "조선 왕조의 법궁"},
    {"name": "남산서울타워", "lat": 37.5512, "lon": 126.9882, "desc": "서울의 대표 랜드마크"},
    {"name": "강남역", "lat": 37.4979, "lon": 127.0276, "desc": "강남 핵심 상권/환승역"}
]

places_json = json.dumps(places, ensure_ascii=False)

# 3. 사이드바 UI
with st.sidebar:
    st.header("📍 장소 리스트")
    st.caption("카카오 지도 SDK 기반 단독 맵 서비스")
    for p in places:
        st.markdown(f"**{p['name']}**\n- {p['desc']}")

# 4. 순수 카카오 지도 웹 템플릿
# kakao.maps.ControlPosition, 지도 컨트롤, 인포윈도우 등 순수 카카오 SDK만 사용
kakao_map_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <!-- 카카오 공식 SDK 로드 (autoload=false) -->
    <script type="text/javascript" src="https://dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_API_KEY}&autoload=false"></script>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        html, body {{
            width: 100%;
            height: 100%;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
        }}
        #map {{
            width: 100%;
            height: 680px;
            border-radius: 12px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
        }}
        .custom-overlay {{
            position: relative;
            bottom: 45px;
            border-radius: 6px;
            border: 1px solid #ccc;
            border-bottom: 2px solid #ddd;
            background-color: #fff;
            padding: 6px 12px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            font-size: 13px;
            font-weight: 600;
            color: #222;
            white-space: nowrap;
        }}
        .custom-overlay:after {{
            content: '';
            position: absolute;
            margin-left: -6px;
            left: 50%;
            bottom: -6px;
            width: 10px;
            height: 10px;
            background: #fff;
            border-bottom: 1px solid #ccc;
            border-right: 1px solid #ccc;
            transform: rotate(45deg);
        }}
    </style>
</head>
<body>
    <div id="map"></div>

    <script>
        kakao.maps.load(function() {{
            var container = document.getElementById('map');
            var options = {{
                center: new kakao.maps.LatLng(37.5665, 126.9780), // 서울 중심
                level: 8
            }};

            // 1) 순수 카카오 맵 인스턴스 생성
            var map = new kakao.maps.Map(container, options);

            // 2) 일반 지도 <-> 스카이뷰 전환 컨트롤 추가
            var mapTypeControl = new kakao.maps.MapTypeControl();
            map.addControl(mapTypeControl, kakao.maps.ControlPosition.TOPRIGHT);

            // 3) 줌 확대/축소 컨트롤 추가
            var zoomControl = new kakao.maps.ZoomControl();
            map.addControl(zoomControl, kakao.maps.ControlPosition.RIGHT);

            // 4) 장소 데이터 마커 & 커스텀 오버레이 등록
            var places = {places_json};

            places.forEach(function(place) {{
                var position = new kakao.maps.LatLng(place.lat, place.lon);

                // 마커 생성
                var marker = new kakao.maps.Marker({{
                    map: map,
                    position: position
                }});

                // 카카오 커스텀 오버레이(말풍선 라벨) 생성
                var content = '<div class="custom-overlay">' + place.name + '</div>';
                var customOverlay = new kakao.maps.CustomOverlay({{
                    map: map,
                    position: position,
                    content: content,
                    yAnchor: 1
                }});

                // 마커 클릭 시 해당 위치로 부드럽게 이동(PanTo)
                kakao.maps.event.addListener(marker, 'click', function() {{
                    map.panTo(position);
                }});
            }});
        }});
    </script>
</body>
</html>
"""

# Streamlit 화면 상단
st.subheader("🗺️ 서울 핵심 거점 지도")

# 5. Streamlit 내에 카카오 전용 지도 렌더링
components.html(kakao_map_html, height=700)