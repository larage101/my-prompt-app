import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

st.set_page_config(page_title="Custom Prompt Extractor", layout="centered")
st.title("📸 SDXL & Grok 전용 프롬프트 추출기")

# -----------------------------
# API KEY 설정
# -----------------------------
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key 입력", type="password")

if not api_key:
    st.warning("⚠ Gemini API Key를 입력해주세요.")
    st.stop()

genai.configure(api_key=api_key)

# -----------------------------
# 모델 설정 (안정 모델)
# -----------------------------
try:
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error(f"모델 초기화 실패: {e}")
    st.stop()

# -----------------------------
# 이미지 업로드
# -----------------------------
uploaded_file = st.file_uploader(
    "이미지를 업로드하세요",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_container_width=True)

    # Gemini에 전달할 이미지 포맷 변환
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_bytes = img_byte_arr.getvalue()

    st.write("---")
    col1, col2 = st.columns(2)

    # -----------------------------
    # SDXL 프롬프트 추출
    # -----------------------------
    with col1:
        if st.button("🚀 SDXL 프롬프트 추출"):
            with st.spinner("SDXL 스타일 분석 중..."):
                try:
                    response = model.generate_content(
                        [
                            "Analyze this image for SDXL. "
                            "Output descriptive keywords separated by commas. "
                            "English only.",
                            {"mime_type": "image/png", "data": img_bytes},
                        ]
                    )
                    st.subheader("SDXL Prompt")
                    st.code(response.text)
                except Exception as e:
                    st.error(f"에러 발생: {e}")

    # -----------------------------
    # Grok 프롬프트 추출
    # -----------------------------
    with col2:
        if st.button("🧠 Grok 프롬프트 추출"):
            with st.spinner("Grok 스타일 분석 중..."):
                try:
                    response = model.generate_content(
                        [
                            "Analyze this image for Grok AI. "
                            "Use descriptive natural language. "
                            "English only.",
                            {"mime_type": "image/png", "data": img_bytes},
                        ]
                    )
                    st.subheader("Grok Prompt")
                    st.code(response.text)
                except Exception as e:
                    st.error(f"에러 발생: {e}")
