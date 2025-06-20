import streamlit as st
import requests
from frontend.streamlit_app import API_URL
from frontend import utils

headers = {
            "Authorization": f"Bearer {utils.get_token()}"
            }
# If preferences for the user exists, the title will be different
response = requests.get(API_URL + "/preferences", headers=headers)
if response.status_code == 200:
    st.title("🔧 Update Your Preferences")
    st.markdown("Feel like changing your goals or routine? Update your fitness preferences below.")
    
    # If preferences exist, pre-fill the form with existing data
    goal_response = response.json().get("goal")
    lifestyle_response = response.json().get("lifestyle")
    preferred_timings_response = response.json().get("preferred_timings")
    note_response = response.json().get("note")
    
else:
    st.title("🚀 Let's Get You Started!")
    st.markdown("Welcome! We’ll set up your fitness plan based on your needs and preferences.")


# Main Form
with st.form("onboarding_form"):
    
    ## GOAL
    st.markdown("### 🎯 What's your primary goal?")
    goal = st.selectbox(
        "Choose your fitness goal:",
        [
            "Functional Fitness",
            "Postnatal Plan",
            "Cardiac exercises",
            "Improve Flexibility",
            "Mental Wellness",
            "Weight Loss",
        ],
        index = [
            "Functional Fitness",
            "Postnatal Plan",
            "Cardiac exercises",
            "Improve Flexibility",
            "Mental Wellness",
            "Weight Loss",
        ].index(goal_response) if response.status_code == 200 else 0 # setting the goal if the user preferences exist
    )

    ## LIFESTYLE
    st.markdown("---")
    st.markdown("### 🌟 What best describes your lifestyle?")
    lifestyle = st.selectbox(
        "Choose one:",
        [
            "Sedentary (Desk Job, minimal movement)",
            "Lightly Active (Some daily movement)",
            "Active (Regular workouts)",
            "Very Active (High intensity + daily movement)",
        ],
        index= [
            "Sedentary (Desk Job, minimal movement)",
            "Lightly Active (Some daily movement)",
            "Active (Regular workouts)",
            "Very Active (High intensity + daily movement)",
        ].index(lifestyle_response) if response.status_code == 200 else 0 # setting the lifestyle if the user preferences exist
    )

    ## WORKOUT TIMES PREFERENCE 
    st.markdown("---")
    st.markdown("### 🕰️ Rank your preferred workout times (most to least preferred)")
    workout_time_options = [
        "Morning (6 AM - 9 AM)",
        "Afternoon (12 PM - 3 PM)",
        "Evening (5 PM - 8 PM)",
        "Night (After 8 PM)",
    ]
    workout_time_pref = st.multiselect(
        "Select and order your preferences:",
        options=workout_time_options,
        default= preferred_timings_response if response.status_code == 200 else []
    )
    st.caption("👆 Select at least 1 option for better personalization.")

    ## Extra Notes
    st.markdown("---")
    note = st.text_area("📝 Any specific notes or considerations? (optional)", value =  note_response if response.status_code == 200 else "")
    # Submit
    submitted = st.form_submit_button("✅ Submit")
    if submitted:
        # set preferences on submit, then redirect to the detailed plan page
        onboarding_data = {
            "goal": goal,
            "lifestyle": lifestyle,
            "preferred_timings": workout_time_pref if workout_time_pref != [] else ["Morning (6 AM - 9 AM)"],  # Default to morning if none selected
            "note": note,
        }
        if response.status_code == 200:
            # If preferences exist, update them
            set_preferences_response = requests.put(API_URL + "/preferences", json=onboarding_data, headers=headers)
            if set_preferences_response.status_code == 200:
                st.toast("✅ Preferences updated successfully!")
                # update the detailed plan first before switching, and show a loading spinner
                with st.spinner("Updating your detailed plan..."):
                    utils.generate_plan(API_URL)
                st.switch_page("pages/detailed_plan.py")
            else:
                error_detail = set_preferences_response.json().get("detail", "Something went wrong!")
        else:
            # If preferences do not exist, create them
            set_preferences_response = requests.post(API_URL + "/preferences", json=onboarding_data, headers= headers)
            if set_preferences_response.status_code == 201:
                st.toast("✅ Preferences saved successfully!")
                # generate the detailed plan first before switching, and show a loading spinner
                with st.spinner("Generating your detailed plan..."):
                    utils.generate_plan(API_URL)
                st.switch_page("pages/detailed_plan.py")
            else:
                error_detail = set_preferences_response.json().get("detail", "Something went wrong!")
        

