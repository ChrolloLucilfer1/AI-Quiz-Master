import streamlit as st
from google import genai
import json
import re

# Structural contract expected from the LLM for a valid quiz payload.
HEX_COLOR_PATTERN = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")
REQUIRED_QUESTION_KEYS = {"q", "options", "correct"}

def validate_quiz_schema(data):
    """
    Validates LLM JSON output against the expected quiz schema before use.
    Checks: top-level required fields, hex color format, per-question required
    fields, option list shape, and that the 'correct' answer is one of the options.
    Returns (is_valid: bool, error_reason: str | None).
    """
    if not isinstance(data, dict):
        return False, "Response is not a JSON object"

    if "color" not in data or "questions" not in data:
        return False, "Missing required top-level field(s): 'color' and/or 'questions'"

    if not isinstance(data["color"], str) or not HEX_COLOR_PATTERN.match(data["color"]):
        return False, f"Invalid hex color format: {data.get('color')!r}"

    questions = data["questions"]
    if not isinstance(questions, list) or len(questions) == 0:
        return False, "'questions' must be a non-empty list"

    for i, question in enumerate(questions):
        if not isinstance(question, dict):
            return False, f"Question {i} is not a JSON object"

        missing = REQUIRED_QUESTION_KEYS - question.keys()
        if missing:
            return False, f"Question {i} missing required field(s): {missing}"

        if not isinstance(question["q"], str) or not question["q"].strip():
            return False, f"Question {i} has an empty or invalid 'q' field"

        options = question["options"]
        if not isinstance(options, list) or len(options) < 2:
            return False, f"Question {i} 'options' must be a list with at least 2 choices"

        if question["correct"] not in options:
            return False, f"Question {i} 'correct' answer is not present in 'options'"

    return True, None


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
            data = json.loads(response.text)

            is_valid, error_reason = validate_quiz_schema(data)
            if not is_valid:
                # Malformed LLM output caught before it reaches the UI.
                # Fall through to the next model rather than serving bad data.
                if model_name == models_to_try[-1]:
                    st.warning(f"⚠️ AI returned malformed quiz data ({error_reason}). Please try again.")
                continue

            return data
            
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