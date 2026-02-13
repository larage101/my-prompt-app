import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import pkg_resources

# ============================================================
# 🕯 기본 설정
# ============================================================
st.set_page_config(page_title="Abyssal Prompt Sanctum", layout="centered")

# ============================================================
# 🖤 다크 판타지 UI
# ============================================================
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&family=Poppins:wght@400;600&display=swap');

/* 전체 배경 */
html, body, [class*="css"] {
    background: linear-gradient(135deg, #1a001f, #2d0036, #3b004f);
    color: #f8e6ff;
    font-family: 'Poppins', sans-serif;
}

/* 상단 여백 조정 */
.block-container {
    padding-top: 1.2rem;
}

/* 타이틀 (줄바꿈 허용 + 잘림 방지) */
.eroge-title {
    text-align: center;
    font-family: 'Playfair Display', serif;
    font-size: 28px;
    font-weight: 600;
    color: #ffccff;
    white-space: normal;
    word-break: keep-all;
    text-shadow: 
        0 0 10px #ff66ff,
        0 0 20px #cc00ff;
    margin-bottom: 20px;
}

/* 카드 스타일 */
section.main > div {
    background: rgba(255, 255, 255, 0.05);
    padding: 20px;
    border-radius: 18px;
    border: 1px solid rgba(255, 150, 255, 0.3);
    backdrop-filter: blur(12px);
}

/* 버튼 */
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
    background: linear-gradient(135deg, #ff99ff, #dd55ff);
    box-shadow: 0 0 20px #ff66ff;
    transform: scale(1.05);
}

/* 슬라이더 색감 */
.stSlider label {
    color: #ffccff;
}

/* 코드 블록 */
.stCodeBlock {
    background-color: rgba(255, 255, 255, 0.08) !important;
    color: #ffe6ff !important;
    border-radius: 12px;
    border: 1px solid rgba(255, 150, 255, 0.4);
}

/* 성공 메시지 */
.stSuccess {
    background-color: rgba(255, 100, 255, 0.1) !important;
    border: 1px solid #ff66ff;
    color: #ffd6ff !important;
}

/* 모바일 대응 */
@media (max-width: 768px) {
    .eroge-title {
        font-size: 20px;
    }
}

</style>

<h1 class="eroge-title">
💗 SDXL & Grok Magical Prompt Atelier ✨
</h1>
""", unsafe_allow_html=True)

st.write("SDK version:", pkg_resources.get_distribution("google-generativeai").version)

# ============================================================
# 🔑 API KEY
# ============================================================
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key 입력", type="password")

if not api_key:
    st.warning("⚠ Gemini API Key를 입력해주세요.")
    st.stop()

genai.configure(api_key=api_key)

# ============================================================
# 🔥 모델 고정
# ============================================================
MODEL_NAME = "models/gemini-2.5-flash"
model = genai.GenerativeModel(MODEL_NAME)

st.success(f"현재 사용 모델: {MODEL_NAME}")

# ============================================================
# 🎛 Generation 설정
# ============================================================
st.sidebar.header("🎛 Arcane Generation Controls")

temperature = st.sidebar.slider("Temperature", 0.0, 1.5, 0.7, 0.1)
top_p = st.sidebar.slider("Top-P", 0.1, 1.0, 0.9, 0.05)
top_k = st.sidebar.slider("Top-K", 1, 100, 40, 1)
max_tokens = st.sidebar.slider("Max Output Tokens", 100, 2048, 800, 50)

generation_config = {
    "temperature": temperature,
    "top_p": top_p,
    "top_k": top_k,
    "max_output_tokens": max_tokens,
}

# ============================================================
# 🖼 이미지 업로드
# ============================================================
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

    # ========================================================
    # 🎨 SDXL
    # ========================================================
    with col1:
        if st.button("🔥 SDXL Ritual"):
            with st.spinner("Invoking SDXL Spirits..."):
                try:
                    response = model.generate_content(
                        [{
                            "role": "user",
                            "parts": [
                                "Analyze this image for SDXL.\n"
                                "Generate:\n"
                                "1. Positive Prompt (comma-separated, highly detailed)\n"
                                "2. Professional Negative Prompt\n\n"
                                "Format:\n"
                                "Positive Prompt:\n...\n\nNegative Prompt:\n...",
                                {"mime_type": "image/png", "data": img_bytes},
                            ],
                        }],
                        generation_config=generation_config
                    )

                    output_text = response.text
                    st.subheader("🕯 SDXL Incantation")
                    st.code(output_text)

                    st.download_button(
                        "📋 Download Prompt",
                        output_text,
                        file_name="sdxl_prompt.txt"
                    )

                    if hasattr(response, "usage_metadata"):
                        usage = response.usage_metadata
                        st.info(
                            f"Prompt: {usage.prompt_token_count} | "
                            f"Output: {usage.candidates_token_count} | "
                            f"Total: {usage.total_token_count}"
                        )

                except Exception as e:
                    st.error(f"에러 발생: {e}")

    # ========================================================
    # 🧠 GROK
    # ========================================================
    with col2:
        if st.button("🩸 Grok Invocation"):
            with st.spinner("Summoning Grok Essence..."):
                try:
                    response = model.generate_content(
                        [{
                            "role": "user",
                            "parts": [
                                "Describe this image in vivid, emotional, natural English.\n"
                                "Make it immersive and expressive.",
                                {"mime_type": "image/png", "data": img_bytes},
                            ],
                        }],
                        generation_config=generation_config
                    )

                    output_text = response.text
                    st.subheader("🔮 Grok Manifestation")
                    st.code(output_text)

                    st.download_button(
                        "📋 Download Prompt",
                        output_text,
                        file_name="grok_prompt.txt"
                    )

                    if hasattr(response, "usage_metadata"):
                        usage = response.usage_metadata
                        st.info(
                            f"Prompt: {usage.prompt_token_count} | "
                            f"Output: {usage.candidates_token_count} | "
                            f"Total: {usage.total_token_count}"
                        )

                except Exception as e:
                    st.error(f"에러 발생: {e}")
