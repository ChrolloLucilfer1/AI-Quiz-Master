import streamlit as st
import sys
import os

# Add src to system path for modular imports
sys.path.append(os.path.join(os.getcwd(), 'src'))
from auth_logic import init_db, login_user, add_user
from quiz_engine import get_quiz_data

# Initialize App
st.set_page_config(page_title="AI Quiz Master", page_icon="🤖", layout="wide")
init_db()

# Session State Management
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
    st.session_state.user_answers = {}
    st.session_state.primary_color = "#FF4B4B"

# --- LOGIN / SIGNUP SCREEN ---
if not st.session_state.authenticated:
    st.title("🤖 AI Quiz Master")
    tab1, tab2 = st.tabs(["Login", "Signup"])
    
    with tab1:
        u = st.text_input("Username", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")
        if st.button("Access Arena"):
            if login_user(u, p):
                st.session_state.authenticated = True
                st.session_state.username = u
                st.rerun()
            else:
                st.error("Invalid credentials.")

    with tab2:
        nu = st.text_input("New Username", key="reg_user")
        np = st.text_input("New Password", type="password", key="reg_pass")
        if st.button("Create Account"):
            if add_user(nu, np):
                st.success("Account created! You can now login.")
            else:
                st.error("Username already exists.")

# --- MAIN QUIZ INTERFACE ---
else:
    st.sidebar.title(f"Welcome, {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.quiz_data = None
        st.rerun()

    if st.session_state.quiz_data is None:
        st.header("Configure Your Challenge")
        topic = st.text_input("Topic", placeholder="e.g., Linux Kernel, UFC, Naruto")
        count = st.select_slider("Number of Questions", options=[5, 10, 15])
        
        if st.button("Generate Quiz"):
            with st.spinner("AI is crafting your quiz..."):
                data = get_quiz_data(topic, count)
                if data:
                    st.session_state.quiz_data = data['questions']
                    st.session_state.primary_color = data.get('color', '#FF4B4B')
                    st.rerun()
    else:
        # Dynamic Theming
        st.markdown(f"""
            <style>
            .stApp {{ background-color: #0E1117; }}
            div[data-testid="stVerticalBlock"] > div {{
                border-left: 5px solid {st.session_state.primary_color};
                background-color: #1A1C23;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
            }}
            </style>
            """, unsafe_allow_html=True)
        
        st.title("🔥 Quiz Arena")
        if st.button("⬅️ Change Topic"):
            st.session_state.quiz_data = None
            st.rerun()

        for i, item in enumerate(st.session_state.quiz_data):
            st.subheader(f"Q{i+1}: {item['q']}")
            st.session_state.user_answers[i] = st.radio("Select Answer:", item['options'], key=f"q{i}", index=None)

        if st.button("Submit Result"):
            if None in st.session_state.user_answers.values():
                st.warning("Please answer all questions before submitting!")
            else:
                score = sum(1 for i, item in enumerate(st.session_state.quiz_data) if st.session_state.user_answers[i] == item['correct'])
                st.balloons()
                st.success(f"Final Score: {score} / {len(st.session_state.quiz_data)}")
                st.session_state.quiz_data = None # Reset for next round