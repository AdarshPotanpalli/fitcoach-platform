import streamlit as st
import requests
from frontend.streamlit_app import API_URL
from frontend import utils
import json

# st.set_page_config(page_title="Detailed Daily Plan", page_icon="📋")

# if detailed plan exists in the database, then fetch it, if not, tell the user to go to preferences page and set preferences first
headers = {
    "Authorization": f"Bearer {utils.get_token()}"
}
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
    
    st.title("📋 Detailed Daily Plan")
    with st.expander(f"🧩 {detailed_plan["task1_title"]}", expanded=False):
        st.markdown(f"<div style='text-align: right;'> Time: <code>{detailed_plan.get('task1_timings', 'N/A')}</code></div>", unsafe_allow_html=True)
        st.markdown("**🪜 Steps:**")
        for step, task in detailed_plan["task1_content"].items():
            st.markdown(f"- {task}")
        st.success(f"**💡 Tip:** _{detailed_plan['task1_tip']}_")
        st.checkbox(f"✅ Mark '{detailed_plan['task1_title']}' as done", key="done_task1")
    
    with st.expander(f"🧩 {detailed_plan['task2_title']}", expanded=False):
        st.markdown(f"<div style='text-align: right;'> Time: <code>{detailed_plan.get('task2_timings', 'N/A')}</code></div>", unsafe_allow_html=True)
        st.markdown("**🪜 Steps:**")
        for step, task in detailed_plan["task2_content"].items():
            st.markdown(f"- {task}")
        st.success(f"**💡 Tip:** _{detailed_plan['task2_tip']}_")
        st.checkbox(f"✅ Mark '{detailed_plan['task2_title']}' as done", key="done_task2")
        
    with st.expander(f"🧩 {detailed_plan['task3_title']}", expanded=False):
        st.markdown(f"<div style='text-align: right;'> Time: <code>{detailed_plan.get('task3_timings', 'N/A')}</code></div>", unsafe_allow_html=True)
        st.markdown("**🪜 Steps:**")
        for step, task in detailed_plan["task3_content"].items():
            st.markdown(f"- {task}")
        st.success(f"**💡 Tip:** _{detailed_plan['task3_tip']}_")
        st.checkbox(f"✅ Mark '{detailed_plan['task3_title']}' as done", key="done_task3")

st.markdown("---")
if st.button("Update Preferences"):
    st.switch_page("pages/onboarding_form.py")