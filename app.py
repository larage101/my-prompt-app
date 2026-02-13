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

@import url('https://fonts.googleapis.com/css2?family=Uncial+Antiqua&family=Cinzel:wght@400;700&display=swap');

html, body, [class*="css"]  {
    background: radial-gradient(circle at top, #1a0000 0%, #0b0b0b 60%);
    color: #e6e0d8;
    font-family: 'Cinzel', serif;
}

.block-container {
    padding-top: 1rem;
}

.dark-title {
    text-align: center;
    font-size: 32px;
    font-family: 'Uncial Antiqua', cursive;
    letter-spacing: 3px;
    color: #d4c5a2;
    text-shadow:
        0 0 8px #990000,
        0 0 20px #660000,
        0 0 40px #330000;
    margin-bottom: 25px;
}

section.main > div {
    background-color: rgba(20, 10, 10, 0.6);
    padding: 20px;
    border-radius: 10px;
    border: 1px solid #400000;
    box-shadow: 0 0 25px rgba(120, 0, 0, 0.3);
}

.stButton>button {
    background: linear-gradient(145deg, #220000, #330000);
    color: #f0e6d2;
    border: 1px solid #660000;
    border-radius: 6px;
    padding: 10px 18px;
    font-weight: bold;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    background: #550000;
    color: #ffffff;
    box-shadow: 0 0 15px #990000;
    border: 1px solid #aa0000;
}

.stCodeBlock {
    background-color: #120808 !important;
    color: #e6d8c3 !important;
    border: 1px solid #550000;
    border-radius: 6px;
}

</style>

<h1 class="dark-title">🕯 Abyssal Prompt Sanctum 🕯</h1>
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
