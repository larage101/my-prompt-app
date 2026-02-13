import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import pkg_resources

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(page_title="SDXL & Grok Prompt Extractor PRO", layout="centered")
st.title("📸 SDXL & Grok 프롬프트 추출기v1")

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
# 모델 고정
# -----------------------------
MODEL_NAME = "models/gemini-2.5-flash"
model = genai.GenerativeModel(MODEL_NAME)

st.success(f"현재 사용 모델: {MODEL_NAME}")

# -----------------------------
# 🎛 Generation 옵션
# -----------------------------
st.sidebar.header("🎛 프롬프트 강도 설정")

temperature = st.sidebar.slider("Temperature (창의성)", 0.0, 1.5, 0.7, 0.1)
top_p = st.sidebar.slider("Top-P (확률 다양성)", 0.1, 1.0, 0.9, 0.05)
top_k = st.sidebar.slider("Top-K (단어 후보 범위)", 1, 100, 40, 1)
max_tokens = st.sidebar.slider("Max Output Tokens (길이)", 100, 2048, 800, 50)

generation_config = {
    "temperature": temperature,
    "top_p": top_p,
    "top_k": top_k,
    "max_output_tokens": max_tokens,
}

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

    st.write("---")
    col1, col2 = st.columns(2)

    # ============================================================
    # 🚀 SDXL 프롬프트 + 네거티브 자동 생성
    # ============================================================
    with col1:
        if st.button("🚀 SDXL 프롬프트 생성"):
            with st.spinner("SDXL 분석 중..."):
                try:
                    response = model.generate_content(
                        [
                            {
                                "role": "user",
                                "parts": [
                                    "Analyze this image for SDXL image generation.\n"
                                    "1. Generate a highly detailed positive prompt using comma-separated keywords.\n"
                                    "2. Generate a professional SDXL negative prompt.\n"
                                    "Format:\n"
                                    "Positive Prompt:\n"
                                    "...\n\n"
                                    "Negative Prompt:\n"
                                    "...",
                                    {"mime_type": "image/png", "data": img_bytes},
                                ],
                            }
                        ],
                        generation_config=generation_config
                    )

                    output_text = response.text

                    st.subheader("🎨 SDXL Prompt Result")
                    st.code(output_text)

                    # 📋 복사 버튼
                    st.download_button(
                        label="📋 프롬프트 복사 (txt 다운로드)",
                        data=output_text,
                        file_name="sdxl_prompt.txt",
                        mime="text/plain"
                    )

                    # 🎯 토큰 사용량
                    if hasattr(response, "usage_metadata"):
                        usage = response.usage_metadata
                        st.info(
                            f"Prompt Tokens: {usage.prompt_token_count} | "
                            f"Output Tokens: {usage.candidates_token_count} | "
                            f"Total: {usage.total_token_count}"
                        )

                except Exception as e:
                    st.error(f"에러 발생: {e}")

    # ============================================================
    # 🧠 Grok 프롬프트 생성
    # ============================================================
    with col2:
        if st.button("🧠 Grok 프롬프트 생성"):
            with st.spinner("Grok 스타일 분석 중..."):
                try:
                    response = model.generate_content(
                        [
                            {
                                "role": "user",
                                "parts": [
                                    "Analyze this image and describe it in vivid, expressive natural English.\n"
                                    "Make it emotional, descriptive, and conversational.\n"
                                    "No bullet points.",
                                    {"mime_type": "image/png", "data": img_bytes},
                                ],
                            }
                        ],
                        generation_config=generation_config
                    )

                    output_text = response.text

                    st.subheader("💬 Grok Prompt")
                    st.code(output_text)

                    # 📋 복사 버튼
                    st.download_button(
                        label="📋 프롬프트 복사 (txt 다운로드)",
                        data=output_text,
                        file_name="grok_prompt.txt",
                        mime="text/plain"
                    )

                    # 🎯 토큰 사용량
                    if hasattr(response, "usage_metadata"):
                        usage = response.usage_metadata
                        st.info(
                            f"Prompt Tokens: {usage.prompt_token_count} | "
                            f"Output Tokens: {usage.candidates_token_count} | "
                            f"Total: {usage.total_token_count}"
                        )

                except Exception as e:
                    st.error(f"에러 발생: {e}")
