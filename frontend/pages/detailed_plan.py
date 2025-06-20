import streamlit as st

# st.set_page_config(page_title="Detailed Daily Plan", page_icon="📋")

# Sample structured plan data ----->
detailed_plan = [
    {
        "title": "Morning Stretch",
        "duration": "10 minutes",
        "description": "Light stretches to wake up your muscles.",
        "steps": [
            "Stand tall and raise your arms.",
            "Stretch side-to-side slowly.",
            "Bend forward and hold for 10 seconds.",
        ],
        "tips": "Do this near an open window for fresh air."
    },
    {
        "title": "Midday Walk",
        "duration": "20 minutes",
        "description": "A light walk to stay active during the day.",
        "steps": [
            "Put on comfortable walking shoes.",
            "Walk around your building or outside.",
            "Maintain a brisk but steady pace.",
        ],
        "tips": "Take a different route to keep it interesting."
    },
    {
        "title": "Evening Strength Workout",
        "duration": "30 minutes",
        "description": "Basic strength exercises to end the day strong.",
        "steps": [
            "5 min warm-up (jog in place, jumping jacks).",
            "3 sets of squats, lunges, and push-ups.",
            "Cool down with deep breathing.",
        ],
        "tips": "Stay hydrated and track your reps!"
    }
]

st.title("📋 Detailed Daily Plan")

for i, activity in enumerate(detailed_plan):
    with st.expander(f"🧩 {activity['title']} ({activity['duration']})", expanded=False):
        st.info(f"**🔎 Description:** {activity['description']}")
        st.markdown("**🪜 Steps:**")
        for step in activity["steps"]:
            st.markdown(f"- {step}")
        st.success(f"**💡 Tip:** _{activity['tips']}_")
        
        # Completion checkbox
        st.checkbox(f"✅ Mark '{activity['title']}' as done", key=f"done_{i}")

# a button to swith to the dashboard page
if st.button("🔙 Back to Dashboard"):
    st.switch_page("pages/dashboard.py")