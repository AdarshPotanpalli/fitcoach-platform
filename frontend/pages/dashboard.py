import streamlit as st
import pandas as pd
import datetime
from datetime import date
import numpy as np
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
import requests
from frontend.streamlit_app import API_URL
from frontend import utils
import time


def headers(): 
    """displays the page headers
    """
    # page configurations
    # st.set_page_config(page_title="Dashboard", page_icon="📊")

    # get the username ------>
    username = "Adarsh"
    st.title(f"📊 Here's Your Health Dashboard, {username}")

def metrics(df: pd.DataFrame):
    """displays progress as compared to last day
    """
    
    st.subheader("✅ Current Progress")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Steps Today", f"{df['Steps'].iloc[-1]}", f"{df['Steps'].iloc[-1] - df['Steps'].iloc[-2]} since yesterday")
    with col2:
        st.metric("Workout Minutes", f"{df['Workout Minutes'].iloc[-1]} min", f"{df['Workout Minutes'].iloc[-1] - df['Workout Minutes'].iloc[-2]} min")
    with col3:
        st.metric("Calories Burned", f"{df['Calories Burned'].iloc[-1]} kcal", f"{df['Calories Burned'].iloc[-1] - df['Calories Burned'].iloc[-2]} kcal")


def graphs(df: pd.DataFrame):
    """displays the graph tabs
    """
    st.markdown("---")
    st.subheader("📈 Progress Over Time")

    # Tabs for each metric
    tab1, tab2, tab3 = st.tabs(["👣 Steps", "🏋️ Workout Minutes", "🔥 Calories Burned"])

    with tab1:
        fig = px.bar(df, x="Date",y="Steps", title="👣 Daily Step Count", color="Steps", color_continuous_scale="Blues")
        fig.update_layout(xaxis_title="Date", yaxis_title="Steps", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig = px.bar(df, x="Date", y="Workout Minutes", title="🏋️ Workout Duration Per Day", color="Workout Minutes", color_continuous_scale="Purples")
        fig.update_layout(xaxis_title="Date", yaxis_title="Minutes", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
        
    # Adjust as needed ------>    
    calorie_goal = 2200  

    with tab3:
        fig = go.Figure()

        # Bright orange for actuals
        fig.add_trace(go.Scatter(
            x=df["Date"],
            y=df["Calories Burned"],
            mode="lines+markers",
            fill="tozeroy",
            name="Calories Burned",
            line=dict(color="#FFA500")  # Vibrant orange
        ))

        # Cyan dashed line for goal
        fig.add_trace(go.Scatter(
            x=df["Date"],
            y=[calorie_goal] * len(df),
            mode="lines",
            name="Goal",
            line=dict(dash="dash", color="#00FFFF")  # Bright cyan
        ))

        fig.update_layout(
            title="🔥 Calories Burned Over Time (with Goal)",
            xaxis_title="Date",
            yaxis_title="Calories",
            template="plotly_dark",  # Best for dark backgrounds
            showlegend=True,
            font=dict(color="white")  # Ensures text is visible
        )

        st.plotly_chart(fig, use_container_width=True)


def plan(today):
    """displays today's plan
    """
    st.markdown("---")
    st.subheader(f"📅 Today's Plan - {today.strftime('%A, %B %d')}")
    plan_df = pd.DataFrame(st.session_state.todays_plan)
    plan_df.columns = ["Time", "Activity"]
    # Reset index and drop the new index column
    plan_df.index = [""] * len(plan_df)
    # Display a static, clean table with no index shown
    st.table(plan_df)

    if st.button("📋 Explore details of your daily plan"):
        st.switch_page("pages/detailed_plan.py")

@st.dialog("Adjust your plan")
def adjust():
    st.write("Do you really want to make changes to your today's plan?")
    # generate new plan --->
    st.session_state.todays_plan = [
    {"time": "9:00 AM", "activity": "Late Morning Stretch (10 min)"},
    {"time": "1:30 PM", "activity": "After Lunch walk (20 min)"},
    {"time": "6:30 PM", "activity": "Strength Workout (30 min)"},
    ]
    if st.button("Submit"):
        st.rerun()
        st.toast("✅ Plan updated successfully!")
        
def adjust_plan():
    """Adjust today's plan
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
    st.write("You need to authenticate your Google Calendar first.")
    if st.link_button("Google Calendar Authenticate", url = auth_url):
        st.toast("🔄 Redirecting to Google Calendar authentication...")

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
                            

    
    # # if sync button is pressed, display the sync url   
    # if sync_button:
    #     # st.success("Click below to authorize Google Calendar sync:")
    #     try:
    #         if response_user.json().get("is_google_synced") == False:
    #             response_post = requests.post(API_URL + "/calendar/sync/post_event", headers=headers)
    #             if response_post.status_code == 400: # Bad Request, user not google authenticated
    #                 response = requests.get(API_URL + "/calendar/sync/start", headers=headers)
    #                 if response.status_code == 307:
    #                     auth_url = response.json().get("auth_url")
    #                     if auth_url:
    #                         sync_redirect(auth_url= auth_url)
    #                 elif response.status_code == 404:
    #                     st.toast(response.json().get("detail", "Plans not found! Set up your preferences first."))
    #                 else:
    #                     st.toast("Failed to initiate calendar sync.")
    #             elif response_post.status_code == 200:
    #                 st.toast("✅ Calendar synced successfully!")
    #                 # wait for 3 seconds before refreshing the page
    #                 time.sleep(1)
    #                 st.rerun() 
    #             else:
    #                 st.toast("Failed to sync calendar.")
    #         else:
    #             response = requests.delete(API_URL + "/calendar/sync/unsync_and_delete_events", headers=headers)
    #             if response.status_code == 200:
    #                 st.toast("✅ Calendar unsynced successfully!")
    #                 time.sleep(1)
    #                 st.rerun()  # Refresh the page to update the state
    #             else:
    #                 st.toast("Failed to unsync calendar.")
            
    #     except Exception as e:
    #         st.error(f"Error: {e}")

    
if __name__ == "__main__":
    
    headers()
    
    sync_calendar() # optional feature to sync with google calendar
    
    # Simulate today's and yesterday's data
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    
    # Sample progress data ------>
    progress_data = {
        "Date": pd.date_range(end=today, periods=7),
        "Steps": np.random.randint(4000, 10000, size=7),
        "Calories Burned": np.random.randint(1500, 2800, size=7),
        "Workout Minutes": np.random.randint(20, 60, size=7),
    }
    df = pd.DataFrame(progress_data)
    metrics(df)
    graphs(df)
    
    ## Simulated plan ----->
    if "todays_plan" not in st.session_state:
        st.session_state.todays_plan = [
            {"time": "7:00 AM", "activity": "Morning Stretch (10 min)"},
            {"time": "12:30 PM", "activity": "Midday Walk (20 min)"},
            {"time": "6:00 PM", "activity": "Strength Workout (30 min)"},
        ]
        
    plan(today)
    adjust_plan()
    talk_with_coach()
    footnote()
        
    
    