from langchain_openai import ChatOpenAI
from langchain_core.prompts import (ChatPromptTemplate, 
                                    HumanMessagePromptTemplate, 
                                    SystemMessagePromptTemplate,
                                    FewShotChatMessagePromptTemplate,
                                    AIMessagePromptTemplate)
from backend.config import settings
from backend import schemas
import json

## hasing and varifying passwords ---------------------------------------------------
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def hash(raw_password:str):
    """Hash a raw password"""
    return pwd_context.hash(raw_password)

def verify(raw_password: str, hashed_password:str):
    """Verify if the entered raw password mathes the hashed password"""
    return pwd_context.verify(secret= raw_password, hash = hashed_password)


## llm agent ---------------------------------------------------------------------------
llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.8,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key= settings.OPENAI_API_KEY  # if you prefer to pass api key in directly instaed of using env vars
        # base_url="...",
        # organization="...",
        # other params...
    )

## system promt and query ---------------------------------------------------------------
system_prompt = """
You are a smart fitness and lifestyle planning assistant. Your job is to create a personalized, realistic, and motivating full-day plan for a user based on their preferences.

You will be given a prompt that contains the user's fitness goal, lifestyle type, preferred timings (in order of preference), and an optional note. This prompt will always be structured like a natural language query, labeled under the variable `query`.

Your job is to generate a **valid JSON-serializable dictionary** that includes exactly the following six keys:
- task1_title
- task1_content
- task2_title
- task2_content
- task3_title
- task3_content

**Formatting rules:**
- Each title should be concise and to the point (no more than ~5 words).
- Each content field must be between **50 to 75 words** in plain, clear English.
- Do **not** include markdown, bullet points, special formatting, or line breaks — only plain text within a clean JSON object.
- Ensure that your output can be parsed using Python’s `json.loads()` without any errors.

Think like a practical, encouraging coach who tailors fitness to real-life routines — focus on motivating and adaptable activities that suit the user’s stated preferences and constraints.
"""

query = """
Based on the following preferences, create a full-day plan broken into 3 tasks. Each task should include a short title and a description. Format the result as a JSON object with task1_title, task1_content, task2_title, task2_content, task3_title, and task3_content.

User Preferences:
- Goal: {goal}
- Lifestyle: {lifestyle}
- Preferred Timings (in order of preference): {preferred_timings}
- Note: {note}
"""

## few shot prompting ---------------------------------------------------------------------------------
examples = [
    {
        "input": """
Based on the following preferences, create a full-day plan broken into 3 tasks. Each task should include a short title and a description. Format the result as a JSON object with task1_title, task1_content, task2_title, task2_content, task3_title, and task3_content.

User Preferences:
- Goal: Stay active at home
- Lifestyle: Sedentary
- Preferred Timings (in order of preference): Morning, Afternoon, Evening
- Note: Avoid high-impact exercises
""",
        "output": """
{
    "task1_title": "Morning Stretch Routine",
    "task1_content": "Start your day with a gentle stretching routine to wake up your muscles and joints. Spend about 10 minutes focusing on full-body stretches, including neck rolls, shoulder circles, and hamstring stretches. This will help improve flexibility and prepare your body for the day ahead.",
    "task2_title": "Afternoon Chair Workout",
    "task2_content": "Use a sturdy chair for low-impact strength training. Perform seated leg lifts, chair squats, and light arm exercises using water bottles or resistance bands. Keep the session around 20–30 minutes.",
    "task3_title": "Evening Relaxation Walk",
    "task3_content": "Wrap up your day with a calming 20-minute indoor or outdoor walk. Keep a relaxed pace to promote circulation and help you unwind before bedtime."
}
"""
    },
    {
        "input": """
Based on the following preferences, create a full-day plan broken into 3 tasks. Each task should include a short title and a description. Format the result as a JSON object with task1_title, task1_content, task2_title, task2_content, task3_title, and task3_content.

User Preferences:
- Goal: Build muscle
- Lifestyle: Gym access
- Preferred Timings (in order of preference): Afternoon, Evening, Morning
- Note: Prior experience with weightlifting
""",
        "output": """
{
    "task1_title": "Afternoon Strength Training",
    "task1_content": "Focus on compound lifts like squats, deadlifts, bench presses, and pull-ups. Perform 4 sets of 6–8 reps per exercise. Rest 60–90 seconds between sets.",
    "task2_title": "Evening Core & Mobility",
    "task2_content": "Target your core with planks, hanging leg raises, and Russian twists. Follow up with 15 minutes of mobility drills including hip openers and thoracic rotations.",
    "task3_title": "Morning Light Cardio",
    "task3_content": "Start your day with a 20-minute walk or bike ride to stimulate blood flow and aid in muscle recovery from the previous day."
}
"""
    }
]

example_prompt = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template("{input}"),
    AIMessagePromptTemplate.from_template("{output}")
])

few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt= example_prompt,
    examples= examples
)

plans_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_prompt),
    few_shot_prompt,
    HumanMessagePromptTemplate.from_template(query)
])

## calls the openai api to get the preferences of the current user -------------------------------------------
def get_todays_plan(preferences: schemas.Preferences):
    
    preferences_dict = {
        "goal": preferences.goal,
        "lifestyle": preferences.lifestyle,
        "preferred_timings": preferences.preferred_timings,
        "note": preferences.note,
    }
    # print(f"My Preferences: {preferences_dict}")
    
    pipeline = (
        {
            "goal": lambda x: x["goal"],
            "lifestyle": lambda x: x["lifestyle"],
            "preferred_timings": lambda x: x["preferred_timings"],
            "note": lambda x: x["note"]
        }
        | plans_prompt 
        | llm
        )
    ai_message = pipeline.invoke(preferences_dict)
    # print("Raw LLM response:", ai_message.content)
    return json.loads(ai_message.content)