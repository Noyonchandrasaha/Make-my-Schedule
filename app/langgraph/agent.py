import os
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_core.tools import StructuredTool

from app.langgraph.tools.create_event_tool import create_event_tool_func

# Wrap your function in StructuredTool directly
create_event_tool_structured = StructuredTool.from_function(
    func=create_event_tool_func,
    name="create_event",
    description="Create a Google Calendar event with optional title, time, location, and reminders.",
)

async def create_schedule_agent():
    # Initialize the LLM
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-70b-8192"
    )

    # Define prompt
    prompt = (
        "You are a helpful AI assistant for managing Google Calendar. "
        "You can create, update, delete, and list calendar events. "
        "Use the create_event tool to create events with validation and conflict checking. "
        "If any field like title, time, location is missing, generate intelligently. "
        "Always respond clearly and helpfully."
    )

    # Build agent
    agent = create_react_agent(
        model=llm,
        tools=[create_event_tool_structured],  # Only create_event tool
        prompt=prompt
    )

    return agent
