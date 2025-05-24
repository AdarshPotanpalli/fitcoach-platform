import streamlit as st

# Page setup
st.set_page_config(page_title="Preferences", page_icon="🛠️")

# Check if user is returning
is_returning = "onboarding_data" in st.session_state

# Dynamic Title & Subtitle
if is_returning:
    st.title("🔧 Update Your Preferences")
    st.markdown("Feel like changing your goals or routine? Update your fitness preferences below.")
else:
    st.title("🚀 Let's Get You Started!")
    st.markdown("Welcome! We’ll set up your fitness plan based on your needs and preferences.")

# Load defaults if available
defaults = st.session_state.get("onboarding_data", {})

# Main Form
with st.form("onboarding_form"):
    st.markdown("### 🎯 What's your primary goal?")
    goal = st.selectbox(
        "Choose your fitness goal:",
        [
            "💪 Functional Fitness",
            "🤱 Postnatal Plan",
            "🏃 Run 4km Nonstop",
            "🧘 Improve Flexibility",
            "🧠 Mental Wellness",
            "🔥 Weight Loss",
        ],
        index=[
            "💪 Functional Fitness",
            "🤱 Postnatal Plan",
            "🏃 Run 4km Nonstop",
            "🧘 Improve Flexibility",
            "🧠 Mental Wellness",
            "🔥 Weight Loss",
        ].index(defaults.get("goal", "💪 Functional Fitness"))
    )

    st.markdown("### 🏋️ How would you rate your current fitness level?")
    level = st.selectbox(
        "Select your level:",
        ["🌱 Beginner", "🌿 Intermediate", "🌳 Advanced"],
        index=["🌱 Beginner", "🌿 Intermediate", "🌳 Advanced"].index(defaults.get("level", "🌱 Beginner"))
    )

    st.markdown("### 🌟 What best describes your lifestyle?")
    lifestyle = st.selectbox(
        "Choose one:",
        [
            "🪑 Sedentary (Desk Job, minimal movement)",
            "🚶 Lightly Active (Some daily movement)",
            "🏃‍♂️ Active (Regular workouts)",
            "⚡ Very Active (High intensity + daily movement)",
        ],
        index=[
            "🪑 Sedentary (Desk Job, minimal movement)",
            "🚶 Lightly Active (Some daily movement)",
            "🏃‍♂️ Active (Regular workouts)",
            "⚡ Very Active (High intensity + daily movement)",
        ].index(defaults.get("lifestyle", "🚶 Lightly Active (Some daily movement)"))
    )

    st.markdown("### 🕰️ What time do you prefer to work out?")
    workout_time = st.selectbox(
        "Select your preferred workout time:",
        [
            "🌅 Morning (6 AM - 9 AM)",
            "🏙️ Afternoon (12 PM - 3 PM)",
            "🌆 Evening (5 PM - 8 PM)",
            "🌙 Night (After 8 PM)",
        ],
        index=[
            "🌅 Morning (6 AM - 9 AM)",
            "🏙️ Afternoon (12 PM - 3 PM)",
            "🌆 Evening (5 PM - 8 PM)",
            "🌙 Night (After 8 PM)",
        ].index(defaults.get("workout_time", "🌅 Morning (6 AM - 9 AM)"))
    )

    notes = st.text_area("📝 Any specific notes or considerations? (optional)", value=defaults.get("notes", ""))

    # Submit
    submitted = st.form_submit_button("✅ Submit")
    if submitted:
        st.session_state.onboarding_data = {
            "goal": goal,
            "level": level,
            "lifestyle": lifestyle,
            "workout_time": workout_time,
            "notes": notes,
        }
        st.toast("✅ Preferences saved successfully!")
        

