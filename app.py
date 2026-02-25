import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# ============================================================
# 기본 설정
# ============================================================
st.set_page_config(page_title="프롬추출", layout="centered")

# ============================================================
# UI 디자인 (모바일 대응)
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;700&display=swap');

html, body, [class*="css"] {
    background: linear-gradient(135deg, #1a001f, #2b0033, #3b004f);
    color: #f8e6ff;
    font-family: 'Poppins', sans-serif;
}

.block-container {
    padding-top: 1rem;
}

.simple-title {
    text-align: center;
    font-size: 26px;
    font-weight: 700;
    color: #ffccff;
    white-space: normal;
    word-break: keep-all;
    text-shadow: 0 0 15px #ff66ff;
    margin-bottom: 15px;
}

section.main > div {
    background: rgba(255, 255, 255, 0.05);
    padding: 20px;
    border-radius: 18px;
    border: 1px solid rgba(255, 150, 255, 0.3);
    backdrop-filter: blur(10px);
}

.stButton>button {
    background: linear-gradient(135deg, #ff66cc, #cc33ff);
    color: white;
    border: none;
    border-radius: 20px;
    padding: 10px 20px;
    font-weight: 600;
    transition: 0.3s;
}

.stButton>button:hover {
    box-shadow: 0 0 20px #ff66ff;
    transform: scale(1.05);
}

.stCodeBlock {
    background-color: rgba(255, 255, 255, 0.08) !important;
    color: #ffe6ff !important;
    border-radius: 12px;
}
</style>

<h1 class="simple-title">💗 프롬추출 ✨</h1>
""", unsafe_allow_html=True)

# ============================================================
# SDK 확인
# ============================================================

# ============================================================
# API KEY
# ============================================================
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key 입력", type="password")

if not api_key:
    st.warning("API 키를 입력해주세요.")
    st.stop()

genai.configure(api_key=api_key)

# ============================================================
# 모델 고정
# ============================================================
MODEL_NAME = "models/gemini-2.5-flash"
model = genai.GenerativeModel(MODEL_NAME)
st.success(f"현재 모델: {MODEL_NAME}")

# ============================================================
# 이미지 업로드
# ============================================================
uploaded_file = st.file_uploader("이미지를 업로드하세요", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_container_width=True)

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_bytes = img_byte_arr.getvalue()

    # ========================================================
    # 🎨 스타일 선택
    # ========================================================
    style_mode = st.radio(
        "🎨 스타일 선택",
        ["🎨 애니", "✨ 반실사", "📷 실사", "💎 초고화질 실사"],
        horizontal=True
    )

    st.write("---")
    col1, col2 = st.columns(2)

    # ========================================================
    # 🔥 SDXL
    # ========================================================
    with col1:
        if st.button("🔥 SDXL"):

            if style_mode == "🎨 애니":
                style_instruction = (
                    "Analyze for anime-style SDXL. "
                    "Focus on clean lineart, cel shading, vibrant colors."
                )
                config = {"temperature": 0.55, "top_p": 0.95, "top_k": 40, "max_output_tokens": 1100}

            elif style_mode == "✨ 반실사":
                style_instruction = (
                    "Analyze for semi-realistic illustration. "
                    "Balanced realism and stylization, soft shading."
                )
                config = {"temperature": 0.45, "top_p": 0.92, "top_k": 35, "max_output_tokens": 1000}

            elif style_mode == "📷 실사":
                style_instruction = (
                    "Analyze for photorealistic SDXL. "
                    "Realistic anatomy, natural lighting, DSLR lens detail."
                )
                config = {"temperature": 0.35, "top_p": 0.9, "top_k": 30, "max_output_tokens": 900}

            else:
                style_instruction = (
                    "Analyze for ultra high-resolution photorealistic SDXL. "
                    "Ultra detailed skin pores, cinematic RAW photo, 8k."
                )
                config = {"temperature": 0.3, "top_p": 0.88, "top_k": 25, "max_output_tokens": 1200}

            with st.spinner("SDXL 분석 중..."):

                response = model.generate_content(
                    [{
                        "role": "user",
                        "parts": [
                            style_instruction +
                            "\nGenerate:\n"
                            "1. Positive Prompt (comma-separated)\n"
                            "2. Professional Negative Prompt\n\n"
                            "Format:\nPositive Prompt:\n...\n\nNegative Prompt:\n...",
                            {"mime_type": "image/png", "data": img_bytes},
                        ],
                    }],
                    generation_config=config
                )

                output_text = response.text
                st.code(output_text)

                st.download_button("📋 다운로드", output_text, "sdxl_prompt.txt")

                if hasattr(response, "usage_metadata"):
                    st.info(f"Total Tokens: {response.usage_metadata.total_token_count}")

    # ========================================================
    # 💋 GROK
    # ========================================================
    with col2:
        if st.button("💋 GROK"):

            config = {"temperature": 0.9, "top_p": 0.95, "top_k": 50, "max_output_tokens": 1300}

            with st.spinner("Grok 감성 추출 중..."):

                response = model.generate_content(
                    [{
                        "role": "user",
                        "parts": [
                            "Describe this image in vivid, emotional, expressive English.",
                            {"mime_type": "image/png", "data": img_bytes},
                        ],
                    }],
                    generation_config=config
                )

                output_text = response.text
                st.code(output_text)

                st.download_button("📋 다운로드", output_text, "grok_prompt.txt")

                if hasattr(response, "usage_metadata"):
                    st.info(f"Total Tokens: {response.usage_metadata.total_token_count}")
