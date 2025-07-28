# 🤖 FitCoach Platform

A personalized AI-powered health companion to help users set goals, track progress, and stay accountable — featuring a conversational assistant and optional Google Calendar integration.

---

## 🚀 Features

- 📝 **Sign Up & Personalize** your health preferences
- 📅 **Daily plans** tailored to your fitness goals
- ✅ **Daily feedback** to fine-tune task recommendations
- 🤖 **Chat with your AI coach** (uses OpenAI API)
- 📊 **Track progress** in an interactive dashboard
- 📆 **Optional Google Calendar sync** for your daily plan

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI + Langchain
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy + Alembic
- **AI**: OpenAI API
- **Auth & Sync**: JWT + Google OAuth
- **Environment Configuration**: Python `dotenv`

---


## 🔧 Getting Started (Local Setup)

### 1. **Clone the Repository**

```bash
git clone https://github.com/AdarshPotanpalli/fitcoach-platform.git
cd fitcoach-platform
````

### 2. **Create and Configure Environment File**

```bash
cp .env.example .env
```

Edit `.env` with your values:

* `OPENAI_API_KEY` (required)

---

### 3. **Install Python Dependencies**

We recommend using a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 4. **Start the Backend Server**

```bash
uvicorn backend.fastapi_app:app --reload
```

API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 5. **Start the Frontend App**

```bash
python -m streamlit run frontend/streamlit_app.py
```

Streamlit UI: [http://localhost:8501](http://localhost:8501)

---

## 📘 App Usage Guide

1. **Create an account** and set your health goals
2. Get **daily personalized tasks**
3. Complete tasks and provide **feedback**
4. Ask your **AI coach** for help anytime
5. Track everything from your **dashboard**

---

### 🔒 Google Calendar Integration (Optional)

> ⚠️ **Note:** The Google Calendar sync features will **not work** in this local setup because the required `google_client_secret.json` file is **not included** in the repository for security reasons.
> These credentials are tied to the developer's Google Cloud project and cannot be shared publicly.
>
> All other features of the app remain fully functional.

---

>**Author:** Adarsh Potanpalli 
>
>**Email:** p.adarsh.24072001@gmail.com 

---

