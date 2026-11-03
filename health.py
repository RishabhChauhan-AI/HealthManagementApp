
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
import streamlit as st
import os
import io
import time


# ==========================================
# 1. STREAMLIT CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Health Management App",
    page_icon=":material/health_and_safety:",
    layout="wide"
)


# ==========================================
# 2. CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.stApp {
    background: #101714;
    color: #E8F5E9;
}

.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.main-title {
    font-size: 38px;
    font-weight: 800;
    color: #E8F5E9;
    margin-bottom: 5px;
}

.subtitle {
    color: #A5B5AA;
    font-size: 16px;
    line-height: 1.7;
    margin-bottom: 25px;
}

.section-title {
    color: #B5E7C1;
    font-size: 22px;
    font-weight: 700;
    margin-top: 15px;
    margin-bottom: 15px;
}

[data-testid="stFileUploader"] {
    background: #18231D;
    border: 1px dashed #4C8C68;
    border-radius: 15px;
    padding: 15px;
}

.stButton > button {
    background: linear-gradient(135deg, #3FA66B, #247B4B);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 20px;
    font-weight: 700;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background: #50B879;
    color: white;
    border: none;
}

.stTextInput input {
    background: #18231D;
    border: 1px solid #34483B;
    border-radius: 10px;
    color: white;
}

[data-testid="stImage"] {
    border-radius: 15px;
    overflow: hidden;
}

[data-testid="stAlert"] {
    border-radius: 12px;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: #18221C;
    border: 1px solid #304638;
    border-radius: 16px;
    padding: 15px;
}

.report-header {
    background: linear-gradient(120deg, #1B3B2A, #193027);
    border: 1px solid #38684B;
    border-radius: 18px;
    padding: 24px;
    margin-top: 20px;
    margin-bottom: 15px;
}

.report-header h2 {
    color: #E8F5E9;
    font-size: 27px;
    margin: 0;
}

.report-header p {
    color: #B5CEBB;
    margin-top: 8px;
    margin-bottom: 0;
}

.report-content h1 {
    color: #86D9A1;
    font-size: 26px;
    border-bottom: 1px solid #345441;
    padding-bottom: 10px;
}

.report-content h2 {
    color: #86D9A1;
    font-size: 21px;
    margin-top: 28px;
}

.report-content h3 {
    color: #B5E7C1;
    font-size: 18px;
}

.report-content p,
.report-content li {
    color: #D7E4DA;
    line-height: 1.8;
}

.report-content strong {
    color: #A4E8B5;
}

.report-content table {
    width: 100%;
    border-collapse: collapse;
}

.report-content th {
    background: #254D35;
    color: white;
    padding: 12px;
    text-align: left;
}

.report-content td {
    background: #1C2B22;
    color: #E0EBE3;
    padding: 12px;
    border-bottom: 1px solid #34483B;
}

.footer {
    text-align: center;
    color: #82958A;
    font-size: 13px;
    padding: 25px 0;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. API KEY CONFIGURATION
# ==========================================

load_dotenv()

api_key = os.getenv("GENAI_API_KEY")

try:
    if "GENAI_API_KEY" in st.secrets:
        api_key = st.secrets["GENAI_API_KEY"]
except Exception:
    pass

if not api_key:
    st.error(
        "Gemini API key not found. "
        "Check your .env or Streamlit Secrets."
    )
    st.stop()


# ==========================================
# 4. INITIALIZE GEMINI CLIENT
# ==========================================

@st.cache_resource
def load_model(key):
    return genai.Client(api_key=key)


client = load_model(api_key)


# Primary and backup models
AVAILABLE_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash"
]


# ==========================================
# 5. NUTRITION ANALYSIS PROMPT
# ==========================================

input_prompt = """
You are an expert nutritionist and food analysis assistant.

Analyze the uploaded food image carefully.

Your goal is to provide an informative, educational,
easy-to-understand nutritional report.

Do not invent ingredients or quantities that cannot be identified.
Clearly distinguish visible observations from assumptions.

Follow this exact Markdown structure:

# FOOD IDENTIFICATION

**Meal name:** Identify the dish.

**Description:** Briefly describe the visible food.

**Estimated serving size:** Give approximate total weight in grams.

# NUTRITION BREAKDOWN

Create a Markdown table:

| Food component | Estimated quantity | Calories | Protein | Carbs | Fat |
|---|---|---:|---:|---:|---:|

Include each identifiable component separately.

# TOTAL NUTRITION

Present estimated totals:

- **Calories:** kcal
- **Protein:** grams
- **Carbohydrates:** grams
- **Fat:** grams

Make sure totals approximately match the component breakdown.

# UNDERSTANDING YOUR MEAL

Explain in simple language:

1. Which component contributes the most calories?
2. Is the meal mainly protein-rich, carbohydrate-rich or fat-rich?
3. What does the protein content mean for muscle maintenance and growth?
4. What should someone know about carbohydrates and fats?
5. Is this a balanced meal? Explain why.

# NUTRITION INSIGHTS

Provide three useful observations.

Include practical suggestions for improving the nutritional balance
without unnecessarily changing the dish.

# ESTIMATION NOTES

Explain:

- Assumed portion sizes.
- Ingredients that are uncertain.
- How cooking oil, butter and sauces affect estimates.
- Confidence level: Low, Medium or High.

# IMPORTANT DISCLAIMER

All values are visual estimates, not laboratory measurements.
Actual nutrition depends on ingredients, preparation and portion sizes.
This analysis is for educational purposes and is not medical advice.

FORMATTING RULES:

- Use clear Markdown headings.
- Use tables wherever appropriate.
- Use bold text for important nutritional values.
- Keep explanations simple but informative.
- Avoid unnecessarily long paragraphs.
- Never claim exact nutritional values from an image.
"""


# ==========================================
# 6. IMAGE PROCESSING
# ==========================================

def input_image_setup(uploaded_file):

    if uploaded_file is None:
        raise ValueError("Please upload an image.")

    uploaded_file.seek(0)

    image = Image.open(uploaded_file)

    image.verify()

    uploaded_file.seek(0)

    image = Image.open(uploaded_file).convert("RGB")

    image_bytes = io.BytesIO()

    image.save(
        image_bytes,
        format="JPEG",
        quality=90
    )

    return image_bytes.getvalue()


# ==========================================
# 7. GEMINI RESPONSE WITH FALLBACK
# ==========================================

def get_gemini_response(user_input, image, prompt):

    last_error = None

    for model_name in AVAILABLE_MODELS:

        start_time = time.time()

        try:

            response = client.models.generate_content(

                model=model_name,

                contents=[
                    prompt,

                    types.Part.from_bytes(
                        data=image,
                        mime_type="image/jpeg"
                    ),

                    user_input
                ],

                config=types.GenerateContentConfig(

                    http_options=types.HttpOptions(

                        timeout=15000,

                        retry_options=types.HttpRetryOptions(
                            attempts=1
                        )

                    )

                )

            )

            elapsed = round(
                time.time() - start_time,
                2
            )

            if response.text:

                return (
                    response.text,
                    model_name,
                    elapsed
                )

            raise Exception(
                "Gemini returned an empty response."
            )

        except Exception as e:

            elapsed = round(
                time.time() - start_time,
                2
            )

            last_error = e

            error_message = str(e).lower()
            error_type = type(e).__name__.lower()

            temporary_error = (
                "503" in error_message
                or "429" in error_message
                or "unavailable" in error_message
                or "overloaded" in error_message
                or "timeout" in error_message
                or "timed out" in error_message
                or "timeout" in error_type
            )

            if temporary_error:

                st.warning(
                    f"{model_name} was unavailable after "
                    f"{elapsed} seconds. Trying backup model..."
                )

                continue

            raise e

    raise Exception(
        "All Gemini models are currently unavailable. "
        "Please try again later. "
        + str(last_error)
    )


# ==========================================
# 8. APPLICATION HEADER
# ==========================================

st.markdown("""
<div class="main-title">
    Health Management
</div>

<div class="subtitle">
    Your personal AI-powered nutrition companion.
    Understand your meals, explore nutritional values
    and make informed food choices.
</div>
""", unsafe_allow_html=True)

st.divider()


# ==========================================
# 9. MEAL INPUT SECTION
# ==========================================

st.markdown(
    '<div class="section-title">Analyze Your Meal</div>',
    unsafe_allow_html=True
)

user_input = st.text_input(
    "Additional instructions (optional)",
    placeholder="Example: Focus on calories, protein and portion size."
)

uploaded_file = st.file_uploader(
    "Upload your food image",
    type=["jpg", "jpeg", "png"],
    help="Upload a clear picture of your meal."
)


# ==========================================
# 10. IMAGE PREVIEW
# ==========================================

if uploaded_file is not None:

    st.markdown("#### Image Preview")

    st.image(
        uploaded_file,
        caption="Your uploaded meal",
        width=450
    )


st.write("")


# ==========================================
# 11. ANALYZE FOOD
# ==========================================

if st.button(
    "Analyze My Meal",
    type="primary",
    use_container_width=True
):

    if uploaded_file is None:

        st.warning(
            "Please upload a food image first."
        )

    else:

        try:

            with st.spinner("Preparing your food image..."):

                image_data = input_image_setup(
                    uploaded_file
                )

            with st.spinner("Analyzing your meal..."):

                response, model_name, elapsed = get_gemini_response(
                    user_input,
                    image_data,
                    input_prompt
                )

            st.success(
                "Your nutritional analysis is ready!"
            )

            # ==================================
            # 12. REPORT HEADER
            # ==================================

            st.markdown("""
            <div class="report-header">
                <h2>Your Nutrition Report</h2>
                <p>
                    A detailed breakdown of your meal
                    and its nutritional value.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.caption(
                f"AI Model: {model_name} | "
                f"Analysis time: {elapsed} seconds"
            )

            # ==================================
            # 13. REPORT CONTENT
            # ==================================

            with st.container(border=True):

                st.markdown(
                    '<div class="report-content">',
                    unsafe_allow_html=True
                )

                st.markdown(response)

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

            # ==================================
            # 14. FOOTER
            # ==================================

            st.markdown("""
            <div class="footer">
                HEALTH MANAGEMENT APP
                <br>
                AI-powered nutritional insights
                <br><br>
                Nutrition values are estimates
                and may differ from actual values.
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:

            st.error(
                f"Something went wrong: {e}"
            )

            st.info(
                "If Gemini is temporarily unavailable, "
                "please wait and try again."
            )
