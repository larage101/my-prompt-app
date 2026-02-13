import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import pkg_resources

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(page_title="Gemini Vision Test", layout="centered")
st.title("📸 Gemini Vision Prompt Extractor")

st.write("SDK version:", pkg_resources.get_distribution("google-generativeai").version)

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
# 사용 가능한 모델 찾기
# -----------------------------
available_models = []

try:
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            available_models.append(m.name)

    if not available_models:
        st.error("사용 가능한 generateContent 모델이 없습니다.")
        st.stop()

    st.success("사용 가능한 모델:")
    for m in available_models:
        st.write(m)

    # 첫 번째 모델 자동 선택
    model_name = available_models[0]
    model = genai.GenerativeModel(model_name)
    st.info(f"현재 사용 모델: {model_name}")

except Exception as e:
    st.error(f"모델 목록 조회 실패: {e}")
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

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_bytes = img_byte_arr.getvalue()

    if st.button("🚀 이미지 분석"):
        with st.spinner("이미지 분석 중..."):
            try:
                response = model.generate_content(
                    [
                        {
                            "role": "user",
                            "parts": [
                                "Describe this image in detailed English.",
                                {"mime_type": "image/png", "data": img_bytes},
                            ],
                        }
                    ]
                )

                st.subheader("📌 분석 결과")
                st.write(response.text)

            except Exception as e:
                st.error(f"에러 발생: {e}")
