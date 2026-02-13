import streamlit as st
import google.generative_ai as genai
from PIL import Image
import os

# 페이지 설정
st.set_page_config(page_title="Prompt Extractor", layout="centered")

st.title("📸 나만의 프롬프트 추출기")

# API 키 설정 (직접 입력 방식)
# 주의: 보안을 원하시면 15번째 줄 주석을 해제하고 16번째 줄을 지우세요.
api_key = st.sidebar.text_input("Gemini API Key", type="password")
# api_key = "여기에_본인의_API_키를_직접_넣으셔도_됩니다"

if api_key:
    try:
        genai.configure(api_key=api_key)
        # 모델 설정 (가장 빠르고 가벼운 모델)
        model = genai.GenerativeModel('gemini-1.5-flash')

        uploaded_file = st.file_uploader("이미지를 업로드하세요", type=['png', 'jpg', 'jpeg'])

        if uploaded_file:
            img = Image.open(uploaded_file)
            st.image(img, caption='선택한 이미지', use_container_width=True)
            
            if st.button('프롬프트 추출하기 ✨'):
                with st.spinner('AI가 이미지를 분석하고 있습니다...'):
                    # 이미지 분석 요청
                    response = model.generate_content([
                        "Describe this image in detail for an AI image generator prompt. Include style, lighting, and composition. English please.",
                        img
                    ])
                    
                    st.success("완료!")
                    st.subheader("추출된 프롬프트")
                    st.code(response.text)
                    
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
else:
    st.info("사이드바에 Google API 키를 입력해 주세요.")
