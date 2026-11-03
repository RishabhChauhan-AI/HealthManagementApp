# Health Management App

An AI-powered nutrition analysis application built using **Python, Streamlit, and Google's Gemini API**.

Health Management App helps users understand the nutritional composition of their meals by analyzing food images. It identifies visible food components and provides estimated nutritional values, including calories, protein, carbohydrates, and fats.

## Features

### AI-Powered Food Analysis
- Upload food images in JPG, JPEG, and PNG formats.
- Identify food items and dishes using AI.
- Estimate meal serving size and weight.
- Generate detailed nutritional reports.

### Nutritional Breakdown
- Estimated calories.
- Protein content.
- Carbohydrates.
- Fat content.
- Component-wise nutritional estimates.

### Nutrition Insights
- Understand which food components contribute the most calories.
- Evaluate whether a meal is protein-rich, carbohydrate-rich, or fat-rich.
- Understand the nutritional balance of a meal.
- Receive suggestions to improve nutritional quality.
- Get insights related to muscle maintenance and growth.

### Additional Features
- Optional user instructions for personalized analysis.
- Automatic image processing.
- Gemini model fallback when a temporary service error occurs.
- Analysis time and model information.
- Custom dark-themed Streamlit interface.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Web application interface |
| Google Gemini API | AI-powered food image analysis |
| Google GenAI SDK | Gemini API integration |
| Pillow (PIL) | Image processing |
| python-dotenv | Environment variable management |

## How It Works

1. The user uploads a photograph of their meal.
2. Pillow processes the uploaded image and converts it into JPEG format.
3. The processed image is sent to Google's Gemini API.
4. Gemini identifies visible food components and estimates their nutritional values.
5. The application generates a structured Markdown nutrition report.
6. The user can review the meal identification, nutritional breakdown, and practical nutrition insights.

## Project Structure

```text
HealthBasedApp/
│
├── health.py
├── requirements.txt
├── README.md
├── .gitignore
└── .env
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/RishabhChauhan-AI/HealthBasedApp.git
```

### 2. Navigate to the project directory

```bash
cd HealthBasedApp
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

**Windows:**

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure your Gemini API key

Create a `.env` file in the project root directory:

```env
GENAI_API_KEY=your_google_gemini_api_key
```

Replace the placeholder with your own Gemini API key.

### 7. Run the application

```bash
streamlit run health.py
```

The application will open in your browser.

## Important Notes

- Nutritional values are estimates generated from food images.
- Actual nutritional values depend on ingredients, portion sizes, and cooking methods.
- Images may not reveal hidden ingredients, cooking oil, sauces, or exact quantities.
- The application is intended for educational purposes and is not a substitute for professional medical or dietary advice.
- A Google Gemini API key is required.

## Future Improvements

- User-defined calorie and macronutrient goals.
- Daily meal tracking.
- Food history and nutritional summaries.
- Multiple food image analysis.
- Personalized meal recommendations.
- Integration with fitness and health tracking features.

## Author

**Rishabh Chauhan**

GitHub: [RishabhChauhan-AI](https://github.com/RishabhChauhan-AI)

---

*Built with Python, Streamlit, and Generative AI to make nutritional information easier to understand.*