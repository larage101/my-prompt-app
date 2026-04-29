import streamlit as st
from PIL import Image
import io
import requests
import base64

# ============================================================
# 기본 설정
# ============================================================
st.set_page_config(page_title="프롬추출", layout="centered")

st.markdown("""
<h1 style="text-align:center; color:#ffccff;">💗 프롬추출 ✨</h1>
""", unsafe_allow_html=True)

# ============================================================
# 🔐 API 키 (세션 저장)
# ============================================================
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

with st.expander("🔐 API 설정", expanded=True):
    api_input = st.text_input("OpenRouter API Key", type="password")

    if st.button("저장"):
        st.session_state.api_key = api_input
        st.success("세션 저장 완료 (새로고침 시 초기화)")

api_key = st.session_state.get("api_key")

if not api_key:
    st.warning("API 키 입력 필요")
    st.stop()

# ============================================================
# 🤖 모델 선택
# ============================================================
model_option = st.selectbox(
    "🤖 모델 선택",
    [
        "llava-hf/llava-1.5-7b-hf (가성비)",
        "qwen/qwen-vl-chat (고성능)",
        "openai/gpt-4o-mini (텍스트)"
    ]
)

# 모델 매핑
if "llava" in model_option:
    model_name = "llava-hf/llava-1.5-7b-hf"
elif "qwen" in model_option:
    model_name = "qwen/qwen-vl-chat"
else:
    model_name = "openai/gpt-4o-mini"

st.success(f"선택된 모델: {model_name}")

# ============================================================
# 이미지 업로드
# ============================================================
uploaded_file = st.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)

    # 리사이즈
    image.thumbnail((1024, 1024), Image.LANCZOS)
    st.image(image, caption="최적화된 이미지")

    # base64 변환
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    img_b64 = base64.b64encode(buffer.getvalue()).decode()

    # ========================================================
    # 🎨 스타일 선택
    # ========================================================
    style_mode = st.radio(
        "🎨 스타일",
        ["애니", "반실사", "실사", "초고화질"],
        horizontal=True
    )

    base_prompt = "Analyze image and generate SDXL prompt."

    if style_mode == "애니":
        style_prompt = "anime style, clean lineart, vibrant colors"
    elif style_mode == "반실사":
        style_prompt = "semi realistic, soft shading"
    elif style_mode == "실사":
        style_prompt = "photorealistic, DSLR lighting"
    else:
        style_prompt = "ultra realistic 8k RAW, skin detail"

    # ========================================================
    # 🔥 프롬프트 생성
    # ========================================================
    if st.button("🔥 생성"):
        with st.spinner("분석 중..."):

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            # 🔥 모델별 최적화
            if "gpt-4o-mini" in model_name:
                # 텍스트 fallback (이미지 없이)
                messages = [
                    {
                        "role": "user",
                        "content": f"{base_prompt} {style_prompt}"
                    }
                ]
            else:
                # 이미지 포함
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"{base_prompt} {style_prompt}"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_b64}"
                                }
                            }
                        ]
                    }
                ]

            payload = {
                "model": model_name,
                "messages": messages
            }

            try:
                res = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60
                )

                result = res.json()

                if "choices" in result:
                    output_text = result["choices"][0]["message"]["content"]

                    st.code(output_text)
                    st.download_button("📋 다운로드", output_text, "prompt.txt")
                else:
                    st.error(result)

            except Exception as e:
                st.error(f"에러: {e}")
