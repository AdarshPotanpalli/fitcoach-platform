import streamlit as st

user_manual_text = """# 📘 Welcome to Your Personal AI Health Coach App!

This guide will help you understand how to use the app, get the most out of your personalized plans, and stay motivated on your health journey.

---

## 🚀 Getting Started

### 1. Login / Create Your Profile
- 🔐 Use **Google Login** or register with **email and password**.
- Your account securely stores your preferences and progress.

---

## 🧭 Navigation Overview

### 📚 **Resources**
- 🏠 **Dashboard**  
  See your current day’s plan, weekly progress, and motivational tips.
- 🤖 **Your AI Coach**  
  Ask fitness, recovery, or health questions and get personalized advice.
- 📝 **How Was Your Day?**  
  Provide daily feedback to improve your next day’s plan.

### 👤 **Your Account**
- 🔐 **Login/Register**  
  Access or create your account.
- ⚙️ **Settings**  
  Manage preferences, calendar sync, and app behavior.

---

## 📅 Daily Routine

### 🔄 Step-by-Step Flow
1. **Answer onboarding questions** on your first login (goal, schedule, fitness level).
2. ✅ A **daily movement plan** is generated just for you.
3. 📆 Plans are optionally added to **your Google Calendar**.
4. 🧘 Follow the plan during the day.
5. ✍️ At night, go to “**How Was Your Day?**” and give feedback.

> Your feedback helps the AI improve your plan every day!

---

## ❓ Ask Your Coach

Use the **AI Coach page** to:
- Get **health advice** tailored to you.
- Ask for **alternative workouts** or motivation.
- Get **diet or recovery suggestions**.

💡 The coach is trained on quality fitness knowledge and personalized through your feedback.

---

## 📊 Dashboard Highlights

- **Today's Plan** – What’s scheduled for today.
- **Progress Tracker** – Weekly performance summary.
- **Motivation** – A new quote or insight every day.
- **Activity Feed** – Log of your past and planned activities.

---

## 🔐 Privacy & Data Safety

- Your data is securely stored and only used to improve your plan.
- Google login is OAuth2 secured.
- No data is shared with third parties.

---

## 💡 Tips for Best Experience

- Complete your feedback **daily** to help personalize future plans.
- Keep your goals updated in the **Settings** page.
- Enable **Google Calendar sync** to stay organized.
- Come back regularly to ask your coach questions!

---

## 🧘 Stay Consistent, Stay Healthy!

Let your AI coach guide you — one step at a time 💪

"""

st.markdown(user_manual_text)
