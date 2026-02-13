import streamlit as st
import google.generative_ai as genai
from PIL import Image

# 1. 페이지 설정
st.set_page_config(page_title="Image to Prompt", layout="centered")
st.title("📸 Image to Prompt")

# 2. API 키 가져오기 (Secrets 우선, 없으면 사이드바)
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        uploaded_file = st.file_uploader("이미지를 선택하세요", type=['png', 'jpg', 'jpeg'])

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)
            
            if st.button('✨ 프롬프트 추출'):
                with st.spinner('분석 중...'):
                    response = model.generate_content([
                        "Describe this image for an AI image generator prompt. Style, lighting, composition in English.",
                        image
                    ])
                    st.subheader("결과:")
                    st.code(response.text)
    except Exception as e:
        st.error(f"에러 발생: {e}")
else:
    st.warning("API 키를 설정해주세요.")
