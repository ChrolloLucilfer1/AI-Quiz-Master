import streamlit as st
from google import genai
import json

def get_quiz_data(topic, num_q):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("API Key missing! Add it to .streamlit/secrets.toml")
        return None

    client = genai.Client(api_key=api_key)
    
    prompt = (
        f"Create a {num_q}-question MCQ quiz about {topic}. "
        f"Pick one vibrant HEX color for the theme. "
        f"Return ONLY JSON: {{'color': '#hex', 'questions': [{{'q': '...', 'options': ['a','b','c','d'], 'correct': '...'}}]}}"
    )
    
    # These are the most stable model IDs for the current SDK
    models_to_try = ["gemini-2.0-flash-lite", "gemini-2.5-flash-lite"]
    
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name, 
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            return json.loads(response.text)
            
        except Exception as e:
            error_str = str(e)
            # If we hit a rate limit (429) or a model not found (404), try the next one
            if "429" in error_str or "404" in error_str:
                if model_name == models_to_try[-1]:
                    st.warning("🚦 The AI is currently unavailable or over-quota. Please try again in 1 minute.")
                continue
            else:
                st.error(f"Technical error with {model_name}: {error_str}")
                return None
    return None