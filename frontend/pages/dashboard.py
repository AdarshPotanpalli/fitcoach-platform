import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
import numpy as np
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
import requests
from frontend.streamlit_app import API_URL
from frontend import utils
import time
import json
import nivo_chart as nc

headers = {
    "Authorization": f"Bearer {utils.get_token()}"
}

def head(): 
    """displays the page headers
    """
    # page configurations
    # st.set_page_config(page_title="Dashboard", page_icon="📊")

    # get the username ------>
    response_user = requests.get(API_URL + "/me", headers=headers)
    if response_user.status_code == 200:
        user_data = response_user.json()
        username = user_data.get("username", "User")
    st.title(f"📊 Here's Your Health Dashboard, {username}")


def graphs():
    """displays the graph tabs
    """
    st.markdown("---")
    st.subheader("📈 Progress Over Time")

    # Feedback History data
    user_feedback_history = []
    response_get_feedback = requests.get(API_URL + "/plans/feedback", headers=headers)
    if response_get_feedback.status_code == 404:
        pass # No feedback history found
    else:
        task_feedback_history = response_get_feedback.json()
        for task_feedback in task_feedback_history:
            tasks_done = sum([task_feedback['task1_done'], task_feedback['task2_done'], task_feedback['task3_done']])
            user_feedback_history.append({
                "value": tasks_done,
                "day": task_feedback['date']
            })

    end_date = datetime.today().date()
    start_date = end_date - timedelta(weeks=20)  # starting from 20 weeks ago

    calendar_chart = {
        "data": user_feedback_history,
        "layout": {
            "type": "calendar",
            "height": 150,  # adjusted for more visibility
            "width": 650,  # wider for better layout
            "from": "2025-07-01",
            "to": "2025-12-31",
            "emptyColor": "#f0f0f0",
            "colors": [
                "#d6e685",  # light green
                "#8cc665",  # medium green
                "#44a340",  # darker green
                "#0d47a1"   # darkest green
            ],
            "margin": {"top": 0, "right": 0, "bottom": 0, "left": 30},
            "yearSpacing": 48,
            "minValue": 0,
            "maxValue": 3,
            "monthBorderColor": "#DDDDDD",
            "dayBorderWidth": 2,
            "dayBorderColor": "#ffffff",
            "monthBorderWidth": 2,
            "legends": [
                {
                    "anchor": "bottom-right",
                    "direction": "row",
                    "translateY": 40,
                    "itemCount": 4,
                    "itemWidth": 70,
                    "itemHeight": 36,
                    "itemsSpacing": 16,
                    "itemDirection": "right-to-left",
                    "itemTextColor": "#333333",
                    "data": [
                        {"color": "#d6e685", "label": "1 task", "value": 0}, # Added value
                        {"color": "#8cc665", "label": "2 tasks", "value": 1}, # Added value
                        {"color": "#44a340", "label": "3 tasks", "value": 2}, # Added value
                        {"color": "#0d47a1", "label": "4+ tasks", "value": 3}  # Added value
                    ]
                }
            ],
        },
    }

    nc.nivo_chart(data=calendar_chart["data"], layout=calendar_chart["layout"], key="calendar_chart")
    
    # Custom legend below the chart
    st.markdown("""
    <div style='display: flex; justify-content: center; gap: 20px; margin-top: 0px;'>
        <div style='display: flex; align-items: center;'>
            <div style='width: 10px; height: 10px; background-color: #d6e685; margin-right: 8px;'></div>
            <span>0 tasks done</span>
        </div>
        <div style='display: flex; align-items: center;'>
            <div style='width: 10px; height: 10px; background-color: #8cc665; margin-right: 8px;'></div>
            <span>1 task done</span>
        </div>
        <div style='display: flex; align-items: center;'>
            <div style='width: 10px; height: 10px; background-color: #44a340; margin-right: 8px;'></div>
            <span>2 tasks done</span>
        </div>
        <div style='display: flex; align-items: center;'>
            <div style='width: 10px; height: 10px; background-color: #0d47a1; margin-right: 8px;'></div>
            <span>3 tasks done</span>
        </div>
    </div>
    """, unsafe_allow_html=True)



def plan():
    """displays today's plan
    """
    date_today = date.today()
    st.markdown("---")
    st.subheader(f"📅 Today's Plan - {date_today.strftime('%A, %B %d')}")
    
    plans_response = requests.get(API_URL + "/plans", headers = headers)
    if plans_response.status_code == 404:
        # if no plan exists, then display a button to redirect to the onboarding page
        st.error("No plans found. Please set your preferences first.")
        if st.button("Set your preferences"):
            st.switch_page("pages/onboarding_form.py")
    else:
        # if plan exists, fetch the plan data
        detailed_plan = plans_response.json()
        detailed_plan["task1_content"] = json.loads(detailed_plan["task1_content"])
        detailed_plan["task2_content"] = json.loads(detailed_plan["task2_content"])
        detailed_plan["task3_content"] = json.loads(detailed_plan["task3_content"])

        # Parsing the plans data for the detailed view
        st.markdown(f"Task 1: {detailed_plan['task1_title']}")
        st.markdown(f"Task 2: {detailed_plan['task2_title']}")
        st.markdown(f"Task 3: {detailed_plan['task3_title']}")
        
        st.info("📋 Each task is further broken down into steps. Click the below button to get the details")
        if st.button("Show Detailed Plan"):
            st.switch_page("pages/detailed_plan.py")


@st.dialog("Update your plan")
def adjust():
    
    plans_response = requests.get(API_URL + "/plans", headers = headers)
    if plans_response.status_code == 404:
        # if no plan exists, then display a button to redirect to the onboarding page
        st.error("No plans found. Please set your preferences first.")
    else:
        st.write("Do you really want to update your today's plan?")
        # generate new plan --->
        if st.button("Submit"):
            with st.spinner("Updating your today's plan..."):
                utils.generate_plan(API_URL)
            st.success("✅ Plan updated successfully!")
            time.sleep(1)
            st.rerun()  # Refresh the page to show the updated plan
        
def adjust_plan():
    """Update today's plan
    """
    st.markdown("---")
    st.markdown("""
    ### 🕒 Behind Schedule?  
    Hit the button below to adjust today’s plan 💼➡️💪
    """)
    if st.button("🔄 Update my plan"):
        adjust()
            
def talk_with_coach():
    # AI Coach Prompt
    st.markdown("---")
    st.markdown("""
    ### 🧑‍🏫 Need Personalized Advice?
    Your AI Coach is ready to assist you with tailored tips, planning, and motivation.
    """)
    if st.button("🤖 Talk with coach"):
        st.switch_page("pages/ai_coach.py")

def footnote():
    """A Motivational footnote
    """
    # Optional: Include a motivational quote or message
    st.markdown("---")

    ## get a new quote per day -----> 
    st.info("💡 *“Discipline is the bridge between goals and accomplishment.” – Jim Rohn*")

@st.dialog("Google Authentication Required")
def sync_redirect(auth_url:str):
    st.markdown("""You need to authenticate your Google Calendar first. 
                Once authenticated, click "Sync Calendar" button again.""")
    link_button = st.link_button("Google Calendar Authenticate", url = auth_url)
    # if link_button:
    #     st.toast("🔄 Redirecting to Google Calendar authentication...")

def sync_calendar():
    """ Function to sync with Google Calendar """
    # Google Calendar Sync
    col1, col2, col3 = st.columns([2, 1,  1])  # adjust ratio as needed # right aligned

    # jwt token headers
    headers = {
        "Authorization": f"Bearer {utils.get_token()}"
    }

    response_user = requests.get(API_URL + "/me", headers=headers)
    if response_user.status_code == 200 : # User is jwt authenticated
        if response_user.json().get("is_google_synced") == False: # User is not synced with Google Calendar
            with col3:
                sync_button = st.button("Sync Calendar")
                if sync_button: # if sync button is pressed
                    try:
                        response_post = requests.post(API_URL + "/calendar/sync/post_event", headers=headers)
                        if response_post.status_code == 400: # Bad Request, user not google authenticated
                            response = requests.get(API_URL + "/calendar/sync/start", headers=headers)
                            if response.status_code == 307:
                                auth_url = response.json().get("auth_url")
                                if auth_url:
                                    sync_redirect(auth_url= auth_url) # redirect for Google Calendar authentication
                            elif response.status_code == 404:
                                st.toast(response.json().get("detail", "Plans not found! Set up your preferences first."))
                            else:
                                st.toast("Failed to initiate calendar sync.")
                        elif response_post.status_code == 200: # Calendar synced successfully
                            st.toast("✅ Calendar synced successfully!")
                            # wait for 3 seconds before refreshing the page
                            time.sleep(1)
                            st.rerun() 
                        else:
                            st.toast("Failed to sync calendar.")
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            with col2:
                sync_button = st.button("Got new plans? Sync Calendar Again!")
                if sync_button: # if sync button is pressed
                    try:
                        response = requests.put(API_URL + "/calendar/sync/update_events", headers=headers)
                        if response.status_code == 200:
                            st.toast("✅ Calendar updated successfully!")
                            # wait for 1 seconds before refreshing the page
                            time.sleep(1)
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            with col3:
                unsync_button = st.button("Unsync Calendar")
                if unsync_button:
                    try:
                        response = requests.delete(API_URL + "/calendar/sync/unsync_and_delete_events", headers=headers)
                        if response.status_code == 200:
                            st.toast("✅ Calendar unsynced successfully!")
                            time.sleep(1)
                            st.rerun()  # Refresh the page to update the state
                        else:
                            st.toast("Failed to unsync calendar.")
                    except Exception as e:
                        st.error(f"Error: {e}")
    else: # User is not jwt authenticated
        pass                            

    
if __name__ == "__main__":
    
    head()
    
    sync_calendar() # optional feature to sync with google calendar
    
    # Progress data ------>
    graphs()
    
    # Show, adjust plan ---->
        
    plan()
    adjust_plan()
    talk_with_coach()
    footnote()
        
    
    