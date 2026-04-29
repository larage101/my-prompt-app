import streamlit as st
from PIL import Image
import io
import requests
import base64
import streamlit.components.v1 as components

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
# 복사 버튼 함수
# ============================================================
def copy_button(text, label="복사"):
    safe_text = text.replace("`", "\\`")
    components.html(f"""
        <button onclick="navigator.clipboard.writeText(`{safe_text}`)">
            📋 {label}
        </button>
    """, height=40)

# ============================================================
# 이미지 업로드
# ============================================================
uploaded_file = st.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)

    image.thumbnail((1024, 1024), Image.LANCZOS)
    st.image(image, caption="최적화된 이미지")

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    img_b64 = base64.b64encode(buffer.getvalue()).decode()

    # ========================================================
    # 선택 옵션
    # ========================================================
    person_type = st.selectbox("👤 인물", ["없음", "성인 여성", "성인 남성", "아이"])
    background = st.selectbox("🌍 배경", ["실내", "야외", "봄", "여름", "가을", "겨울", "낮", "밤"])
    mood = st.selectbox("🎭 분위기", ["자연광", "시네마틱", "부드러운", "강한 대비", "몽환적"])

    style_mode = st.radio("🎨 스타일", ["애니", "반실사", "실사", "초고화질"], horizontal=True)

    if style_mode == "애니":
        style_prompt = "anime style, clean lineart, vibrant colors"
    elif style_mode == "반실사":
        style_prompt = "semi realistic, soft shading"
    elif style_mode == "실사":
        style_prompt = "photorealistic, DSLR lighting"
    else:
        style_prompt = "ultra realistic 8k RAW, skin detail"

    # ========================================================
    # 프롬프트
    # ========================================================
    base_prompt = f"""
    Analyze this image in detail and create a high-quality Stable Diffusion (SDXL) prompt.

    Context:
    - Person: {person_type}
    - Background: {background}
    - Mood: {mood}
    - Style: {style_prompt}

    Return ONLY in this format:

    Positive Prompt:
    ...

    Negative Prompt:
    ...
    """

    # ========================================================
    # 실행
    # ========================================================
    if st.button("🔥 생성"):
        with st.spinner("분석 중..."):

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": base_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_b64}"
                                }
                            }
                        ]
                    }
                ]
            }

            try:
                res = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=90
                )

                result = res.json()

                if "choices" in result:
                    output_text = result["choices"][0]["message"]["content"]

                    # ====================================================
                    # 프롬프트 분리
                    # ====================================================
                    pos, neg = "", ""

                    if "Positive Prompt:" in output_text:
                        pos = output_text.split("Positive Prompt:")[1].split("Negative Prompt:")[0].strip()

                    if "Negative Prompt:" in output_text:
                        neg = output_text.split("Negative Prompt:")[1].strip()

                    # ====================================================
                    # 출력 UI
                    # ====================================================
                    st.subheader("✅ Positive Prompt")
                    st.code(pos)
                    copy_button(pos, "Positive 복사")

                    st.subheader("🚫 Negative Prompt")
                    st.code(neg)
                    copy_button(neg, "Negative 복사")

                    st.download_button("📋 전체 다운로드", output_text, "prompt.txt")

                else:
                    st.error(result)

            except Exception as e:
                st.error(f"에러: {e}")
Positive Prompt:
...

Negative Prompt:
...
"""

    # ========================================================
    # 🔥 프롬프트 생성
    # ========================================================
    if st.button("🔥 생성"):
        with st.spinner("분석 중... (무료라 느릴 수 있음)"):

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            # ✅ 1순위: Nemotron (무료 멀티모달)
            payload = {
                "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": base_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_b64}"
                                }
                            }
                        ]
                    }
                ]
            }

            try:
                res = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=90
                )

                result = res.json()

                # ====================================================
                # ✅ 정상 응답
                # ====================================================
                if "choices" in result:
                    output_text = result["choices"][0]["message"]["content"]

                    st.code(output_text)
                    st.download_button("📋 다운로드", output_text, "prompt.txt")

                # ====================================================
                # ⚠️ 실패 → fallback (텍스트 모델)
                # ====================================================
                else:
                    st.warning("무료 모델 실패 → fallback 실행")

                    fallback_payload = {
                        "model": "openai/gpt-4o-mini",
                        "messages": [
                            {
                                "role": "user",
                                "content": base_prompt
                            }
                        ]
                    }

                    res2 = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=fallback_payload,
                        timeout=60
                    )

                    result2 = res2.json()

                    if "choices" in result2:
                        output_text = result2["choices"][0]["message"]["content"]
                        st.code(output_text)
                    else:
                        st.error(result2)

            except Exception as e:
                st.error(f"에러: {e}")
