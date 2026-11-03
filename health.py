
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
import streamlit as st
import os
import io

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GENAI_API_KEY")

if not api_key:
    st.error("Gemini API key not found. Check your .env file.")
    st.stop()


# Initialize Gemini client
@st.cache_resource
def load_model():
    return genai.Client(api_key=api_key)


client = load_model()


# Function to get Gemini response
def get_gemini_response(user_input, image, prompt):

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=[
            prompt,
            types.Part.from_bytes(
                data=image,
                mime_type="image/jpeg"
            ),
            user_input
        ]
    )

    return response.text


# Function to process uploaded image
def input_image_setup(uploaded_file):

    if uploaded_file is None:
        raise ValueError("Please upload an image.")

    image = Image.open(uploaded_file)
    image.verify()

    uploaded_file.seek(0)
    image = Image.open(uploaded_file).convert("RGB")

    image_bytes = io.BytesIO()
    image.save(image_bytes, format="JPEG")

    return image_bytes.getvalue()


# Streamlit page configuration
st.set_page_config(
    page_title="Gemini Health App",
    page_icon=":material/health_and_safety:",
    layout="centered"
)

st.title("Health Management App")
st.write("Upload your food image to estimate its nutritional value.")


# User input
user_input = st.text_input(
    "Additional instructions (optional):",
    placeholder="Example: Estimate calories and protein."
)

uploaded_file = st.file_uploader(
    "Upload your food image",
    type=["jpg", "jpeg", "png"]
)


# Display uploaded image
if uploaded_file is not None:

    st.image(
        uploaded_file,
        caption="Uploaded Food Image",
        use_container_width=True
    )


# Analysis prompt
input_prompt = """
You are a professional nutrition analysis assistant.

Analyze the food items visible in the uploaded image.

Provide the following information:

1. Identify every visible food item.
2. Estimate the serving size of each item.
3. Estimate calories for each item.
4. Estimate protein, carbohydrates and fats.
5. Calculate the approximate total calories and macronutrients.

Use this format:

Food Analysis

1. Food Item:
   Estimated Quantity:
   Calories:
   Protein:
   Carbohydrates:
   Fats:

Repeat for every food item.

Total Nutritional Summary:
Total Calories:
Total Protein:
Total Carbohydrates:
Total Fats:

Important:
- Give estimates, not exact measurements.
- Mention assumptions about portion sizes.
- Do not invent ingredients that cannot be identified.
- If the image is unclear, explain the limitation.
- Do not present the results as medical advice.
"""


# Submit button
if st.button("Analyze Food", type="primary"):

    if uploaded_file is None:
        st.warning("Please upload a food image first.")

    else:

        try:

            with st.spinner("Analyzing your food image..."):

                image_data = input_image_setup(uploaded_file)

                response = get_gemini_response(
                    user_input,
                    image_data,
                    input_prompt
                )

            st.subheader("Nutritional Analysis")
            st.write(response)

        except Exception as e:

            st.error(f"Something went wrong: {e}")
