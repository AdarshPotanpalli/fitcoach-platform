import streamlit as st
import requests
from frontend.streamlit_app import API_URL
from frontend import utils
import json

# st.set_page_config(page_title="Detailed Daily Plan", page_icon="📋")
st.title("📋 Detailed Daily Plan")

# if detailed plan exists in the database, then fetch it, if not, tell the user to go to preferences page and set preferences first
headers = {
    "Authorization": f"Bearer {utils.get_token()}"
}

@st.dialog("Are you sure you want to submit feedback?")
def submit_feedback(plans_feedback_data):
    """Function to handle feedback submission."""
    st.write("Per day you can submit feedback only once.")
    
    feedback_submit_final_button_pressed = st.button("Submit")
    if feedback_submit_final_button_pressed:
        response_feedback = requests.post(API_URL + "/plans/feedback", json = plans_feedback_data, headers=headers)
        if response_feedback.status_code == 200:
            st.success("Feedback submitted successfully!", icon="✅")
        else:
            st.error(f"Error submitting feedback: {response_feedback.json().get('detail', 'Unknown error')}")
        

plans_response = requests.get(API_URL + "/plans", headers = headers)
if plans_response.status_code == 404:
    # if no plan exists, then display a button to redirect to the onboarding page
    st.error("No detailed plan found. Please set your preferences first.")
    if st.button("Set your preferences"):
        st.switch_page("pages/onboarding_form.py")
else:
    # if plan exists, fetch the plan data
    detailed_plan = plans_response.json()
    detailed_plan["task1_content"] = json.loads(detailed_plan["task1_content"])
    detailed_plan["task2_content"] = json.loads(detailed_plan["task2_content"])
    detailed_plan["task3_content"] = json.loads(detailed_plan["task3_content"])

    # Parsing the plans data for the detailed view
    with st.expander(f"🧩 {detailed_plan["task1_title"]}", expanded=False):
        st.markdown(f"<div style='text-align: right;'> Time: <code>{detailed_plan.get('task1_timings_start', 'N/A')} - {detailed_plan.get('task1_timings_end', 'N/A')}</code></div>", unsafe_allow_html=True)
        st.markdown("**🪜 Steps:**")
        for step, task in detailed_plan["task1_content"].items():
            st.markdown(f"- {task}")
        st.success(f"**💡 Tip:** _{detailed_plan['task1_tip']}_")
        task1_done = st.checkbox(f"✅ Mark '{detailed_plan['task1_title']}' as done", key="done_task1")
    
    with st.expander(f"🧩 {detailed_plan['task2_title']}", expanded=False):
        st.markdown(f"<div style='text-align: right;'> Time: <code>{detailed_plan.get('task2_timings_start', 'N/A')} - {detailed_plan.get('task2_timings_end', 'N/A')}</code></div>", unsafe_allow_html=True)
        st.markdown("**🪜 Steps:**")
        for step, task in detailed_plan["task2_content"].items():
            st.markdown(f"- {task}")
        st.success(f"**💡 Tip:** _{detailed_plan['task2_tip']}_")
        task2_done = st.checkbox(f"✅ Mark '{detailed_plan['task2_title']}' as done", key="done_task2")
        
    with st.expander(f"🧩 {detailed_plan['task3_title']}", expanded=False):
        st.markdown(f"<div style='text-align: right;'> Time: <code>{detailed_plan.get('task3_timings_start', 'N/A')} - {detailed_plan.get('task3_timings_end', 'N/A')}</code></div>", unsafe_allow_html=True)
        st.markdown("**🪜 Steps:**")
        for step, task in detailed_plan["task3_content"].items():
            st.markdown(f"- {task}")
        st.success(f"**💡 Tip:** _{detailed_plan['task3_tip']}_")
        task3_done = st.checkbox(f"✅ Mark '{detailed_plan['task3_title']}' as done", key="done_task3")

    st.info("📋 Select the tasks you have completed today first, then click the button below to submit your feedback.")
    feedback_col1, feedback_col2, feedback_col3 = st.columns([1, 2, 1])
    with feedback_col2:
        st.button("Click to Share Your Completed Tasks for Today!", on_click=submit_feedback, args=([{
            "task1_done": task1_done,
            "task2_done": task2_done,
            "task3_done": task3_done
        }]))
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    # Action buttons for generating a new plan, updating preferences, and asking AI Coach
    with col1:
        st.markdown("Need a new plan?")
        if st.button("Generate New Plan"):
            with st.spinner("Generating new plan..."):
                utils.generate_plan(API_URL)
                st.success("New plan generated successfully!")
                st.rerun()
    with col2:
        st.markdown("Want to update your preferences?")
        if st.button("Update Preferences"):
            st.switch_page("pages/onboarding_form.py")
            
    with col3:
        st.markdown("Any doubts? Ask your AI Coach!")
        if st.button("Ask AI Coach"):
            st.switch_page("pages/ai_coach.py")