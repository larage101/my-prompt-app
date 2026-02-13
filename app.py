import streamlit as st
import subprocess
import sys
from PIL import Image

# [필독] 라이브러리 설치 에러 방지를 위한 강제 로드 로직
try:
    import google.generative_ai as genai
except ImportError:
    # 실행 중 라이브러리가 없으면 즉시 설치 시도
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generative-ai"])
    import google.generative_ai as genai

# 1. 페이지 기본 설정
st.set_page_config(page_title="나만의 프롬프트 추출기", layout="centered", page_icon="📸")

st.title("📸 Image to Prompt")
st.write("이미지를 업로드하면 AI 이미지 생성용 프롬프트를 추출합니다.")

# 2. API 키 불러오기 (시크리트 우선 -> 사이드바 직접 입력)
api_key = None

# Streamlit Secrets 확인
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    # 시크리트에 없을 경우 사이드바에서 입력받음
    with st.sidebar:
        st.header("설정")
        api_key = st.text_input("Gemini API Key 입력", type="password")
        st.info("Google AI Studio에서 발급받은 키를 넣어주세요.")

# 3. 메인 기능
if api_key:
    try:
        genai.configure(api_key=api_key)
        # 이미지 인식 전용 모델 설정
        model = genai.GenerativeModel('gemini-1.5-flash')

        uploaded_file = st.file_uploader("사진을 선택하거나 촬영하세요.", type=['png', 'jpg', 'jpeg'])

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption='업로드된 이미지', use_container_width=True)
            
            if st.button('✨ 프롬프트 추출하기'):
                with st.spinner('AI가 이미지를 분석 중입니다...'):
                    # AI에게 줄 세부 요청사항 (프롬프트 엔지니어링)
                    prompt_instruction = """
                    Analyze this image and generate a high-quality prompt for AI image generators like Midjourney or Stable Diffusion. 
                    Include details about the subject, artistic style, lighting, camera angle, and color palette. 
                    Please provide the output as a single paragraph in English.
                    """
                    
                    response = model.generate_content([prompt_instruction, image])
                    
                    st.success('분석 완료!')
                    st.subheader("추출된 프롬프트")
                    st.code(response.text)
                    st.button("다시 하기", on_click=lambda: st.rerun())

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
else:
    st.warning("API 키가 필요합니다. 사이드바에 입력하거나 Streamlit Secrets에 설정해 주세요.")

# 하단 정보
st.markdown("---")
st.caption("Gemini 1.5 Flash 모델을 사용하여 실시간으로 분석합니다.")
