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

Your job is to generate a **valid JSON-serializable dictionary** that includes exactly the following 12 keys:
- task1_title
- task1_content (a dict with step_1, step_2, step_3)
- task1_timings
- task1_tip
- task2_title
- task2_content (a dict with step_1, step_2, step_3)
- task2_timings
- task2_tip
- task3_title
- task3_content (a dict with step_1, step_2, step_3)
- task3_timings
- task3_tip

**Formatting rules:**
- Each title should be concise and to the point (no more than ~5 words).
- Each step inside content should be a short instruction (~1–2 sentences).
- Timings should follow the format "HH:MM AM/PM - HH:MM AM/PM".
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
    "task1_timings": "07:00 AM - 07:30 AM",
    "task1_tip": "Play calming instrumental music to enhance relaxation during stretches.",

    "task2_title": "Afternoon Chair Workout",
    "task2_content": json.dumps({
        "step_1": "Perform seated leg lifts and ankle rotations for 10 minutes.",
        "step_2": "Do 2 sets of 10 chair squats and light arm curls with water bottles.",
        "step_3": "Cool down with shoulder rolls and relaxed breathing."
    }),
    "task2_timings": "01:00 PM - 01:30 PM",
    "task2_tip": "Watch your favorite show while working out to stay motivated.",

    "task3_title": "Evening Relaxation Walk",
    "task3_content": json.dumps({
        "step_1": "Begin with a gentle 5-minute warm-up walk around your home.",
        "step_2": "Walk at a relaxed pace for 15 minutes while maintaining good posture.",
        "step_3": "End with standing stretches for your legs and lower back."
    }),
    "task3_timings": "06:30 PM - 07:00 PM",
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
    "task1_timings": "12:30 PM - 01:30 PM",
    "task1_tip": "Use a workout playlist with high-energy music to push through heavy sets.",

    "task2_title": "Evening Core & Mobility",
    "task2_content": json.dumps({
        "step_1": "Do 3 rounds of planks, hanging leg raises, and Russian twists.",
        "step_2": "Spend 15 minutes on hip openers, spinal twists, and shoulder mobility.",
        "step_3": "Finish with breathing exercises and light stretching."
    }),
    "task2_timings": "06:00 PM - 06:45 PM",
    "task2_tip": "Light candles or use a diffuser for a spa-like atmosphere during stretches.",

    "task3_title": "Morning Light Cardio",
    "task3_content": json.dumps({
        "step_1": "Start with a brisk walk or cycling for 10 minutes.",
        "step_2": "Maintain moderate pace for another 10 minutes.",
        "step_3": "Cool down with easy pace and full-body stretches."
    }),
    "task3_timings": "07:30 AM - 08:00 AM",
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
You are a smart fitness and lifestyle planning assistant. 
Your job is to provide helpful, engaging, and personalized responses to user queries about health, fitness, nutrition and lifestyle planning.
Keep your response concise and to the point always.

Extra information (optional):
{user_plans}
"""
# chat prompt template
chat_prompt_chatbot = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_prompt_chatbot),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template("{user_query}"),
])

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
                break  # End of stream
            yield token  # Yield the token for downstream use (e.g., FastAPI StreamingResponse)

handler = TokenStreamHandler()

async def get_chatbot_response(user_query: str, user_id:str, user_plans: str = None ):
    """Generates a response from the AI chatbot based on user input."""
    
    # ai_message = pipeline_with_history.invoke(
    #     {"user_plans": user_plans, "user_query": user_query}, 
    #     config = {"session_id": user_id}
    #     )
    
    async for chunk in pipeline_with_history.astream(
        {"user_plans": user_plans, "user_query": user_query}, 
        config = {"session_id": user_id}
    ):
        yield chunk.content
    
    # return ai_message.content