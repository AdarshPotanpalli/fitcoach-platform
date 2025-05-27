import streamlit as st

st.set_page_config(page_title="AI Health Coach - User Guide", page_icon="📘")

st.title("📘 Welcome to Your Personal AI Health Coach App!")
st.write("This guide helps you get the most out of your personalized health journey.")

st.success("✅ Pro Tip: Follow the steps below to get started quickly!")

# Getting Started
with st.expander("🚀 Getting Started"):
    st.subheader("1. Login / Create Your Profile")
    st.markdown("- 🔐 Use **Google Login** or register with **email and password**.")
    st.markdown("- Your account securely stores your preferences and progress.")
    if st.button("📝 Register Now"):
        st.info("Redirecting to Sign Up page...")
        st.switch_page("pages/register.py")

# Navigation Overview
with st.expander("🧭 Navigation Overview"):
    st.subheader("📚 Resources")
    st.markdown("""
    - 🏠 **Dashboard** – See your current day’s plan, weekly progress, and motivational tips.  
    - 🤖 **Your AI Coach** – Ask health questions and get personalized advice.  
    - 📝 **How Was Your Day?** – Provide feedback to improve tomorrow's plan.
    """)
    st.subheader("👤 Your Account")
    st.markdown("""
    - 🔐 **Login/Register**  
    - ⚙️ **Settings** – Manage preferences, calendar sync, and app behavior.
    """)

# Daily Routine
with st.expander("📅 Daily Routine"):
    st.subheader("🔄 Step-by-Step Flow")
    st.markdown("""
    1. Answer onboarding questions (goal, schedule, fitness level).  
    2. ✅ A personalized daily movement plan is generated.  
    3. 📆 Optionally sync with Google Calendar.  
    4. 🧘 Follow the plan.  
    5. ✍️ At night, give feedback on your day.
    """)
    st.info("Your feedback helps the AI improve your plan every day!")

# Ask Your Coach
with st.expander("❓ Ask Your Coach"):
    st.markdown("""
    Use the **AI Coach page** to:
    - Get **tailored health advice**.
    - Ask for **alternative workouts** or motivation.
    - Get **diet or recovery suggestions**.
    """)
    st.success("💡 The coach learns from your feedback and adapts every day.")

# Dashboard Highlights
with st.expander("📊 Dashboard Highlights"):
    st.markdown("""
    - **Today's Plan** – What’s scheduled for today.  
    - **Progress Tracker** – Weekly performance summary.  
    - **Motivation** – A new quote or insight every day.  
    - **Activity Feed** – Log of your past and planned activities.
    """)

# Privacy
with st.expander("🔐 Privacy & Data Safety"):
    st.markdown("""
    - Your data is securely stored and used only to improve your experience.  
    - Google login uses OAuth2 for security.  
    - No data is shared with third parties.
    """)
    st.warning("🔒 Stay secure: Always log out after using shared devices.")

# Tips
with st.expander("💡 Tips for Best Experience"):
    st.markdown("""
    - Complete your feedback **daily** to help personalize future plans.  
    - Keep your goals updated in the **Settings** page.  
    - Enable **Google Calendar sync** to stay organized.  
    - Come back regularly to ask your coach questions!
    """)

st.markdown("---")
st.header("🧘 Stay Consistent, Stay Healthy!")
st.markdown("Let your AI coach guide you — one step at a time 💪")

if st.button("🎯 Get Started Now"):
    st.balloons()
    st.success("Awesome! Head to the Dashboard to begin your journey.")
