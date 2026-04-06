import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# ============================================================
# 페이지 기본 설정
# ============================================================
st.set_page_config(page_title="프롬추출", layout="centered")

# CSS 디자인 (기존과 동일)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght=500;700&display=swap');
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
# 무료 모델 선택 (2026년 4월 기준 추천)
# ============================================================
st.subheader("🛠️ 사용할 모델 선택 (무료 티어 추천)")

model_options = {
    "Gemini 2.5 Flash (추천 - 균형 좋음)": "gemini-2.5-flash",
    "Gemini 2.5 Flash-Lite (가장 가벼움, 429 에러 적음)": "gemini-2.5-flash-lite",
    "Gemini 2.5 Pro (고성능, 쿼터 빨리 소모)": "gemini-2.5-pro",
    "Gemini 2.0 Flash-001 (기존, 2026년 6월 종료 예정)": "gemini-2.0-flash-001"
}

selected_model_display = st.selectbox(
    "모델을 선택하세요",
    options=list(model_options.keys()),
    index=0  # 기본: 2.5 Flash
)

MODEL_NAME = model_options[selected_model_display]

# 모델 생성
model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    generation_config={
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 1200,
    }
)

st.success(f"✅ 현재 선택된 모델: **{selected_model_display}** ({MODEL_NAME})")

# ============================================================
# 이미지 업로드 및 처리
# ============================================================
uploaded_file = st.file_uploader("이미지를 업로드하거나 촬영하세요", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    
    # 이미지 리사이징 (1024px 이하로 최적화)
    max_size = 1024
    if image.width > max_size or image.height > max_size:
        image.thumbnail((max_size, max_size), Image.LANCZOS)
    
    st.image(image, caption="최적화된 이미지", use_container_width=True)

    # JPEG 압축으로 변환
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="JPEG", quality=85)
    img_bytes = img_byte_arr.getvalue()

    # ============================================================
    # 스타일 선택
    # ============================================================
    style_mode = st.radio(
        "🎨 스타일 선택",
        ["🎨 애니", "✨ 반실사", "📷 실사", "💎 초고화질 실사"],
        horizontal=True
    )

    st.write("---")
    col1, col2 = st.columns(2)

    # ====================== SDXL 분석 ======================
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

            with st.spinner("SDXL 프롬프트 분석 중..."):
                try:
                    response = model.generate_content([
                        style_instruction + "\nGenerate:\n1. Positive Prompt (comma-separated)\n2. Negative Prompt\n\nFormat:\nPositive Prompt:\n...\n\nNegative Prompt:\n...",
                        {"mime_type": "image/jpeg", "data": img_bytes}
                    ], generation_config=config)
                    
                    output_text = response.text
                    st.code(output_text, language="markdown")
                    st.download_button("📋 SDXL 프롬프트 다운로드", output_text, "sdxl_prompt.txt")
                except Exception as e:
                    error_msg = str(e).lower()
                    if "429" in error_msg or "quota" in error_msg or "exhausted" in error_msg:
                        st.error("❌ API 쿼터를 초과했습니다.\n\n"
                                 "💡 해결 방법:\n"
                                 "1. 더 가벼운 모델(Gemini 2.5 Flash-Lite)로 변경\n"
                                 "2. Google Cloud에서 Billing 계정 연결\n"
                                 "3. 잠시 후 다시 시도")
                    else:
                        st.error(f"에러 발생: {e}")

    # ====================== GROK 감성 분석 ======================
    with col2:
        if st.button("💋 GROK"):
            config = {"temperature": 0.9, "top_p": 0.95, "top_k": 50, "max_output_tokens": 1300}
            with st.spinner("Grok 감성 프롬프트 추출 중..."):
                try:
                    response = model.generate_content([
                        "Describe this image in vivid, emotional, expressive English. Focus on atmosphere, mood, lighting, and artistic details.",
                        {"mime_type": "image/jpeg", "data": img_bytes}
                    ], generation_config=config)
                    
                    output_text = response.text
                    st.code(output_text, language="markdown")
                    st.download_button("📋 GROK 프롬프트 다운로드", output_text, "grok_prompt.txt")
                except Exception as e:
                    error_msg = str(e).lower()
                    if "429" in error_msg or "quota" in error_msg or "exhausted" in error_msg:
                        st.error("❌ API 쿼터를 초과했습니다.\n\n"
                                 "💡 해결 방법:\n"
                                 "1. 더 가벼운 모델(Gemini 2.5 Flash-Lite)로 변경\n"
                                 "2. Billing 계정 연결 후 쿼터 증가\n"
                                 "3. 잠시 기다린 후 다시 시도")
                    else:
                        st.error(f"에러 발생: {e}")
