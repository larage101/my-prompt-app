import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="Custom Prompt Extractor", layout="centered")
st.title("📸 SDXL & Grok 전용 프롬프트 추출기")

api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # 모델 명칭을 models/ 경로를 포함하여 명확히 지정합니다.
        # 만약 1.5-flash가 계속 안 된다면 'gemini-1.5-pro'로 바꿔보세요.
        model = genai.GenerativeModel('gemini-2.0-flash')

        uploaded_file = st.file_uploader("이미지를 업로드하세요", type=['png', 'jpg', 'jpeg'])

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)
            
            st.write("---")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button('🚀 SDXL 프롬프트 추출'):
                    with st.spinner('SDXL 스타일 분석 중...'):
                        sdxl_instruction = "Analyze this image for SDXL. Output descriptive keywords separated by commas. English only."
                        # 안전한 호출을 위해 리스트 형태로 전달
                        response = model.generate_content([sdxl_instruction, image])
                        st.subheader("SDXL Prompt")
                        st.code(response.text)

            with col2:
                if st.button('🧠 Grok 프롬프트 추출'):
                    with st.spinner('Grok 스타일 분석 중...'):
                        grok_instruction = "Analyze this image for Grok AI. Use descriptive natural language. English only."
                        response = model.generate_content([grok_instruction, image])
                        st.subheader("Grok Prompt")
                        st.code(response.text)

    except Exception as e:
        # 404 에러 발생 시 다른 모델명을 시도해볼 수 있도록 안내
        st.error(f"에러 발생: {e}")
        st.info("팁: 만약 모델을 찾을 수 없다고 나오면 코드의 'models/gemini-1.5-flash' 부분을 'models/gemini-pro-vision'으로 바꿔보세요.")
else:
    st.warning("API 키를 설정해주세요.")
