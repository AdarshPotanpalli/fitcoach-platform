import streamlit as st

def dashboard_page(user_name, today_plan, progress_summary, motivation_quote):
    st.title(f"Welcome back, {user_name}! 👋")

    # Summary cards in columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="Today's Plan", value=today_plan['title'], delta=today_plan['status'])

    with col2:
        st.metric(label="Weekly Progress", value=f"{progress_summary['percent_complete']}%", delta=progress_summary['delta'])

    with col3:
        st.write("💡 Motivation")
        st.info(motivation_quote)

    st.markdown("---")

    st.subheader("Your Activity Feed")
    if today_plan.get('activities'):
        for activity in today_plan['activities']:
            st.write(f"- {activity}")
    else:
        st.write("No activities planned for today. Enjoy your rest day! 🎉")




# Example usage (replace with real data from your backend)
if __name__ == "__main__":
    # get the name from the logged in user -->
    user_name = "Alice"
    # get the plan from the logged in user -->
    today_plan = {
        'title': "Light Yoga & Stretching",
        'status': "On track",
        'activities': ["10 min breathing exercise", "15 min light yoga", "5 min stretching"]
    }
    # get this from the user feedback -->
    progress_summary = {'percent_complete': 65, 'delta': "+5% vs last week"}
    motivation_quote = "Consistency is the key to lasting health!"

    next_page = dashboard_page(user_name, today_plan, progress_summary, motivation_quote)
    
