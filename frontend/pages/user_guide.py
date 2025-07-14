import streamlit as st

# st.set_page_config(page_title="AI Health Coach - User Guide", page_icon="📘")

st.title("📘 Welcome to Your Personal AI Health Coach App!")
st.write("This guide helps you get the most out of your personalized health journey.")

st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)

# Row 1: Signup and Personalisation
col1, col2 = st.columns(2)
with col1:
    st.subheader("📝 Step 1: Create an Account")
    st.markdown("Sign up with your email and password to get started.")

with col2:
    st.subheader("🎯 Step 2: Set Your Preferences")
    st.markdown("""
    On the **Personalization page**, set your fitness goals and lifestyle.
    This personalizes your experience. You can update these preferences anytime later.
    """)

st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)

# Row 2: Daily Plan and Feedback
col3, col4 = st.columns(2)
with col3:
    st.subheader("📅 Step 3: Get Your Daily Plan")
    st.markdown("""
    A new day plan is generated automatically every day.
    Each plan contains **3 tasks**, and each task has **3 steps**.
    """)

with col4:
    st.subheader("✅ Step 4: Give Feedback")
    st.markdown("""
    After completing your tasks, give feedback **before midnight**.
    This helps track your progress accurately.
    """)

st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)

# Row 3: AI Coach and Dashboard
col5, col6 = st.columns(2)
with col5:
    st.subheader("🤖 Step 5: Talk to Your AI Coach")
    st.markdown("""
    You can chat with the AI Coach anytime.
    The coach knows your **goals** and **today’s plan**, and can guide you on your journey.
    """)

with col6:
    st.subheader("📊 Step 6: Visit Your Dashboard")
    st.markdown("""
    Track your progress, view a summary of your day’s tasks,
    and update today’s plan if you’re behind schedule.
    """)

st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)

# Final Row: Calendar Syncing
col7, col8 = st.columns(2)

with col7:
    st.subheader("📆 Optional: Google Calendar Sync")
    st.markdown("""
    From the dashboard, you can **sync your day’s plan to your Google Calendar**.
    This requires Google authentication.
    """)

with col8:
    st.subheader("🚫 Unsync Calendar if you wish")
    st.markdown("""
    You can also **unsync** your Google Calendar to remove the events.
    Note: Calendar syncing is **not scheduled automatically** each day.
    """)

st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)

st.success("We hope you enjoy the experience! Stay consistent and let your AI coach help you thrive.")
