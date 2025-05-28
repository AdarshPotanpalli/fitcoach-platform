import streamlit as st

# Page setup
# st.set_page_config(page_title="Preferences", page_icon="🛠️")

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
    
    ## GOAL
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

    # st.markdown("### 🏋️ How would you rate your current fitness level?")
    # level = st.selectbox(
    #     "Select your level:",
    #     ["🌱 Beginner", "🌿 Intermediate", "🌳 Advanced"],
    #     index=["🌱 Beginner", "🌿 Intermediate", "🌳 Advanced"].index(defaults.get("level", "🌱 Beginner"))
    # )

    ## LIFESTYLE
    st.markdown("---")
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

    ## WORKOUT TIMES PREFERENCE 
    st.markdown("---")
    st.markdown("### 🕰️ Rank your preferred workout times (most to least preferred)")
    workout_time_options = [
        "🌅 Morning (6 AM - 9 AM)",
        "🏙️ Afternoon (12 PM - 3 PM)",
        "🌆 Evening (5 PM - 8 PM)",
        "🌙 Night (After 8 PM)",
    ]
    workout_time_pref = st.multiselect(
        "Select and order your preferences:",
        options=workout_time_options,
        default=defaults.get("workout_time_pref", []),
    )
    st.caption("👆 Select at least 1 option for better personalization.")
    # # Validate selection
    # if len(workout_time_pref) < 2:
    #     st.info("Tip: Select at least 2 for better personalization.")

    ## Extra Notes
    st.markdown("---")
    notes = st.text_area("📝 Any specific notes or considerations? (optional)", value=defaults.get("notes", ""))

    # Submit
    submitted = st.form_submit_button("✅ Submit")
    if submitted:
        st.session_state.onboarding_data = {
            "goal": goal,
            "lifestyle": lifestyle,
            "workout_time_pref": workout_time_pref,
            "notes": notes,
        }
        st.toast("✅ Preferences saved successfully!")
        

