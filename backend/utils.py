from langchain_openai import ChatOpenAI
from langchain_core.prompts import (ChatPromptTemplate, 
                                    HumanMessagePromptTemplate, 
                                    SystemMessagePromptTemplate,
                                    MessagesPlaceholder,
                                    FewShotChatMessagePromptTemplate,
                                    AIMessagePromptTemplate)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.schema import LLMResult
from backend.config import settings
from backend import schemas
import json
import asyncio
from datetime import date
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

## hasing and varifying passwords ---------------------------------------------------
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def hash(raw_password:str):
    """Hash a raw password"""
    return pwd_context.hash(raw_password)

def verify(raw_password: str, hashed_password:str):
    """Verify if the entered raw password mathes the hashed password"""
    return pwd_context.verify(secret= raw_password, hash = hashed_password)

## encrypting and decrypting the google credentials -----------------------------------
load_dotenv()
fernet = Fernet(os.getenv("GOOGLE_CREDENTIALS_ENCRYPTION_KEY").encode())

def encrypt_credentials(credentials: str) -> str:
    return fernet.encrypt(credentials.encode()).decode()

def decrypt_credentials(encrypted: str) -> dict:
    decrypted_bytes = fernet.decrypt(encrypted.encode())
    return json.loads(decrypted_bytes.decode())


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

The user may provide tasks they failed to complete recently. The user has struggled with these tasks recently. Consider adjusting their intensity or frequency.

The user may provide tasks they completed successfully. These tasks aligned well with the user's habits, preferences, or motivation. Use them as inspiration for related or slightly more challenging tasks.

Your job is to generate a **valid JSON-serializable dictionary** that includes exactly the following 12 keys:
- task1_title
- task1_content (a dict with step_1, step_2, step_3)
- task1_timings_start (in the format "HH:MM:SS")
- task1_timings_end (in the format "HH:MM:SS")
- task1_tip
- task2_title
- task2_content (a dict with step_1, step_2, step_3)
- task2_timings_start (in the format "HH:MM:SS")
- task2_timings_end (in the format "HH:MM:SS")
- task2_tip
- task3_title
- task3_content (a dict with step_1, step_2, step_3)
- task3_timings_start (in the format "HH:MM:SS")
- task3_timings_end (in the format "HH:MM:SS")
- task3_tip

**Formatting rules:**
- Each title should be concise and to the point (no more than ~5 words).
- Each step inside content should be a short instruction (~1–2 sentences).
- Timings should follow the format "HH:MM:SS".
- Tips should be engaging, motivational, and offer useful suggestions to make the task more enjoyable or sustainable.
- Ensure that your output can be parsed using Python’s `json.loads()` without any errors.
- Only return the JSON object — no explanations, comments, or extra text.

Think like a practical, encouraging coach who tailors fitness to real-life routines — focus on motivating and adaptable activities that suit the user’s stated preferences and constraints.
"""

query = """
Based on the following preferences, create a full-day plan broken into 3 tasks. Each task should include a short title, a content dictionary with 3 steps, a time window, and an interesting motivational tip. Format the result as a JSON object with task1_title, task1_content, task1_timings, task1_tip, task2_title, task2_content, task2_timings, task2_tip, task3_title, task3_content, task3_timings, and task3_tip.

User Preferences:
- Goal: {goal}
- Lifestyle: {lifestyle}
- Preferred Timings (in order of preference): {preferred_timings}
- Note: {note}
- Tasks the user failed to complete recently: {list_of_task_failures}
- Tasks the user completed successfully: {list_of_task_successes}
"""


## few shot prompting ---------------------------------------------------------------------------------
examples = [
    {
        "input": """
Based on the following preferences, create a full-day plan broken into 3 tasks. Each task should include a short title, a description broken into 3 steps, a time slot, and an engaging tip to make the workout more interesting. Format the result as a JSON object with task1_title, task1_content, task1_timings, task1_tip, task2_title, task2_content, task2_timings, task2_tip, task3_title, task3_content, task3_timings, and task3_tip. Each content field should be a dictionary with keys step_1, step_2, and step_3.

User Preferences:
- Goal: Stay active at home
- Lifestyle: Sedentary
- Preferred Timings (in order of preference): Morning, Afternoon, Evening
- Note: Avoid high-impact exercises
""",
        "output": json.dumps(
{
    "task1_title": "Morning Stretch Routine",
    "task1_content": json.dumps({
        "step_1": "Start with neck rolls and shoulder circles to loosen up the upper body.",
        "step_2": "Do 5–10 minutes of gentle hamstring and back stretches.",
        "step_3": "Finish with deep breathing and light mobility drills to energize."
    }),
    "task1_timings_start": "07:00:00",
    "task1_timings_end": "07:30:00",
    "task1_tip": "Play calming instrumental music to enhance relaxation during stretches.",

    "task2_title": "Afternoon Chair Workout",
    "task2_content": json.dumps({
        "step_1": "Perform seated leg lifts and ankle rotations for 10 minutes.",
        "step_2": "Do 2 sets of 10 chair squats and light arm curls with water bottles.",
        "step_3": "Cool down with shoulder rolls and relaxed breathing."
    }),
    "task2_timings_start": "01:00:00",
    "task2_timings_end": "01:30:00",
    "task2_tip": "Watch your favorite show while working out to stay motivated.",

    "task3_title": "Evening Relaxation Walk",
    "task3_content": json.dumps({
        "step_1": "Begin with a gentle 5-minute warm-up walk around your home.",
        "step_2": "Walk at a relaxed pace for 15 minutes while maintaining good posture.",
        "step_3": "End with standing stretches for your legs and lower back."
    }),
    "task3_timings_start": "06:30:00",
    "task3_timings_end": "07:00:00",
    "task3_tip": "Listen to an audiobook or podcast to make the walk more enjoyable."
})

    },
    {
        "input": """
Based on the following preferences, create a full-day plan broken into 3 tasks. Each task should include a short title, a description broken into 3 steps, a time slot, and an engaging tip to make the workout more interesting. Format the result as a JSON object with task1_title, task1_content, task1_timings, task1_tip, task2_title, task2_content, task2_timings, task2_tip, task3_title, task3_content, task3_timings, and task3_tip. Each content field should be a dictionary with keys step_1, step_2, and step_3.

User Preferences:
- Goal: Build muscle
- Lifestyle: Gym access
- Preferred Timings (in order of preference): Afternoon, Evening, Morning
- Note: Prior experience with weightlifting
""",
        "output": json.dumps(
{
    "task1_title": "Afternoon Strength Training",
    "task1_content": json.dumps({
        "step_1": "Begin with a 10-minute warm-up using treadmill or dynamic stretches.",
        "step_2": "Perform 4 sets of compound lifts: squats, deadlifts, bench presses.",
        "step_3": "Cool down with light cardio and foam rolling."
    }),
    "task1_timings_start": "12:30:00",
    "task1_timings_end": "13:30:00",
    "task1_tip": "Use a workout playlist with high-energy music to push through heavy sets.",

    "task2_title": "Evening Core & Mobility",
    "task2_content": json.dumps({
        "step_1": "Do 3 rounds of planks, hanging leg raises, and Russian twists.",
        "step_2": "Spend 15 minutes on hip openers, spinal twists, and shoulder mobility.",
        "step_3": "Finish with breathing exercises and light stretching."
    }),
    "task2_timings_start": "18:00:00",
    "task2_timings_end": "18:45:00",
    "task2_tip": "Light candles or use a diffuser for a spa-like atmosphere during stretches.",

    "task3_title": "Morning Light Cardio",
    "task3_content": json.dumps({
        "step_1": "Start with a brisk walk or cycling for 10 minutes.",
        "step_2": "Maintain moderate pace for another 10 minutes.",
        "step_3": "Cool down with easy pace and full-body stretches."
    }),
    "task3_timings_start": "07:00:00",
    "task3_timings_end": "08:00:00",
    "task3_tip": "Take your cardio session outdoors for fresh air and natural light."
})

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
def get_todays_plan(preferences: schemas.Preferences, list_of_task_failures = [], list_of_task_successes = []):
    
    preferences_dict = {
        "goal": preferences.goal,
        "lifestyle": preferences.lifestyle,
        "preferred_timings": preferences.preferred_timings,
        "note": preferences.note,
        "list_of_task_failures": ", ".join(list_of_task_failures),
        "list_of_task_successes": ", ".join(list_of_task_successes)
    }
    # print(f"My Preferences: {preferences_dict}")
    
    pipeline = (
        {
            "goal": lambda x: x["goal"],
            "lifestyle": lambda x: x["lifestyle"],
            "preferred_timings": lambda x: x["preferred_timings"],
            "note": lambda x: x["note"],
            "list_of_task_failures": lambda x: x["list_of_task_failures"],
            "list_of_task_successes": lambda x: x["list_of_task_successes"]
        }
        | plans_prompt 
        | llm
        )
    ai_message = pipeline.invoke(preferences_dict)
    # print("Raw LLM response:", ai_message.content)
    return json.loads(ai_message.content)


## -------------------------------------------------------------------- LLM agent for chat bot --------------------------

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

# System prompt
system_prompt_chatbot = """
- You are a smart fitness and lifestyle planning assistant. 
- Your job is to provide responses to user queries about health, fitness, nutrition and lifestyle planning.
- Respond with engaging, well-structured markdown using appropriate emojis, headings, bold text, and bullet points(when appropriate) to make the content visually appealing and reader-friendly.
- Keep your response concise and to the point always.

Goal of the user:
{goal}

User plans (if the user asks any questions related to their plans,use the following information to answer):
- Task 1: {user_task1}
- Task 2: {user_task2}
- Task 3: {user_task3}
"""
user_query_chatbot = """
{user_query}

"""

# chat prompt template
chat_prompt_chatbot = ChatPromptTemplate(
    [SystemMessagePromptTemplate.from_template(system_prompt_chatbot),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template(user_query_chatbot),],
    input_variables=["user_task1", "user_task2", "user_task3", "user_query", "goal"],
    )

# define get chat history
chat_map = {}
def get_chat_history(user_id: str):
    """Retrieves the chat history for a given user."""
    if user_id not in chat_map:
        chat_map[user_id] = InMemoryChatMessageHistory()
    return chat_map[user_id]

# pipeline wrapped with runnables with message history
pipeline_chatbot = chat_prompt_chatbot | llm
pipeline_with_history = RunnableWithMessageHistory(
    pipeline_chatbot,
    get_session_history= get_chat_history,
    input_messages_key="user_query",
    history_messages_key="chat_history"
)

## custom callback handler
class TokenStreamHandler(AsyncCallbackHandler):
    def __init__(self):
        # Initialize an asyncio queue to hold the streamed tokens
        self.queue = asyncio.Queue()

    async def on_llm_new_token(self, token: str, **kwargs):
        # This callback is triggered every time the LLM emits a new token
        # Add the token to the queue for streaming
        await self.queue.put(token)

    async def on_llm_end(self, response: LLMResult, **kwargs):
        # This callback is triggered when the LLM finishes generating a response
        # Put a sentinel value (None) in the queue to indicate the end of stream
        await self.queue.put(None)

    async def __aiter__(self):
        # Asynchronous generator to yield tokens one by one from the queue
        while True:
            token = await self.queue.get()  # Wait for next token
            if token is None:
                return  # End of stream
            yield token  # Yield the token for downstream use (e.g., FastAPI StreamingResponse)
            await asyncio.sleep(0.01) # add tiny delay to have a streaming behaviour

handler = TokenStreamHandler()    
async def get_chatbot_response(user_query: str, 
                               user_id:str, 
                               user_task1: str = None,
                               user_task2: str = None, 
                               user_task3: str = None,
                               goal: str = None):
    """Generates a response from the AI chatbot based on user input."""
    
    async for chunk in pipeline_with_history.astream(
        {"user_task1": user_task1, "user_task2": user_task2, "user_task3": user_task3, 
         "user_query": user_query, "goal": goal}, 
        config = {"session_id": user_id, "callbacks": [handler]}
    ):
        yield chunk.content
        
def create_calendar_events(user_plans: schemas.Plans, service):
    
    """Creates calendar events based on the user's plans."""
    
    # creating events from user's plans -------------------------------->
    todays_date = date.today().isoformat()  # Get today's date in ISO format
    task1_content = ""
    task2_content = "" 
    task3_content = ""
    task1_content_dict = json.loads(user_plans.task1_content)
    for i, (step, task) in enumerate(task1_content_dict.items()):
        task1_content += f"Step {i+1}:   {task}\n\n"
    task2_content_dict = json.loads(user_plans.task2_content)
    for step, task in task2_content_dict.items():
        task2_content += f"Step {i+1}:   {task}\n\n"
    task3_content_dict = json.loads(user_plans.task3_content)
    for step, task in task3_content_dict.items():
        task3_content += f"Step {i+1}:   {task}\n\n"
    event1 = {
        'summary': user_plans.task1_title,
        'description': task1_content,
        'start': {
            'dateTime': todays_date + 'T' + user_plans.task1_timings_start,
            'timeZone': 'Europe/Berlin',
        },
        'end': {
            'dateTime': todays_date + 'T' + user_plans.task1_timings_end,
            'timeZone': 'Europe/Berlin',
        },
    }
    event2 = {
        'summary': user_plans.task2_title,
        'description': task2_content,
        'start': {
            'dateTime': todays_date + 'T' + user_plans.task2_timings_start,
            'timeZone': 'Europe/Berlin',
        },
        'end': {
            'dateTime': todays_date + 'T' + user_plans.task2_timings_end,
            'timeZone': 'Europe/Berlin',
        },
    }
    event3 = {
        'summary': user_plans.task3_title,
        'description': task3_content,
        'start': {
            'dateTime': todays_date + 'T' + user_plans.task3_timings_start,
            'timeZone': 'Europe/Berlin',
        },
        'end': {
            'dateTime': todays_date + 'T' + user_plans.task3_timings_end,
            'timeZone': 'Europe/Berlin',
        },
    }
    # -------------------------------------------------------------------------------
    created_event_ids = []
    
    created_event1 = service.events().insert(calendarId='primary', body=event1).execute()
    created_event_ids.append(created_event1['id'])
    created_event2 = service.events().insert(calendarId='primary', body=event2).execute()
    created_event_ids.append(created_event2['id'])
    created_event3 = service.events().insert(calendarId='primary', body=event3).execute()
    created_event_ids.append(created_event3['id'])
    
    return created_event_ids