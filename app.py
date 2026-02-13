import streamlit as st
import google.generative_ai as genai
from PIL import Image

# 1. 페이지 설정
st.set_page_config(page_title="Prompt Extractor", layout="centered")
st.title("📸 Image to Prompt")
st.write("이미지를 올리면 AI 프롬프트를 만들어줍니다.")

# 2. API 키 설정 (보안을 위해 사이드바에서 입력받거나 환경변수 사용)
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # 3. 파일 업로더
    uploaded_file = st.file_uploader("이미지 선택", type=['png', 'jpg', 'jpeg'])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='업로드 완료', use_container_width=True)
        
        if st.button('✨ 프롬프트 추출 시작'):
            with st.spinner('AI가 분석 중입니다...'):
                # AI에게 전달할 상세 지침
                instruction = "Analyze this image and provide a detailed prompt for AI image generation (like Midjourney or Stable Diffusion). Focus on style, lighting, composition, and subject. Output should be in English."
                response = model.generate_content([instruction, image])
                
                st.subheader("추출된 프롬프트:")
                st.code(response.text)
                st.info("위 코드를 복사해서 이미지 생성 AI에 사용하세요.")
else:
    st.warning("왼쪽 사이드바에 API 키를 입력해주세요.")
