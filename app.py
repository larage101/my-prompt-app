import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# ============================================================
# 기본 설정
# ============================================================
st.set_page_config(page_title="프롬추출", layout="centered")

# CSS 디자인은 그대로 유지 (생략)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;700&display=swap');
html, body, [class*="css"] {
    background: linear-gradient(135deg, #1a001f, #2b0033, #3b004f);
    color: #f8e6ff;
    font-family: 'Poppins', sans-serif;
}
.block-container { padding-top: 1rem; }
.simple-title {
    text-align: center; font-size: 26px; font-weight: 700; color: #ffccff;
    text-shadow: 0 0 15px #ff66ff; margin-bottom: 15px;
}
section.main > div {
    background: rgba(255, 255, 255, 0.05); padding: 20px;
    border-radius: 18px; border: 1px solid rgba(255, 150, 255, 0.3);
    backdrop-filter: blur(10px);
}
.stButton>button {
    background: linear-gradient(135deg, #ff66cc, #cc33ff);
    color: white; border: none; border-radius: 20px; padding: 10px 20px;
    font-weight: 600; transition: 0.3s;
}
.stButton>button:hover { box-shadow: 0 0 20px #ff66ff; transform: scale(1.05); }
.stCodeBlock { background-color: rgba(255, 255, 255, 0.08) !important; color: #ffe6ff !important; border-radius: 12px; }
</style>
<h1 class="simple-title">💗 프롬추출 ✨</h1>
""", unsafe_allow_html=True)

# ============================================================
# API KEY 설정
# ============================================================
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key 입력", type="password")

if not api_key:
    st.warning("API 키를 입력해주세요.")
    st.stop()

genai.configure(api_key=api_key)

# ============================================================
# 모델 설정 (공식 지원 명칭인 2.0-flash로 수정)
# ============================================================
MODEL_NAME = "models/gemini-2.0-flash"
model = genai.GenerativeModel(MODEL_NAME)
st.success(f"현재 모델: {MODEL_NAME}")

# ============================================================
# 이미지 업로드 및 리사이징 로직
# ============================================================
# 갤러리 업로드와 카메라 촬영 두 가지 옵션을 모두 제공합니다.
uploaded_file = st.file_uploader("이미지를 업로드하거나 촬영하세요", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # 1. 이미지 열기
    image = Image.open(uploaded_file)
    
    # 2. 리사이징 (모바일 고화질 사진 대응)
    # 가로 1024px 기준으로 비율 맞춰 축소 (속도와 용량 최적화)
    max_size = 1024
    if image.width > max_size or image.height > max_size:
        image.thumbnail((max_size, max_size), Image.LANCZOS)
    
    st.image(image, caption="최적화된 이미지", use_container_width=True)

    # 3. 분석용 바이트 변환 (JPEG 압축으로 전송 속도 향상)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="JPEG", quality=85)
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

    # 🔥 SDXL 분석
    with col1:
        if st.button("🔥 SDXL"):
            if style_mode == "🎨 애니":
                style_instruction = "Analyze for anime-style SDXL. Focus on clean lineart, cel shading, vibrant colors."
                config = {"temperature": 0.55, "top_p": 0.95, "top_k": 40, "max_output_tokens": 1100}
            elif style_mode == "✨ 반실사":
                style_instruction = "Analyze for semi-realistic illustration. Balanced realism and stylization, soft shading."
                config = {"temperature": 0.45, "top_p": 0.92, "top_k": 35, "max_output_tokens": 1000}
            elif style_mode == "📷 실사":
                style_instruction = "Analyze for photorealistic SDXL. Realistic anatomy, natural lighting, DSLR lens detail."
                config = {"temperature": 0.35, "top_p": 0.9, "top_k": 30, "max_output_tokens": 900}
            else:
                style_instruction = "Analyze for ultra high-resolution photorealistic SDXL. Ultra detailed skin pores, cinematic RAW photo, 8k."
                config = {"temperature": 0.3, "top_p": 0.88, "top_k": 25, "max_output_tokens": 1200}

            with st.spinner("SDXL 분석 중..."):
                try:
                    response = model.generate_content([
                        style_instruction + "\nGenerate:\n1. Positive Prompt (comma-separated)\n2. Negative Prompt\n\nFormat:\nPositive Prompt:\n...\n\nNegative Prompt:\n...",
                        {"mime_type": "image/jpeg", "data": img_bytes}
                    ], generation_config=config)
                    
                    output_text = response.text
                    st.code(output_text)
                    st.download_button("📋 다운로드", output_text, "sdxl_prompt.txt")
                except Exception as e:
                    st.error(f"분석 중 에러가 발생했습니다: {e}")

    # 💋 GROK 감성 분석
    with col2:
        if st.button("💋 GROK"):
            config = {"temperature": 0.9, "top_p": 0.95, "top_k": 50, "max_output_tokens": 1300}
            with st.spinner("Grok 감성 추출 중..."):
                try:
                    response = model.generate_content([
                        "Describe this image in vivid, emotional, expressive English.",
                        {"mime_type": "image/jpeg", "data": img_bytes}
                    ], generation_config=config)
                    
                    output_text = response.text
                    st.code(output_text)
                    st.download_button("📋 다운로드", output_text, "grok_prompt.txt")
                except Exception as e:
                    st.error(f"분석 중 에러가 발생했습니다: {e}")
