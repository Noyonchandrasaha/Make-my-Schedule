from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
import os

async def create_schedule_agent(tools):
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-8b-8192"
    )

    prompt = (
        "You are an AI assistant for Google Calendar management. "
        "You can create, list, update, and delete calendar events by title. "
        "Always check for conflicting events before scheduling or updating. "
        "When you need to operate on calendar, use the tools accordingly. "
        "Format your responses clearly for the user."
    )

    return create_react_agent(
        model=llm,
        tools=tools,
        prompt=prompt
    )
